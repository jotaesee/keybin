import typer, pyperclip, sys
from keybin.models import passwordLog
from keybin.commands.profile import profile_app
from typing import List
from keybin.core import newSecureString, newLog, doSearch
from rich.table import Table
from rich.console import Console

console = Console()


app = typer.Typer()
app.add_typer(profile_app, name="profile")

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
        
        
@app.command("genlog")
@app.command("gl")
def genlog(
    service : str = typer.Option(None,"--service", "-s"), 
    user : str = typer.Option(None, "--user", "-u"),
    email : str = typer.Option(None, "--email", "-e"),
    password : str = typer.Option(None, "--password", "-p",),
    tags : List[str] = typer.Option(None, "--tags", "-t", help="Add tags, used for filtering when searching."),
    no_prompts: bool = typer.Option(False, "--no-prompts", "-n", help="Don't ask for missing data"),
    autopass: bool = typer.Option(False, "--autopass", "-a", help="Create and auto assign a secure password")
    ):

    if password is None and autopass : password = newSecureString()
    
    if not no_prompts:
        if service is None : service = typer.prompt("Enter service")
        if user is None : user = typer.prompt("Enter user")
        if email is None : email = typer.prompt("Enter email")
        if password is None : password = typer.prompt("Enter password")       
        if tags is None : 
            response = typer.confirm("Would you like to add tags?")
            if response:
                typer.echo("Enter tags separated by commas:")
                tag_input = input()
                tags = [t.strip() for t in tag_input.split(",") if t.strip()]
    
    newLog(service, user, email, password, tags)
    

@app.command()
def find(
    search: str = typer.Argument(None),
    service: str = typer.Option(None, "--service", "-s"),
    username: str = typer.Option(None, "--user", "-u", help="Search exact match for username"),
    tags: list[str] = typer.Option(None, "--tags", "-t", help="Use this for filtering with tags."),
):
    searchResult: List[passwordLog] = doSearch(search, service, username, tags)

    if not searchResult:
        typer.echo("No results found")
        return

    table = Table(title="Search Results")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Service", style="magenta")
    table.add_column("User", style="green")
    table.add_column("Email", style="yellow")
    table.add_column("Tags", style="blue")
    table.add_column("Created At", style="dim")

    for log in searchResult:
    
        table.add_row(
            str(log.logID),
            log.service,
            log.user,
            log.email,
            str(log.tags),
            log.createdAt,
        )
 
    console.print(table)
    