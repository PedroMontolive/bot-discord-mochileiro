import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from utils.permissions import has_role, is_owner

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
    print(f"Bot conectado como {bot.user}")

@bot.command()
@commands.has_role("Eternauta")
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
@commands.has_role("Eternauta")
async def comandos(ctx):
    cmds = [cmd.name for cmd in bot.commands]
    await ctx.send(f"Comandos disponíveis: {', '.join(cmds)}")

async def main():
    try:
        async with bot:
            print("Carregando extensão welcome...")
            await bot.load_extension("cogs.welcome")
            print("Extensão carregada com sucesso!")
            print("Carregando extensão tickets...")
            await bot.load_extension("cogs.tickets")
            print("Extensão carregada com sucesso!")
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
