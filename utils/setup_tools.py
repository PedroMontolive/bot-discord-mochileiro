import discord
from discord.utils import get
import os
from discord import Colour

DATA_DIR = "data"

def save_welcome_message_id(guild_id, message_id):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(f"{DATA_DIR}/welcome_msg_{guild_id}.txt", "w") as f:
        f.write(str(message_id))

def load_welcome_message_id(guild_id):
    try:
        with open(f"{DATA_DIR}/welcome_msg_{guild_id}.txt", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return None

async def create_eternauta_role(guild):
    role = get(guild.roles, name="Eternauta")
    if not role:
        azul_ciano = discord.Colour.teal()
        role = await guild.create_role(
            name="Eternauta",
            colour=azul_ciano,
            mentionable=True
            )
    return role

async def create_welcome_channel(guild, eternauta_role):
    channel = get(guild.text_channels, name="👋🏼hey-olhe-aqui")
    if not channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            eternauta_role: discord.PermissionOverwrite(view_channel=False),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel = await guild.create_text_channel("👋🏼hey-olhe-aqui", overwrites=overwrites)
    return channel
