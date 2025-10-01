import discord
from discord.ext import commands
from discord import app_commands
import socket
import threading
import logging
import json
import asyncio
from colorama import init

###
TOKEN = 'your bot token here :3'

init()

COLORS = {
    "DEBUG": "\033[94m",   
    "INFO": "\033[92m",    
    "WARNING": "\033[93m", 
    "ERROR": "\033[91m",   
    "CRITICAL": "\033[95m",
}
RESET = "\033[0m"

class cform(logging.Formatter):
    def format(self, record):
        color = COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{RESET}"
        return super().format(record)

formatter = cform('[%(asctime)s] [%(levelname)-8s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# important but stupid variables

clients = []

kmap = {
    "f1": 290, "f2": 291, "f3": 292, "f4": 293, "f5": 294, "f6": 295,
    "f7": 296, "f8": 297, "f9": 298, "f10": 299, "f11": 300, "f12": 301,
    "1": 49, "2": 50, "3": 51, "4": 52, "5": 53,
    "6": 54, "7": 55, "8": 56, "9": 57, "0": 48,
    "a": 65, "b": 66, "c": 67, "d": 68, "e": 69, "f": 70, "g": 71, "h": 72,
    "i": 73, "j": 74, "k": 75, "l": 76, "m": 77, "n": 78, "o": 79, "p": 80,
    "q": 81, "r": 82, "s": 83, "t": 84, "u": 85, "v": 86, "w": 87, "x": 88,
    "y": 89, "z": 90,
    "space": 32, "spacebar": 32,
    "enter": 257, "return": 257,
    "tab": 258,
    "backspace": 259,
    "escape": 256, "esc": 256,
    "shift": 340, "lshift": 340, "left_shift": 340,
    "rshift": 344, "right_shift": 344,
    "ctrl": 341, "control": 341, "lctrl": 341, "left_ctrl": 341,
    "rctrl": 345, "right_ctrl": 345,
    "alt": 342, "lalt": 342, "left_alt": 342,
    "ralt": 346, "right_alt": 346,
    "up": 265, "down": 264, "left": 263, "right": 262,
    "arrow_up": 265, "arrow_down": 264, "arrow_left": 263, "arrow_right": 262,
    "mouse1": -100, "left_click": -100, "lmb": -100,
    "mouse2": -99, "right_click": -99, "rmb": -99,
    "mouse3": -98, "middle_click": -98, "mmb": -98, "wheel": -98,
    "mouse4": -97, "mouse5": -96,
    "comma": 44, ",": 44,
    "period": 46, ".": 46, "dot": 46,
    "slash": 47, "/": 47,
    "semicolon": 59, ";": 59,
    "minus": 45, "-": 45, "dash": 45,
    "equals": 61, "=": 61,
    "[": 91, "left_bracket": 91,
    "]": 93, "right_bracket": 93,
    "\\": 92, "backslash": 92,
    "`": 96, "backtick": 96, "grave": 96,
    "'": 39, "quote": 39, "apostrophe": 39,
}

def parsek(user_input: str) -> int:
    key = user_input.lower().strip()
    return kmap.get(key)

def keyexamples() -> str:
    examples = ["f6", "r", "space", "shift", "mouse1", "ctrl", "tab", "esc"]
    return ", ".join(f"`{ex}`" for ex in examples)

with open("options.json", "r") as f:
    OPTIONS = json.load(f)

with open("languages.json", "r", encoding="utf-8") as f:
    LANGUAGES = json.load(f)

with open("soundcategories.json", "r", encoding="utf-8") as f:
    SOUNDS = json.load(f)

with open("attributes.json", "r", encoding="utf-8") as f:
    ATTRIBUTES = json.load(f)
    aitems = list(ATTRIBUTES.items())

with open("keys.json", "r", encoding="utf-8") as f:
    KEYS = json.load(f)

with open("effects.json", "r", encoding="utf-8") as f:
    EFFECTS = json.load(f)

def buildtrans():
    tmap = {}
    for field_name, data in KEYS.items():
        tkey = data.get('translationKey')
        if tkey:
            tmap[tkey] = field_name
    return tmap

transfield = buildtrans()
fieldtrans = {v: k for k, v in transfield.items()}

def group_options():
    groups = {"bool": [], "int": [], "double": [], "enum": [], "complex": []}
    for name, data in OPTIONS.items():
        kind = (data.get("kind") or "").lower()
        groups.get(kind if kind in groups else "complex").append((name, data))
    return groups

def chunk(items, n=10):
    for i in range(0, len(items), n):
        yield items[i:i+n]

#def chunk(items, n=10):
#    for i in range(0, len(items), n):
#        yield items[i:i+n]

def chunk_options(n=10):
    items = list(OPTIONS.items())
    for i in range(0, len(items), n):
        yield items[i:i+n]

PAGES = list(chunk_options(10))

def handle_client(conn, addr):
    logging.info(f"\033[95m[DCMP-S]\033[0m Client connected: {addr}")
    clients.append(conn)

    if bot.is_ready():
        asyncio.run_coroutine_threadsafe(update_status(), bot.loop)

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            logging.info(f"\033[95m[DCMP-S]\033[0m Received from {addr}: {data.decode()}")
    except ConnectionResetError:
        logging.critical(f"\033[95m[DCMP-S]\033[0m Client {addr} forcibly closed connection.")
    finally:
        if conn in clients:
            clients.remove(conn)
        conn.close()
        logging.warning(f"\033[95m[DCMP-S]\033[0m Client {addr} disconnected.")

        if bot.is_ready():
            asyncio.run_coroutine_threadsafe(update_status(), bot.loop)

def broadcast(message: str):
    logging.info(f"\033[95m[DCMP-S]\033[0m \nBroadcast called:\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n{message}\n\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    for conn in clients[:]:
        try:
            conn.sendall(message.encode())
        except (BrokenPipeError, ConnectionResetError):
            logging.info("\033[95m[DCMP-S]\033[0m Removing dead client")
            if conn in clients:
                clients.remove(conn)
            conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", 5555))
    s.listen()
    logging.info("\033[95m[DCMP-S]\033[0m Server listening on 5555...")
    while True:
        try:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            logging.info(f"\033[95m[DCMP-S]\033[0m Error accepting connection: {e}")
            break

### DISCORD BOT SETUP HERE ###
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def update_status(): ### CHANGE HOW YOUR BOT LOOKS
    logging.info("\033[95m[DCMP-S]\033[0m Updating status...")
    """Update bot status with current client count"""
    try:
        client_count = len(clients)
        if client_count == 0:
            activity = discord.Game(name="waiting for connections")
        elif client_count == 1:
            activity = discord.Game(name="managing 1 client")
        else:
            activity = discord.Game(name=f"managing {client_count} clients")

        await bot.change_presence(
            status=discord.Status.idle,
            activity=activity
        )
        logging.info(f"\033[95m[DCMP-S]\033[0m Status updated: {client_count} clients")
    except Exception as e:
        logging.info(f"\033[95m[DCMP-S]\033[0m Error updating status: {e}")

class EffectPager(discord.ui.View):
    def __init__(self, items):
        super().__init__(timeout=60)
        self.pages = list(chunk(items, 10))
        self.i = 0
        self.title = "Effects"


    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.i+1}/{len(self.pages)})",
            color=discord.Color.blue()
        )
        for key, data in self.pages[self.i]:
            id = data.get("id", "").replace("minecraft:", "")
            categ = data.get("category", "?")

            embed.add_field(
                name=f"`{id}`",
                value=f"**Category:** {categ.capitalize()}",
                inline=False
            )
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages)-1:
            self.i += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

