import typer, pyperclip, time
from keybin.commands.profile import profile_app
from keybin.commands.log import log_app
from keybin.core import newSecureString, getConfig, getLogFile, createToken, eraseToken, tokenCheck
from .exceptions import *

app = typer.Typer()
app.add_typer(profile_app, name="profile")
app.add_typer(log_app, name ="log")

@app.command("gp")
@app.command("genpass")
def genpass(
    copy : bool = typer.Option(False,"--copy", "-c", help="If true, copies the new password to the clipboard"),
    symbols: bool = typer.Option(True, help="If true, include symbols in the generated password."),
    length : int = typer.Option(16, "--length", "-l", help="Desired length for new password")
    ):    
                
    newpass = newSecureString(symbols, length)
    if copy: pyperclip.copy(newpass)
    newpass = typer.style(newpass, fg="yellow", bold=True)    
    typer.echo(f"Your new secure password : {newpass}")
    
    return newpass

@app.command("status")
def userStatus() :
    typer.secho("--- Keybin status ---", fg="cyan")
    
    config = getConfig()
    active_profile = config.active_profile
    if not active_profile : 
        typer.secho("No active profile", fg = "red")
        exit()
    
    try:
        log_file = getLogFile()
        datapath = config.profiles[active_profile].data_path
        log_count = len(log_file.logs)
        
        profileIsEncrypted = config.profiles[active_profile].encrypted
        
        if profileIsEncrypted :
            typer.echo(f"Active profile: {typer.style(f"{active_profile} (Encrypted)", bold=True, fg="green")}")
        else:
            typer.echo(f"Active profile: {typer.style(f"{active_profile} (NOT Encrypted)", bold=True, fg="red")}")
        typer.echo(f"Profile's data path: {typer.style(datapath, bold=True, fg="bright_blue")} ")
        typer.echo(f"Saved logs count: {typer.style(log_count, bold=True)}")
        
        token = tokenCheck()
        key, login_timestamp = token.split(":")
        remaingSessionTime = int(900 - (time.time() - int(login_timestamp)) )
        if remaingSessionTime > 60 :
            remaingSessionTime = int(remaingSessionTime/60) 
            typer.echo(f"Session remaining time: {typer.style(f"{remaingSessionTime}m", fg ="yellow")}")
        else: typer.echo(f"Session remaining time: {typer.style(f"{remaingSessionTime}s", fg ="red")}")
    
    except NoSessionActiveError:
        return typer.secho("No session active, try logging in.", fg= "red")
    except CorruptedSessionError:
        return typer.secho("Corrupted session, please log again.", fg ="red")
    except SessionExpiredError:
        return typer.echo(f"Session remaining time: {typer.style("Expired, log in again.", fg="red")}")


@app.command("login")
def login(
    user : str = typer.Argument(None, help="User to log onto"),
    key : str = typer.Argument(None, help="Masterkey for profile") ):
    
    if not user : 
        typer.secho("ERROR: Please select a profile to log into", fg="red")
        exit()
    
    try:
        createToken(user, key)
        typer.secho(f"Logged succesfully into {user}", fg = "green")
    except PasswordNeededError: 
        return typer.secho("ERROR: Masterkey needed for this profile", fg = "red")
    except InvalidPasswordError:
        return typer.secho("ERROR: Invalid key", fg = "red")
    except UserNotFoundError:
        return typer.secho("ERROR: User does not exist", fg = "red")
    except SessionAlreadyExistsError: 
        return typer.secho("ERROR: There's a user active, check who you are with 'keybin status' or try switching with 'keybin profile switch <profile> <masterkey>' ", fg = "red")       

    
    
@app.command("logout")
def logout():
    if not eraseToken():
        return typer.secho("Already logged out", fg="yellow")    
    typer.secho("Logged out successfully", fg = "green")