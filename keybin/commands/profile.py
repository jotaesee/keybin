from rich.console import Console
from rich.table import Table
from keybin.exceptions import *
import typer
from keybin.core import getConfig, startProfile, unlockDek, eraseProfileData, eraseToken, createToken, require_active_session
from keybin.models import ConfigDataModel, ProfileModel

profile_app = typer.Typer()


@profile_app.command("list")
def list():
    config: ConfigDataModel = getConfig()
    console = Console()
    table = Table(title="All profiles list")

    table.add_column("Profile name", style="cyan", no_wrap=True)
    table.add_column("Datapath", style="green")
    table.add_column("Encrypted", style="magenta")

    for profile_name, profile_data in config.profiles.items():
        encrypted_display = "Yes" if profile_data.encrypted else "No"
        table.add_row(profile_name, profile_data.data_path, encrypted_display)

    console.print(table)
    
    
@profile_app.command("add")
def newProfile(user : str = typer.Option(None , "--user", "-u"), key : str = typer.Option(None, "--key", "-k"), path : str = typer.Option(None, "--path", "-p") ):
    if not user : user = typer.prompt("Insert new profile name")
    if not key and typer.confirm(f"Add masterkey? (RECOMMENDED)"): key = typer.prompt("Insert new profile masterkey", hide_input=True)
    if not path and typer.confirm("Add custom path?"): path = typer.prompt("Insert custom path")
 
    try :
        startProfile(user, key)
        typer.secho("Profile created correctly.", fg="green")
        if getConfig().active_profile:
            if typer.confirm(f"change to {typer.style(f"{user}", fg="yellow")}?"):
                switchProfile(user, key)
                
    except ProfileAlreadyExistsError:
        typer.secho("ERROR: There's already a profile with this name, try another.", fg = "red")
    

@profile_app.command("switch")
@require_active_session
def switchProfile(user:str = typer.Argument(None, help="Profile to switch to"), key : str = typer.Argument(None, help="Masterkey for profile")):
    
    config : ConfigDataModel = getConfig()    
    if not user : 
        user = typer.prompt("Select user:")
    if user not in config.profiles:
            typer.echo(typer.style("ERROR : This profile does not exist.", fg="red"))
            return 0

    profileIsEncrypted = config.profiles[user].encrypted    
    
    if profileIsEncrypted : ## si el perfil tiene contraseña tengo que pedirla y chequear 
        if not key : key = typer.prompt("Please insert profile's masterkey: \n", hide_input=True)
        if not unlockDek(key, user):
            typer.echo(typer.style("ERROR : Incorrect masterkey.", fg="red"))
            return 0
        
    eraseToken() ## eliminamos token anterior
    createToken(user, key) ## creamos nueva sesion
    typer.echo(f"{typer.style("Switched correctly to", fg="green")} {typer.style(f"{user}", fg="yellow")}")
    
    
@profile_app.command("delete")
def deleteProfile(profile: str = typer.Argument(None)):
        
    config = getConfig()
    if not profile : profile = typer.prompt("Input a profile to delete")
    
    if profile not in config.profiles:
        typer.echo(typer.style("ERROR : This profile does not exist.", fg="red"))
        return 0
    
    profileIsEncrypted = config.profiles[profile].encrypted
    
    if  profileIsEncrypted: 
        key = typer.prompt("Insert profile's masterkey to confirm deletion", hide_input=True)
        if not unlockDek(key, profile) : 
            typer.echo(typer.style("ERROR : Incorrect masterkey.", fg="red"))
            typer.Exit()
    else:
        if not typer.confirm("This profile doesn't have a masterkey. Please confirm deletion manually:", default=False):
            typer.echo(typer.style("Operation cancelled", fg="red"))
            typer.Exit()
        
    eraseProfileData(config, profile)
    typer.echo(f"{typer.style(profile, fg = "yellow")} {typer.style("deleted successfully.", fg="green")}" )
    if config.active_profile == profile : eraseToken()
    
    