class SoundPager(discord.ui.View):
    def __init__(self, categories, title="Sound Categories"):
        super().__init__(timeout=120)
        self.pages = list(chunk(categories, 10))
        self.index = 0
        self.title = title

    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.index + 1}/{len(self.pages)})",
            color=discord.Color.blue()
        )
        for cat in self.pages[self.index]:
            embed.add_field(name=cat["name"],value=cat["desc"], inline=False)
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index > 0:
            self.index -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.index < len(self.pages) - 1:
            self.index += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

class KeyPages(discord.ui.View):
    def __init__(self, items, title):
        super().__init__(timeout=60)
        self.pages = list(chunk(items, 10))
        self.i = 0
        self.title = title

    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.i+1}/{len(self.pages)})",
            color=discord.Color.blue()
        )
        for key, data in self.pages[self.i]:
            display = data.get("displayName")
            transkey = data.get("translationKey")

            embed.add_field(
                name=f"`{transkey}`",
                value=f"**Default:** {display}",
                inline=False
            )
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages)-1:
            self.i += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

class AttributePages(discord.ui.View):
    def __init__(self, items, title):
        super().__init__(timeout=60)
        self.pages = list(chunk(items, 10))
        self.i = 0
        self.title = title

    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.i+1}/{len(self.pages)})",
            color=discord.Color.blue()
        )
        for attribute_key, data in self.pages[self.i]:

            clean_id = data.get("id", "").replace("minecraft:", "")
            default_val = data.get("defaultValue", "?")

            embed.add_field(
                name=f"`{clean_id}`",
                value=f"**Default:** {default_val}",
                inline=False
            )
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages)-1:
            self.i += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

