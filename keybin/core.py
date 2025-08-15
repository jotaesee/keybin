import secrets, string, json, os, difflib
from passlib.context import CryptContext
from keybin.models import passwordLog, ProfileModel, ConfigDataModel, LogsFileModel
from datetime import datetime, timezone
from pathlib import Path
from platformdirs import user_data_dir, user_config_path

CONFIG_PATH = user_config_path("configs", "keybin")
DEFAULT_STORAGE_PATH = user_data_dir("data", "keybin")

passContext = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def getConfig():
    if not CONFIG_PATH.exists():
        createConfig()
        
    with open(CONFIG_PATH, mode="r", encoding="utf-8") as read_file:
        config = json.load(read_file)
        return ConfigDataModel.model_validate(config) ## esto es para convertir de json al model
    
    
def createConfig():
    
    defaultConfig = {
        "active_profile" : "default",
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
    if logFile : print(logFile)
    newLogID = logFile.currentLogId + 1 
    log = passwordLog(logID = newLogID, service=service, user=user, email=email, password=password, tags=tags, createdAt=datetime.now(timezone.utc).isoformat())
    logFile.currentLogId = newLogID
    logFile.logs[newLogID] = log
    saveLogFile(logFile)
    

def newSecureString(symbols : bool = True, length : int = 16):
    
    chars = string.ascii_letters + string.digits
    if symbols : chars += string.punctuation
    newpass = "".join(secrets.choice(chars) for _ in range(length))
    return newpass 
        
def doSearch(search : str | None = None , service : str | None = None ,username : str | None = None, tags : list[str] | None = None):
    
    profileLogFile : LogsFileModel = getLogFile()
    logs_list: list[passwordLog] = profileLogFile.logs.values()  # lista ya con instancias
    filtered_results : list [passwordLog]= []

    if search == "all": return logs_list
    
    if search : return _fuzzySearch(search) ## la busqueda no especifica en que campo busca, asi que tenemos que mandarla a fuzzy search y que se encargue ahi
    
    for log in logs_list:
        passes = True

        if service and log.service != service:
            passes = False

        if username and log.user != username:
            passes = False

        if tags:
            if not log.tags or not any(tag in log.tags for tag in tags):
                passes = False

        if passes:
            filtered_results.append(log)

    return filtered_results


def _fuzzySearch(search : str):
    
    return [passwordLog( user="juse", password="contraseñaxd",tags = None, createdAt=None)]