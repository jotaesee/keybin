import typer, pyperclip, sys
from keybin.commands.profile import profile_app
from keybin.commands.log import log_app
from keybin.core import newSecureString



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
        
    