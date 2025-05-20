import discord
from discord.ext import commands
from discord.utils import get
from utils.setup_tools import create_eternauta_role, create_welcome_channel, save_welcome_message_id, load_welcome_message_id
import os

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup(self, ctx):
        guild = ctx.guild
        role = await create_eternauta_role(guild)
        channel = await create_welcome_channel(guild, role)

        welcome_message = (
            "👋 **Bem-vindo(a) à comunidade Refúgio 42!**\n\n"
            "Antes de começarmos, precisamos saber se você é humano (preferencialmente, né 😅).\n\n"
            "✅ Basta clicar no ícone abaixo para continuar sua jornada como um **Eternauta**."
        )
        message = await channel.send(welcome_message)
        await message.pin()
        await message.add_reaction("✅")
        save_welcome_message_id(guild.id, message.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        welcome_msg_id = load_welcome_message_id(guild.id)
        if not welcome_msg_id or payload.message_id != welcome_msg_id:
            return

        if str(payload.emoji) != "✅":
            return

        role = get(guild.roles, name="Eternauta")
        if role:
            member = guild.get_member(payload.user_id)
            if member and role not in member.roles:
                await member.add_roles(role)

def setup(bot):
    bot.add_cog(WelcomeCog(bot))