class PagedLanguages(discord.ui.View):
    def __init__(self, items, title):
        super().__init__(timeout=60)
        self.pages = list(chunk(items, 10))
        self.i = 0
        self.title = title

    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.i+1}/{len(self.pages)})",
            color=discord.Color.blue()
        )
        for code, data in self.pages[self.i]:
            name = data.get("name", "?")
            region = data.get("region", "?")
            bidi = "↔️ RTL" if data.get("bidirectional") == "true" else ""
            embed.add_field(
                name=f"{code}",
                value=f"{name} {bidi}", # Not adding region because region is in the display name
                inline=False
            )
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages)-1:
            self.i += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

class PagedOptions(discord.ui.View):
    def __init__(self, items, title):
        super().__init__(timeout=60)
        self.pages = list(chunk(items, 10))
        self.i = 0
        self.title = title

    def make_embed(self):
        embed = discord.Embed(
            title=f"{self.title} (Page {self.i+1}/{len(self.pages)})",
            color=discord.Color.orange()
        )
        for name, data in self.pages[self.i]:
            kind = data.get("kind", "complex")
            if kind == "enum":
                embed.add_field(name=f"`{name}`", value=f"Enum: {', '.join(data.get('values', []))}", inline=False)
            elif kind in ("bool","int","double"):
                embed.add_field(name=f"`{name}`", value=f"Type: {kind}", inline=False)
            else:
                cls = data.get("class","?")
                embed.add_field(name=f"`{name}`", value=f"Complex ({cls}) — not directly settable", inline=False)
        return embed

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i > 0:
            self.i -= 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.i < len(self.pages)-1:
            self.i += 1
            await interaction.response.edit_message(embed=self.make_embed(), view=self)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')

    await update_status()

    try:
        synced = await bot.tree.sync()
        logging.info(f"\033[95m[DCMP-S]\033[0m Synced {len(synced)} command(s)")
    except Exception as e:
        logging.info(f"\033[95m[DCMP-S]\033[0m Failed to sync commands: {e}")



@bot.tree.command(name="option", description="Set a Minecraft client option")
@app_commands.describe(name="The option name (see /listoptions)", value="The value to set")
async def option(interaction: discord.Interaction, name: str, value: str):
    broadcast(f"{name} {value}")
    embed = discord.Embed(
        title="✅ Option Sent",
        description=f"**{name}** = `{value}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Clients", value=str(len(clients)))

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="listlanguages", description="List all available languages")
async def languages(interaction: discord.Interaction):
    items = list(LANGUAGES.items())
    view = PagedLanguages(items, "🌐 Available Languages")
    await interaction.response.send_message(embed=view.make_embed(), view=view, ephemeral=False)

@bot.tree.command(name="lang", description="Set the client language")
@app_commands.describe(code="The language code, e.g. en_us")
async def setlang(interaction: discord.Interaction, code: str):
    if code not in LANGUAGES:
        await interaction.response.send_message(
            f"❌ Unknown language code: `{code}`",
            ephemeral=True
        )
        return

    broadcast(f"lang {code}")
    info = LANGUAGES[code]

    embed = discord.Embed(
            title="✅ Language Sent",
            description=f"Set Language to **{info['name']}** (`{code}`)",
            color=discord.Color.green()
        )
    embed.add_field(name="Clients", value=str(len(clients)))

    await interaction.response.send_message(embed=embed, ephemeral=False)

    #info = LANGUAGES[code]
    #await interaction.response.send_message(
    #    f"✅ Language set to `{info['name']} ({info['region']})` (`{code}`)",
    #    ephemeral=False
    #)

@bot.tree.command(name="listeffects", description="List all effects")
async def listeffects(interaction: discord.Interaction):
    view = EffectPager(list(EFFECTS.items()))
    await interaction.response.send_message(embed=view.make_embed(), view=view)

@bot.tree.command(name="effect", description="Set an effect (hardcoded for 30 sec)")
@app_commands.describe(id="The effect id")
async def addeffect(interaction: discord.Interaction, id: str):
    efx = None
    for key,v in EFFECTS.items():
        if key.lower() == id.lower():
            efx = v
            break

    if not efx:
        await interaction.response.send_message(
            f"❌ Unknown effect ID: `{id.lower()}`",
            ephemeral=True
        )
        return

    broadcast(f"effect {efx['id']}")

    embed = discord.Embed(
            title="✅ Effect Sent",
            description=f"Applied **{efx["id"].replace("minecraft:", "")}** for **30s**",
            color=discord.Color.green()
        )
    embed.add_field(name="Clients", value=str(len(clients)))

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="listsounds", description="Show all sound categories")
async def sounds(interaction: discord.Interaction):
    view = SoundPager(SOUNDS)
    await interaction.response.send_message(embed=view.make_embed(), view=view)

