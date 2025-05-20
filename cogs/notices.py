import os
import json
from discord.ext import commands
import discord
from utils.permissions import has_role, is_owner
import aiohttp
import io

class Notices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # caminho para arquivo na pasta data
        self.config_file = "data/notice_config.json"
        
        # cria a pasta data se não existir
        os.makedirs("data", exist_ok=True)
        
        self.notice_channel_id = None
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r") as f:
                data = json.load(f)
                self.notice_channel_id = data.get("notice_channel_id")
        except (FileNotFoundError, json.JSONDecodeError):
            self.notice_channel_id = None

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump({"notice_channel_id": self.notice_channel_id}, f)

    @commands.command(name='setup_notices')
    @commands.has_permissions(administrator=True)
    @is_owner()
    async def setup_notices(self, ctx):
        guild = ctx.guild

        role_staff = discord.utils.get(guild.roles, name="Staff")
        role_eternauta = discord.utils.get(guild.roles, name="Eternauta")

        if not role_staff or not role_eternauta:
            await ctx.send("Os cargos 'Staff' e/ou 'Eternauta' não foram encontrados.")
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role_eternauta: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            role_staff: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        channel = await guild.create_text_channel("🛎・avisos", overwrites=overwrites)
        self.notice_channel_id = channel.id
        self.save_config()  # salva o ID do canal no arquivo
        await ctx.send(f"Canal {channel.mention} criado para avisos!")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.notice_channel_id or message.author.bot:
            return

        if message.channel.id == self.notice_channel_id:
            timestamp = message.created_at.strftime("%d/%m/%Y %H:%M")

            embed = discord.Embed(
                description=message.content or "⠀",
                color=discord.Color.gold()
            )
            embed.set_footer(text=f"{timestamp}")

            file = None
            if message.attachments:
                img = message.attachments[0]
                if img.content_type and img.content_type.startswith("image"):
                    # baixa a imagem em memória
                    async with aiohttp.ClientSession() as session:
                        async with session.get(img.url) as resp:
                            if resp.status == 200:
                                data = await resp.read()
                                file = discord.File(io.BytesIO(data), filename=img.filename)
                                embed.set_image(url=f"attachment://{img.filename}")

            if file:
                await message.channel.send(embed=embed, file=file)
            else:
                await message.channel.send(embed=embed)

            await message.delete()


async def setup(bot):
    await bot.add_cog(Notices(bot))
