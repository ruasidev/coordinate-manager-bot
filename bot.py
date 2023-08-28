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

# Returns a list of dimensions containing the name
def dim_count(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")

    dimensions_with_name = []

    for dimension in data:
        if name in data[dimension]:
            dimensions_with_name.append(dimension)
    
    return dimensions_with_name

def delete_coordinate(name, d):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")

    found = False
    multiple = False

    if len(dim_count(name)) > 1:
        multiple = True
    # If user doesn't specify a dimension, check if the name exists in several dimensions, returns the handled error if that's the case
    # If the user doesn't specify a dimension and the name doesn't appear in more than 1 dimension, just delete whatever we can find
    if d == None:
        # Check if the name exists in multiple dimensions
        if multiple:
            return f"`{name}` was found in multiple dimensions: `{', '.join(dim_count(name))}`. Please specify a dimension to delete this location :3"
        else:
            for dimension in data:
                if name in data[dimension]:
                    del data[dimension][name]
                    found = True
    else:
        # If user specifies a dimension, check if the name appears in that dimension. If it does, delete it
        if name in data[dimensions[d]]:
            del data[dimensions[d]][name]
            found = True
    
    if found:
        with open("coordinates.json", 'w') as f:
            json.dump(data, f, indent=4)
        if multiple: 
            return f"Removed `{name}` from the `{dimensions[d]}` from coordinate list"
        else:
            return f"Removed `{name}` from the from coordinates list"
    else:
        return f"Coordinate `{name}` wasn't found in any dimensions"

def find_coordinates(name, d):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")
        return ""
    
    if not exists(name):
        return f"Location `{name}` not found in any dimension :("

    multiple = False
    coordinate = None
    dim = None

    if len(dim_count(name)) > 1:
        multiple = True
    
    if d == None:
        if multiple:
            return f"`{name}` was found in multiple dimensions: `{', '.join(dim_count(name))}`. Please specify a dimension to query this location."
        else:
            for dimension in data:
                if name in data[dimension]:
                    coordinate = data[dimension][name]
                    dim = dimension
    else:
        if name in data[dimensions[d]]:
            coordinate = data[dimensions[d]][name]
            dim = dimensions[d]
        else:
            for dimension in data:
                if name in data[dimension]:
                    if not multiple:
                        return f"I didn't find this location in the `{dimensions[d]}`. Did you mean `{dimension}`?"
                    else:
                        return f"I didn't find this location in the `{dimensions[d]}`. Did you mean `{dim_count(name)[0]}` or `{dim_count(name)[1]}`?"
    
    x = coordinate["x"]
    y = coordinate["y"]
    z = coordinate["z"]
    return f"`{name}` is located at `{x} {y} {z}` in the `{dim}`"

def rawcoords(name):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")
        return ""
    
    for dimension in data:
        if name in data[dimension]:
            coordinates = data[dimension][name]
            x = coordinates['x']
            y = coordinates['y']
            z = coordinates['z']
            return [dimension, x, y, z]

    return f"Location `{name}` not found in any dimension :("

def exists(name, d = None):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")
        return False
    
    if d == None:
        for dimension in data:
            if name in data[dimension]:
                return True
    
    if name in data[d]:
        return True
    return False

def list_coords(d):
    try:
        with open('coordinates.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("JSON File not found. Try replacing json filename with its full PATH")
        return False
    
    locations = []

    if len(data[dimensions[d]]) < 1:
        return f"There are currently no locations set for the `{dimensions[d]}`"
    else:
        for location, coordinates in data[dimensions[d]].items():
            x = coordinates["x"]
            y = coordinates["y"]
            z = coordinates["z"]
            locations.append(f"`{location}: {x} {y} {z}`")
    
    return "\n".join(locations)

@client.tree.command(name="set")
@app_commands.describe(name = "Name of the location", x = "X Coordinate for the location", y = 'Y Coordinate for the location', z = 'Z Location for the coordinate', d = 'o = Overworld, n = Nether, e = End, Default = Overworld')
async def set(interaction: discord.Interaction, name: str, x: int, y: int, z: int, d: str = "o"):
    if not (d == "o" or d == "n" or d == "e" or d == None):
        await interaction.response.send_message(f"Invalid Dimension. I can only accept `o` `n` or `e` as valid dimensions.")
        return
    
    if exists(name, dimensions[d]):
        await interaction.response.send_message(f' The name `{rawcoords(name)[0]}` already exists in this dimension and is located at {rawcoords(name)[1]}, {rawcoords(name)[2]}, {rawcoords(name)[3]}')
    elif d == None:
        await interaction.response.send_message(f'`{name}` coordinates set to `{x}, {y}, {z}`')
        add_coordinates(name, x, y, z, "Overworld")
    else:
        await interaction.response.send_message(f'`{name}` coordinates set to `{x}, {y}, {z}` in the `{dimensions[d]}`')
        add_coordinates(name, x, y, z, dimensions[d])

# Remove Coordinates
@client.tree.command(name='remove')
@app_commands.describe(name = "Name of the location to remove")
async def remove(interaction: discord.Interaction, name: str, d: str = None):
    if not (d == "o" or d == "n" or d == "e" or d == None):
        await interaction.response.send_message(f"Invalid Dimension. I can only accept `o` `n` or `e` as valid dimensions.")
    else:
        await interaction.response.send_message( delete_coordinate(name, d) )

# Find Coordinates
@client.tree.command(name="find")
@app_commands.describe(name = "Name of the location you want the coordinates to", d = 'o = Overworld, n = Nether, e = End, Default = Overworld')
async def remove(interaction: discord.Interaction, name: str, d: str = None):
    if not (d == "o" or d == "n" or d == "e" or d == None):
        await interaction.response.send_message(f"Invalid Dimension. I can only accept `o` `n` or `e` as valid dimensions.")
        return
    
    await interaction.response.send_message( find_coordinates(name, d) )

# List Coordinates
@client.tree.command(name="list")
@app_commands.describe(dimension = 'o = Overworld, n = Nether, e = End, Default = Overworld')
async def remove(interaction: discord.Interaction, dimension: str):
    if not (dimension == "o" or dimension == "n" or dimension == "e"):
        await interaction.response.send_message(f"Invalid Dimension. I can only accept `o` `n` or `e` as valid dimensions.")
        return
    
    await interaction.response.send_message( list_coords(dimension) )

@client.command()
async def sendjson(ctx):
    try:
        with open('coordinates.json', 'rb') as f:
            json_file = discord.File(f, filename='coordinates.json')
            await ctx.send(file=json_file)
    except FileNotFoundError:
        await ctx.send("JSON File not found or some reason (huh)")


@client.command()
async def test(ctx, arg):
    await ctx.send(arg)

@client.command()
async def what(ctx):
    await ctx.send(
        "To use Coordinate Manager Bot, all commands are used via slash commands (/)\n\nThere are 3 commands to use: \n/set\n`/set (name) (x) (y) (z) (dimension [optional])` \nwill set a location with a name to the specified coordinates. If no dimension argument is given, it will be defaulted to the overworld.\nPlease note if you specify a dimension, you must enter `o` for overworld, `n` for nether, and `e` for the end.\n\n/remove\n`/remove (name)` \nwill remove the set coordinates of the specified name.\n\n/find\n`/find (name)` \nwill return the coordinates and the dimension of the location name specified.\n\n/list\n`/list (dimension)`"
    )

client.run(token)
