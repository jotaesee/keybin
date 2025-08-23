import secrets, string, json, os, keyring, time, typer
from .exceptions import *
from thefuzz import fuzz
from passlib.context import CryptContext
from keybin.models import passwordLog, ProfileModel, ConfigDataModel, LogsFileModel
from datetime import datetime, timezone
from pathlib import Path
from platformdirs import user_data_dir, user_config_path
from functools import wraps


CONFIG_PATH = user_config_path("configs", "keybin")
DEFAULT_STORAGE_PATH = user_data_dir("data", "keybin")
SESSION_TIME = 900 ## 15 minutos x ahi
passContext = CryptContext(schemes=["bcrypt"], deprecated = "auto")


def eraseToken():
    config : ConfigDataModel = getConfig()
    user = config.active_profile
    config.active_profile = ""
    saveConfig(config)
    try:
        keyring.delete_password("keybin_session", f"{user}")
        return True
    except keyring.errors.PasswordDeleteError:
        return False

def createToken(user : string , key : str):
    
    config = getConfig()
    profileKey = config.profiles[user].masterkey
    
    if config.active_profile:
        raise SessionAlreadyExistsError("ERROR: There's an active session")
    
    if user not in config.profiles: 
        raise UserNotFoundError("ERROR: Profile does not exist")

    if profileKey != '' :  
        if not key :
            raise PasswordNeededError("ERROR: Masterkey required for this profile")
        if not checkPass(key, profileKey):
            raise InvalidPasswordError("ERROR: Invalid password")
    

    timestamp = int(time.time())
    sessionToken = f"{key}:{timestamp}"
    config.active_profile = user
    keyring.set_password("keybin_session", f"{user}", f"{sessionToken}")
    saveConfig(config)


def tokenCheck():
    
    config = getConfig()
    user = config.active_profile
    session_data = keyring.get_password("keybin_session", f"{user}")
    
    if not session_data or not user:
        eraseToken()
        raise NoSessionActiveError("ERROR: Invalid or no session, try login in again.")
    
    try:
        key, login_timestamp = session_data.split(":")
        login_timestamp = int(login_timestamp)
    except (ValueError, TypeError):
        keyring.delete_password("keybin_session", f"{user}")
        eraseToken()
        raise CorruptedSessionError("ERROR: Session's corrrupted, please login again")

    if time.time() - login_timestamp > SESSION_TIME: ## chequeo si no murió ya la sesion
        keyring.delete_password("keybin_session", f"{user}")
        eraseToken()
        raise SessionExpiredError("ERROR: Session's expired")
    
    return 0

def getConfig():
    if not CONFIG_PATH.exists():
        createConfig()
        
    with open(CONFIG_PATH, mode="r", encoding="utf-8") as read_file:
        config = json.load(read_file)
        return ConfigDataModel.model_validate(config) ## esto es para convertir de json al model
    
    
def createConfig():
    
    defaultConfig = {
        "active_profile" : "",
        "profiles" : {
            "default" : {
                "data_path" : str(Path(DEFAULT_STORAGE_PATH).joinpath("default")),
                "password" : ""
            }
        }
    }
    Path(CONFIG_PATH).parent.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_PATH, mode="w", encoding="utf-8") as new_file:
        json.dump(defaultConfig, new_file, indent=4)

def startProfile(user : str, key : str, datapath : str | None = None):
    
    if datapath == None : datapath = str(Path(DEFAULT_STORAGE_PATH).joinpath(user)) 
    
    profile = ProfileModel(
        masterkey = passContext.hash(key) if key else "",
        data_path = datapath
    )
    config : ConfigDataModel = getConfig()
    config.profiles[user] = profile
    saveConfig(config)

def saveConfig(config : ConfigDataModel):
    
    with open(CONFIG_PATH, mode="w", encoding="utf-8") as new_file:
        json.dump(config.model_dump(), new_file, indent=4) ## esto es del model al json

def eraseProfileData(config : ConfigDataModel, profile : str):
    profileLogData= Path(config.profiles[profile].data_path)
    if profileLogData.exists():
        os.remove(profileLogData)
    del config.profiles[profile]
    saveConfig(config)

def getActivePath():
    config : ConfigDataModel = getConfig()
    userprofile : ProfileModel = config.profiles[config.active_profile]
    path = Path(userprofile.data_path)
    return path

def checkPass(keyToHash : string, keyHashed : string):
    if not keyHashed : return True
    if not keyToHash : return False ## si hay key en el perfil y no llega hasta aqui, rip
    return passContext.verify(keyToHash, keyHashed)