@bot.tree.command(name="sound", description="Set a sound category's volume (see /sounds)")
@app_commands.describe(id="The sound category", volume="The volume (double)")
async def setsound(interaction: discord.Interaction, id: str, volume: int):
    sound_info = None
    for s in SOUNDS:
        if s["name"].lower() == id.lower():
            sound_info = s
            break

    if not sound_info:
        await interaction.response.send_message(
            f"❌ Unknown sound name: `{id.lower()}`",
            ephemeral=True
        )
        return

    broadcast(f"sound {sound_info["id"]} {volume}")

    embed = discord.Embed(
            title="✅ Sound Sent",
            description=f"Set **{sound_info["id"]}** to **{volume}**",
            color=discord.Color.green()
        )
    embed.add_field(name="Clients", value=str(len(clients)))

    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="listkeys", description="List all settable keys")
async def listkeys(interaction: discord.Interaction):
    view = KeyPages(list(KEYS.items()), "Keybinds")
    await interaction.response.send_message(embed=view.make_embed(), view=view)

@bot.tree.command(name="keybind", description="Change a keybinding")
@app_commands.describe(
    action="The keybind to change (use what you see in /listkeys)",
    key="The key to bind it to (e.g., f6, r, space, mouse1)"
)
async def keybind_command(interaction: discord.Interaction, action: str, key: str):
    field_name = None

    if action in KEYS:
        field_name = action
    elif action in transfield:
        field_name = transfield[action]

    if field_name is None:
        available = list(transfield.keys())[:10]
        available_str = ", ".join(f"`{k}`" for k in available)
        await interaction.response.send_message(
            f"❌ Unknown keybind: `{action}`\n"
            f"**Available:** {available_str}...\n"
            f"💡 Use `/listkeys` to see all available keybinds",
            ephemeral=True
        )
        return

    key_code = parsek(key)
    if key_code is None:
        await interaction.response.send_message(
            f"❌ Unknown key: `{key}`\n"
            f"**Examples:** {keyexamples()}\n"
            f"💡 Try common keys like letters, numbers, f-keys, or mouse buttons",
            ephemeral=True
        )
        return

    keybind_info = KEYS[field_name]
    display_name = keybind_info.get('displayName', action)
    tkey = keybind_info.get('translationKey', action)

    broadcast(f"setkey {tkey} {key_code}")

    embed = discord.Embed(
        title="✅ Keybind Set",
        description=f"`{tkey}` set to `{key.upper()}`",
        color=discord.Color.green()
    )
    embed.add_field(name="Display Name", value=display_name, inline=True)
    embed.add_field(name="Key Code", value=str(key_code), inline=True)
    embed.add_field(name="Clients", value=str(len(clients)), inline=True)

    await interaction.response.send_message(embed=embed, ephemeral=False)

@keybind_command.autocomplete('action')
async def keybind_action_autocomplete(interaction: discord.Interaction, current: str):
    if not current:
        common_translations = ["key.drop", "key.inventory", "key.forward", "key.back",
                             "key.left", "key.right", "key.jump", "key.sneak"]
        choices = []
        for trans_key in common_translations:
            if trans_key in transfield:
                field_name = transfield[trans_key]
                display_name = KEYS[field_name].get('displayName', trans_key)
                choices.append(app_commands.Choice(
                    name=f"{trans_key} ({display_name})",
                    value=trans_key
                ))
    else:
        matches = []
        current_lower = current.lower()

        for trans_key, field_name in transfield.items():
            display_name = KEYS[field_name].get('displayName', '')
            if (current_lower in trans_key.lower() or
                current_lower in display_name.lower()):
                matches.append(app_commands.Choice(
                    name=f"{trans_key} ({display_name})",
                    value=trans_key
                ))
        choices = matches

    return choices[:25]

@keybind_command.autocomplete('key')
async def keybind_key_autocomplete(interaction: discord.Interaction, current: str):
    if not current:
        common_keys = ["f6", "r", "space", "shift", "ctrl", "mouse1", "tab", "esc"]
        choices = [app_commands.Choice(name=key.upper(), value=key) for key in common_keys]
    else:
        current_lower = current.lower()
        matches = [key for key in kmap.keys() if current_lower in key]
        choices = [app_commands.Choice(name=key.upper(), value=key) for key in matches]

    return choices[:25]

