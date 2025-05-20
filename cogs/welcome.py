import discord
from discord.ext import commands
from discord.utils import get
from utils.setup_tools import create_eternauta_role, create_welcome_channel, save_welcome_message_id, load_welcome_message_id
from utils.permissions import has_role, is_owner

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    @is_owner()
    async def setup(self, ctx):
        guild = ctx.guild
        role = await create_eternauta_role(guild)
        channel = await create_welcome_channel(guild, role)

        welcome_embed = discord.Embed(
            title="👋 Bem-vindo(a) à comunidade Refúgio 42!",
            description=(
                "Antes de começarmos, precisamos saber se você é humano (preferencialmente, né 😅).\n\n"
                "✅ Basta clicar no ícone abaixo para continuar sua jornada como um **Eternauta**."
            ),
            color=discord.Color.blue()
        )

        message = await channel.send(embed=welcome_embed)
        await message.pin()
        await message.add_reaction("✅")
        save_welcome_message_id(guild.id, message.id)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
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
        if not role:
            print("Cargo 'Eternauta' não encontrado.")
            return

        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except:
                print("Falha ao buscar membro.")
                return

        if role not in member.roles:
            try:
                await member.add_roles(role)
                print(f"Cargo 'Eternauta' adicionado para {member}.")
            except Exception as e:
                print(f"Erro ao adicionar cargo: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        welcome_msg_id = load_welcome_message_id(guild.id)
        if not welcome_msg_id or payload.message_id != welcome_msg_id:
            return

        if str(payload.emoji) != "✅":
            return

        role = get(guild.roles, name="Eternauta")
        if not role:
            print("Cargo 'Eternauta' não encontrado.")
            return

        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except:
                print("Falha ao buscar membro.")
                return

        if role in member.roles:
            try:
                await member.remove_roles(role)
                print(f"Cargo 'Eternauta' removido de {member}.")
            except Exception as e:
                print(f"Erro ao remover cargo: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