def getLogFile():
    path = getActivePath()
    
    if not path.exists():
        createLogFile(path)
    
    with open(path, mode="r", encoding="utf-8") as read_file:
        data = json.load(read_file)
        return LogsFileModel.model_validate(data)
    
    
def createLogFile(path : Path):
    defaultFile = {"currentLogId" : 0, "logs": {}}
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as new_file:
        json.dump(defaultFile, new_file, indent=4)

def saveLogFile(logFile : LogsFileModel):
    path = getActivePath()
    with open(path, "w", encoding="utf-8") as new_file:
        json.dump(logFile.model_dump(), new_file, indent=4)

def newLog(
    service : str | None = None, 
    user : str | None = None,
    email : str | None = None,
    password : str | None = None,
    tags : list[str] | None = None):
    
    logFile : LogsFileModel = getLogFile()
    newLogID = logFile.currentLogId + 1 
    log = passwordLog(logID = newLogID, service=service, user=user, email=email, password=password, tags=tags, createdAt=datetime.now(timezone.utc).isoformat())
    logFile.currentLogId = newLogID
    logFile.logs[newLogID] = log
    saveLogFile(logFile)
    
def deleteLog(id : int, noPrompt : bool) :
    logFile = getLogFile()
    if not logFile.logs.get(id) :
        raise NoLogFoundError("ERROR: No log with this ID.")
    
    logFile.logs.pop(id)
    saveLogFile(logFile)    
        
        
def newSecureString(symbols : bool = True, length : int = 16):
    
    chars = string.ascii_letters + string.digits
    if symbols : chars += string.punctuation
    newpass = "".join(secrets.choice(chars) for _ in range(length))
    return newpass 
        
def doSearch(search : str | None = None , service : str | None = None ,username : str | None = None, tags : list[str] | None = None, id : int | None = None):
    
    profileLogFile : LogsFileModel = getLogFile()
    logs_list: list[passwordLog] = profileLogFile.logs.values()  # lista ya con instancias
    filtered_results : list [passwordLog]= []

    if search == "all": 
        return logs_list
    
    if search : return _fuzzySearch(search) ## la busqueda no especifica en que campo busca, asi que tenemos que mandarla a fuzzy search y que se encargue ahi
    
    for log in logs_list:
        passes = True

        if id and log.logID != id :
            passes = False

        if service and log.service != service:
            passes = False

        if username and log.user != username:
            passes = False

        if tags:
            if not log.tags or not all(tag in log.tags for tag in tags):
                passes = False

        if passes:
            filtered_results.append(log)

    if filtered_results == [] :
        raise NoLogFoundError("No results for this search")
    
    return filtered_results


def _fuzzySearch(search : str):
    SCORE_THRESHOLD = 75

    profileLogFile: LogsFileModel = getLogFile()
    all_logs: list[passwordLog] = list(profileLogFile.logs.values())
    scored_results = []
    search_lower = search.lower()

    for log in all_logs: ## buscar en todos los campos pq no sabemos q busca

        service = log.service.lower() if log.service else ""
        user = log.user.lower() if log.user else ""
        email = log.email.lower() if log.email else ""
        tags = log.tags if log.tags else ""
        
        score_service = fuzz.partial_ratio(search_lower, service)
        score_user = fuzz.partial_ratio(search_lower, user)
        score_email = fuzz.partial_ratio(search_lower, email)
        
        score_tags = 0
        for tag in tags:
            newScore = fuzz.partial_ratio(search_lower, tag)
            if newScore > score_tags : score_tags = newScore
        
        max_score = max(score_service, score_user, score_email, score_tags, score_tags)
        
        if max_score >= SCORE_THRESHOLD: ## puntaje pasa el threshold, tonces lo agregamos a los resultados con su puntaje
            scored_results.append((log, max_score))


## hay q ordenar y filtrar
    scored_results.sort(key=lambda item: item[1], reverse=True)
    final_results = [log for log, score in scored_results]
    
    return final_results



def require_active_session(func):
    """
    Checks token for secured commands.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            tokenCheck() 
            return func(*args, **kwargs)

        except (NoSessionActiveError, SessionExpiredError, CorruptedSessionError) as e:
            typer.secho(str(e), fg="red")
            return
        except Exception as e:
            typer.secho(f"Unexpected error: {e}", fg="red")
            return

    return wrapper