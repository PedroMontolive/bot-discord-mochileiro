import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from utils.permissions import has_role, is_owner
from discord.utils import get
from cogs.tickets import TicketMenu  # Importa a View TicketMenu direto da cog

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

    guild_id = os.getenv("GUILD_ID")
    if not guild_id:
        print("❌ Variável GUILD_ID não configurada no .env")
        return

    guild = bot.get_guild(int(guild_id))
    if not guild:
        print(f"❌ Guilda com ID {guild_id} não encontrada!")
        return

    categoria = get(guild.categories, name="SUPORTE")
    if not categoria:
        print("❌ Categoria 'SUPORTE' não encontrada!")
        return

    canal_suporte = get(categoria.text_channels, name="🧰suporte-geral")
    if not canal_suporte:
        print("❌ Canal '🧰suporte-geral' não encontrado!")
        return

    pins = await canal_suporte.pins()
    for mensagem in pins:
        if mensagem.author == bot.user and mensagem.embeds:
            try:
                await mensagem.edit(view=TicketMenu())
                print("📌 View TicketMenu registrada com sucesso.")
            except Exception as e:
                print(f"⚠️ Erro ao registrar View TicketMenu: {e}")
            break

@bot.command()
@commands.has_role("Eternauta")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_role("Eternauta")
async def comandos(ctx):
    cmds = [cmd.name for cmd in bot.commands]
    await ctx.send(f"Comandos disponíveis: {', '.join(cmds)}")

async def load_extension_with_style(bot, name, path):
    print(f"⏳ Carregando [{name.upper():<10}] ...", end="", flush=True)
    await asyncio.sleep(0.4)  # simula tempo de carregamento
    await bot.load_extension(path)
    print(f"\r✅ Extensão [{name.upper():<10}] carregada com sucesso!")

async def main():
    try:
        async with bot:
            await load_extension_with_style(bot, "welcome", "cogs.welcome")
            await load_extension_with_style(bot, "tickets", "cogs.tickets")
            await load_extension_with_style(bot, "notices", "cogs.notices")

            print("\n🚀 Todas as extensões carregadas! Iniciando o bot...\n")
            await bot.start(TOKEN)
    except KeyboardInterrupt:
        print("\n[!] Bot encerrado com CTRL+C com segurança. Até mais, comandante.")
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Encerrando execução...")