@bot.tree.command(name="listattributes", description="List all attributes")
async def listattributes(interaction: discord.Interaction):
    view = AttributePages(aitems, "Attributes")
    await interaction.response.send_message(embed=view.make_embed(), view=view)

@bot.tree.command(name="attribute", description="Set the attribute to a value")
@app_commands.describe(id="The attribute name", value="The value (type reset to reset value)")
async def attribute(interaction: discord.Interaction, id: str, value: str):
    normal = id.lower()
    if normal not in ATTRIBUTES:
        await interaction.response.send_message(
            f"❌ Unknown attribute: `{id}`",
            ephemeral=True
        )
        return

    broadcast(f"attribute {ATTRIBUTES[normal]['id']} {value}")
    info = ATTRIBUTES[normal]

    if value.lower() == 'reset':
        desc = f"Reset `{info['id']}` to **{info['defaultValue']}**"
        ntitle="🔄 Attribute Reset"

    else:
        ntitle="✅ Attribute Set"
        desc = f"Set `{info['id']}` to **{value}**"

    embed = discord.Embed(
            title=ntitle,
            description=desc,
            color=discord.Color.green()
        )
    embed.add_field(name="Clients", value=str(len(clients)))

    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="listoptions", description="Show option groups")
async def listoptions(interaction: discord.Interaction):
    groups = group_options()
    embed = discord.Embed(title="Option Groups", color=discord.Color.orange())
    for k in ("bool","int","double","enum","complex"):
        embed.add_field(name=k.capitalize(), value=f"{len(groups[k])} options", inline=False)
    embed.add_field(name="", value="Use /showgroup <name> to view options!")
    await interaction.response.send_message(embed=embed, ephemeral=False)

@bot.tree.command(name="showgroup", description="Show all options of a type")
@app_commands.describe(kind="One of: bool, int, double, enum, complex")
async def showgroup(interaction: discord.Interaction, kind: str):
    groups = group_options()
    kind = kind.lower()
    items = groups.get(kind, [])
    if not items:
        await interaction.response.send_message(f"No options in `{kind}`.", ephemeral=False)
        return
    view = PagedOptions(items, f"{kind.capitalize()} Options")
    await interaction.response.send_message(embed=view.make_embed(), view=view, ephemeral=False)

@bot.tree.command(name="searchoption", description="Search options by keyword")
@app_commands.describe(keyword="Part of the option name")
async def searchoption(interaction: discord.Interaction, keyword: str):
    keyword = keyword.lower()
    results = [(n,d) for n,d in OPTIONS.items() if keyword in n.lower()]
    if not results:
        await interaction.response.send_message(f"No results for `{keyword}`.", ephemeral=False)
        return
    view = PagedOptions(results, f"Search: {keyword}")
    await interaction.response.send_message(embed=view.make_embed(), view=view, ephemeral=False)


#@bot.tree.command(name="broadcastraw", description="Broadcast a raw string to all connected socket clients")
#@app_commands.describe(raw="The raw string to broadcast to socket clients")
async def broadcastraw(interaction: discord.Interaction, raw: str):
    try:
        broadcast(raw)

        client_count = len(clients)
        await interaction.response.send_message(
            f"✅ Broadcasted message to {client_count} connected client(s):\n```{raw}```",
            ephemeral=False
        )

        logging.info(f"\033[95m[DCMP-S]\033[0m Discord user {interaction.user} broadcasted: {raw}")

    except Exception as e:
        await interaction.response.send_message(
            f"❌ Error broadcasting message: {str(e)}",
            ephemeral=False
        )
        logging.info(f"\033[95m[DCMP-S]\033[0m Error in broadcastraw command: {e}")

@bot.tree.command(name="clientcount", description="Check how many socket clients are connected")
async def clientcount(interaction: discord.Interaction):
    """
    Slash command to check connected client count
    """
    client_count = len(clients)
    await interaction.response.send_message(
        f"📊 Currently connected socket clients: {client_count}",
        ephemeral=False
    )

#@bot.tree.command(name="updatestatus", description="Manually update the bot status")
async def updatestatus(interaction: discord.Interaction):
    await update_status()
    client_count = len(clients)
    await interaction.response.send_message(
        f"🔄 Status updated! Currently managing {client_count} client(s)",
        ephemeral=False
    )

logging.info("\033[95m[DCMP-S]\033[0m Starting socket server...")
threading.Thread(target=start_server, daemon=True).start()

bot.run(TOKEN)