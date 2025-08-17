import typer, pyperclip, sys
from keybin.commands.profile import profile_app
from keybin.commands.log import log_app
from keybin.core import newSecureString, getConfig, getLogFile


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
    log_file = getLogFile()
        
    active_profile = config.active_profile
    datapath = config.profiles[active_profile].data_path
    log_count = len(log_file.logs)
    
    typer.echo(f"Active profile: {typer.style(active_profile, bold=True, fg="green")}")
    typer.echo(f"Profile's data path: {typer.style(datapath, bold=True, fg="bright_blue")} ")
    typer.echo(f"Saved logs count: {typer.style(log_count, bold=True)}")
