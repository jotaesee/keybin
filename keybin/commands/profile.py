from rich.console import Console
from rich.table import Table

import typer
from keybin.core import getConfig, startProfile, saveConfig, checkPass, eraseProfileData
from keybin.models import ConfigDataModel, ProfileModel

profile_app = typer.Typer()


@profile_app.command()
def whoami():
    config : ConfigDataModel = getConfig()
    typer.echo(config.active_profile)

@profile_app.command("list")
def list():
    config: ConfigDataModel = getConfig()
    console = Console()
    table = Table(title="All profiles list")

    table.add_column("Profile name", style="cyan", no_wrap=True)
    table.add_column("Datapath", style="green")
    table.add_column("Masterkey", style="magenta")

    for profile_name, profile_data in config.profiles.items():
        masterkey_display = "Yes" if profile_data.masterkey else "No"
        table.add_row(profile_name, profile_data.data_path, masterkey_display)

    console.print(table)
    
    
    
@profile_app.command("new")
def newProfile(user : str = typer.Option(None , "--user", "-u"), key : str = typer.Option(None, "--key", "-k"), path : str = typer.Option(None, "--path", "-p") ):
    if not user : user = typer.prompt("Insert new profile name")
    if not path and typer.confirm("Add custom path?"): path = typer.prompt("Insert custom path")
    if not key and typer.confirm("Add masterkey? (RECOMMENDED)"): key = typer.prompt("Insert new profile masterkey")
    startProfile(user, key)
    typer.echo(typer.style("Profile created correctly.", fg="green"))
    if typer.confirm(f"change to {typer.style(f"{user}", fg="yellow")}?"):
        switchProfile(user, tryPass=key)
        

@profile_app.command("switch")
def switchProfile(user:str = typer.Argument(None), tryPass : str = typer.Option(None, "--key", "-k")):
    
    config : ConfigDataModel = getConfig()    
    if not user : 
        user = typer.prompt("Select user")
    if user not in config.profiles:
            typer.echo(typer.style("ERROR : This profile does not exist.", fg="red"))
            return 0
        

    configKey = config.profiles[user].masterkey ## llave del perfil    
    if configKey != "" and configKey != None : ## si no esta vacia y no es nula tengo q que comprobar la contraseña
        if not tryPass : tryPass = typer.prompt("Please insert profile's masterkey: \n")
        if not checkPass(tryPass, config.profiles[user].masterkey):
            typer.echo(typer.style("ERROR : Incorrect masterkey.", fg="red"))
            return 0
        
    config.active_profile = user
    
    typer.echo(f"{typer.style("Switched correctly to", fg="green")} {typer.style(f"{user}", fg="yellow")}")
    saveConfig(config)
    
    
@profile_app.command("delete")
def deleteProfile(profile: str = typer.Argument(None)):
        
    config = getConfig()
    if not profile : profile = typer.prompt("Input a profile to delete")
        
    if profile == "default":
        typer.echo(typer.style("ERROR : You can not delete the default profile.", fg="red"))
        return 0
        
    if profile not in config.profiles:
        typer.echo(typer.style("ERROR : This profile does not exist.", fg="red"))
        return 0
    
    if config.profiles[profile].masterkey : 
        key = typer.prompt("Insert profile's masterkey to confirm deletion")
        if not checkPass(key, config.profiles[profile].masterkey) : 
            typer.echo(typer.style("ERROR : Incorrect masterkey.", fg="red"))
            return 0
    else:
        if not typer.confirm("This profile doesn't have a masterkey. Please confirm deletion manually:", default=False):
            typer.echo(typer.style("Operation cancelled", fg="red"))
            return 0
        
    eraseProfileData(config, profile)
    typer.echo(f"{typer.style(profile, fg = "yellow")} {typer.style("deleted successfully.", fg="green")}" )
    if config.active_profile == profile : switchProfile(user="default")
    
    