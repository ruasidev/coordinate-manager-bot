import discord
from discord.ext import commands
from discord import app_commands
import os
import json
from dotenv import load_dotenv

load_dotenv('.env')
token = os.environ.get("DISCORD_TOKEN")
if not token:
    print("Token is unreachable")
    exit()
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix="$", intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    try:
        synced = await client.tree.sync()
        print(f'Synced {len(synced)} commands(s)')
    except Exception as e:
        print(e)


@client.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}", ephemeral=True)

dimensions = {
    "o": "Overworld",
    "n": "Nether",
    "e": "End"
}

def add_coordinates(name, x, y, z, dimension):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {
            "Overworld": {},
            "Nether": {},
            "End": {}
        }
    new_entry = {
        "x": x,
        "y": y,
        "z": z
    }
    if dimension in data:
        data[dimension][name] = new_entry
    else:
        print("Invalid dimension:", dimension)
    
    with open("coordinates.json", 'w') as f:
        json.dump(data, f, indent=4)

def delete_coordinate(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found for some reason (huh)")

    found = False
    for dimension in data:
        if name in data[dimension]:
            del data[dimension][name]
            found = True
            break
    
    if found:
        with open("coordinates.json", 'w') as f:
            json.dump(data, f, indent=4)
        return True
    else:
        return False

def find_coordinates(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found for some reason (huh)")
        return ""
    
    for dimension in data:
        if name in data[dimension]:
            coordinates = data[dimension][name]
            x = coordinates['x']
            y = coordinates['y']
            z = coordinates['z']
            return f"`{name}` is located at `{x} {y} {z}` in the `{dimension}`"

    return f"Location `{name}` not found in any dimension :("

def rawcoords(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found for some reason (huh)")
        return ""
    
    for dimension in data:
        if name in data[dimension]:
            coordinates = data[dimension][name]
            x = coordinates['x']
            y = coordinates['y']
            z = coordinates['z']
            return f"`{x} {y} {z}` in the `{dimension}`"

    return f"Location `{name}` not found in any dimension :("

def exists(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found for some reason (huh)")
        return ""
    
    for dimension in data:
        if name in data[dimension]:
            return True
    return False

@client.tree.command(name="set")
@app_commands.describe(name = "Name of the location", x = "X Coordinate for the location", y = 'Y Coordinate for the location', z = 'Z Location for the coordinate', d = 'o = Overworld, n = Nether, e = End, Default = Overworld')
async def set(interaction: discord.Interaction, name: str, x: int, y: int, z: int, d: str = "o"):
    if exists(name):
        await interaction.response.send_message(f' The name `{name}` already exists and is located at {rawcoords(name)}')
    elif d == None:
        await interaction.response.send_message(f'`{name}` coordinates set to `{x}, {y}, {z}`')
        add_coordinates(name, x, y, z, "Overworld")
    elif not (d == "o" or d == 'n' or d == 'e'):
        await interaction.response.send_message(f"Invalid dimension argument :( pls use `o` `n` or `e` to specify dimension. \"`{d}`\" aint gonna cut it buddy")
    else:
        await interaction.response.send_message(f'`{name}` coordinates set to `{x}, {y}, {z}` in the `{dimensions[d]}`')
        add_coordinates(name, x, y, z, dimensions[d])


@client.tree.command(name='remove')
@app_commands.describe(name = "Name of the location to remove")
async def remove(interaction: discord.Interaction, name: str):
    deleted = delete_coordinate(name)
    if deleted:  
        await interaction.response.send_message(f"Removed `{name}` from coordinate list")
    else:
        await interaction.response.send_message(f"Coordinate `{name}` wasn't found in any dimension")

@client.tree.command(name="find")
@app_commands.describe(name = "Name of the location you want the coordinates to")
async def remove(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(find_coordinates(name))


@client.command()
async def test(ctx, arg):
    await ctx.send(arg)

@client.command()
async def what(ctx):
    await ctx.send(
        "To use Coordinate Manager Bot, all commands are used via slash commands (/)\n\nThere are 3 commands to use: \n/set\n`/set (name) (x) (y) (z) (dimension [optional])` \nwill set a location with a name to the specified coordinates. If no dimension argument is given, it will be defaulted to the overworld.\nPlease note if you specify a dimension, you must enter `o` for overworld, `n` for nether, and `e` for the end.\n\n/remove\n`/remove (name)` \nwill remove the set coordinates of the specified name.\n\n/find\n`/find (name)` \nwill return the coordinates and the dimension of the location name specified."
    )

client.run(token)