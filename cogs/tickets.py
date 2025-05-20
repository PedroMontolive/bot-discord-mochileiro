import discord
from discord.ext import commands
from discord.utils import get
from utils.permissions import has_role, is_owner
from utils.setup_tools import create_staff_role
import os
import io
from discord import File
from discord.ui import View, Select, Button  # mantém Button importado

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    @is_owner()
    async def setup_suporte(self, ctx):
        guild = ctx.guild
        categoria = get(guild.categories, name="SUPORTE")
        if categoria is None:
            categoria = await guild.create_category("SUPORTE")

        canais_texto = ["🧰suporte-geral"]
        canais_audio = ["💾 Suporte 01", "💾 Suporte 02"]

        for nome in canais_texto:
            canal = get(categoria.text_channels, name=nome)
            if canal is None:
                canal = await guild.create_text_channel(nome, category=categoria)
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False, read_messages=True),
                guild.me: discord.PermissionOverwrite(send_messages=True, read_messages=True)
            }
            await canal.edit(overwrites=overwrites)

        for nome in canais_audio:
            canal = get(categoria.voice_channels, name=nome)
            if canal is None:
                await guild.create_voice_channel(nome, category=categoria)

        staff_role = await create_staff_role(guild)

        mensagem = (
            f"**Setup concluído!**\n\n"
            f"GUILD_ID: {guild.id}\n"
            f"STAFF_ROLE_ID: {staff_role.id}\n"
            f"CATEGORIA_TICKET_ID: {categoria.id}\n\n"
            f"Use esses IDs para configurar seu arquivo .env."
        )
        try:
            await ctx.author.send(mensagem)
            await ctx.send("Setup do suporte concluído! IDs enviados no privado.")
        except discord.Forbidden:
            await ctx.send("Não consegui enviar mensagem privada. Verifique suas configurações de privacidade.")

    @commands.command()
    async def ticket(self, ctx):
        guild = ctx.guild
        categoria = get(guild.categories, name="SUPORTE")
        if categoria is None:
            await ctx.send("O sistema de suporte não está configurado corretamente.", delete_after=10)
            return

        canal_suporte = get(categoria.text_channels, name="🧰suporte-geral")
        if canal_suporte is None:
            await ctx.send("O canal de suporte-geral não foi encontrado.", delete_after=10)
            return

        pins = await canal_suporte.pins()
        embed_fixado = None
        for msg in pins:
            if msg.author == self.bot.user and msg.embeds:
                embed_fixado = msg
                break

        if not embed_fixado:
            embed = discord.Embed(
                title="🎫 Crie seu ticket aqui",
                description="Selecione um assunto abaixo para abrir um ticket e falar com a equipe de suporte.",
                color=discord.Color.blue()
            )
            view = TicketMenu()
            mensagem = await canal_suporte.send(embed=embed, view=view)
            await mensagem.pin()

        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.send(f"O painel de tickets está disponível em {canal_suporte.mention}", delete_after=10)

    async def criar_mensagem_fechar(self, canal, user, staff_role):
        view = CloseTicketView(user, staff_role)
        msg = await canal.send("Use o botão abaixo para finalizar este ticket.", view=view)
        await msg.pin()


class TicketMenu(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


class CloseTicketView(View):
    def __init__(self, ticket_owner, staff_role):
        super().__init__(timeout=None)
        self.ticket_owner = ticket_owner
        self.staff_role = staff_role

    @discord.ui.button(label="Finalizar Ticket", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        if user != self.ticket_owner and self.staff_role not in user.roles:
            await interaction.response.send_message("Você não tem permissão para finalizar este ticket.", ephemeral=True)
            return

        channel = interaction.channel
        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            author = msg.author.display_name
            content = msg.content
            messages.append(f"{author}: {content}")

        texto = "\n".join(messages)
        arquivo = io.BytesIO(texto.encode('utf-8'))
        arquivo.seek(0)

        try:
            await self.ticket_owner.send(file=discord.File(fp=arquivo, filename=f"ticket-{channel.name}.txt"))
        except discord.Forbidden:
            await interaction.response.send_message("Não consegui enviar o arquivo no privado do usuário.", ephemeral=True)
            return

        await interaction.response.send_message("Ticket finalizado e arquivo enviado no privado.", ephemeral=True)
        await channel.delete()


class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="REFÚGIO - SUPORTE", emoji="🛠️", description="Suporte geral no Refúgio", value="suporte"),
            discord.SelectOption(label="REFÚGIO - DENÚNCIA", emoji="🚨", description="Denúncias no Refúgio", value="denuncia"),
            discord.SelectOption(label="REFÚGIO - HACKER", emoji="🕵️", description="Suspeita de hacker", value="hacker"),
            discord.SelectOption(label="GERAL - CONTRIBUIÇÃO", emoji="💰", description="Contribuições gerais", value="contribuicao")
        ]
        super().__init__(placeholder="Selecione um assunto", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        assunto = self.values[0]
        user = interaction.user
        guild = interaction.guild

        GUILD_ID = os.getenv("GUILD_ID")
        STAFF_ROLE_ID = os.getenv("STAFF_ROLE_ID")
        CATEGORIA_TICKET_ID = os.getenv("CATEGORIA_TICKET_ID")

        if not GUILD_ID or not STAFF_ROLE_ID or not CATEGORIA_TICKET_ID:
            await interaction.response.send_message("Configuração do bot incompleta.", ephemeral=True)
            return

        try:
            guild_id_int = int(GUILD_ID)
            staff_role_id_int = int(STAFF_ROLE_ID)
            categoria_id_int = int(CATEGORIA_TICKET_ID)
        except ValueError:
            await interaction.response.send_message("IDs configurados no .env inválidos.", ephemeral=True)
            return

        if guild.id != guild_id_int:
            await interaction.response.send_message("Este comando só funciona neste servidor.", ephemeral=True)
            return

        nome_canal = f"ticket-{assunto}-{user.name}".replace(" ", "-").lower()
        categoria = guild.get_channel(categoria_id_int)
        staff_role = guild.get_role(staff_role_id_int)

        if categoria is None or staff_role is None:
            await interaction.response.send_message("Configuração incorreta: categoria ou cargo não encontrados.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        existing_channel = get(categoria.text_channels, name=nome_canal)
        if existing_channel:
            await interaction.response.send_message(f"Você já tem um ticket aberto: {existing_channel.mention}", ephemeral=True)
            return

        canal = await guild.create_text_channel(nome_canal, category=categoria, overwrites=overwrites)
        
        # Chama método para enviar a mensagem de fechar ticket
        cog = self.view.bot.get_cog("TicketsCog") if hasattr(self.view, "bot") else None
        if cog:
            await cog.criar_mensagem_fechar(canal, user, staff_role)
        else:
            # Caso não tenha referência do cog, cria a view diretamente
            view = CloseTicketView(user, staff_role)
            await canal.send("Use o botão abaixo para finalizar este ticket.", view=view)

        await interaction.response.send_message(f"Ticket criado: {canal.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
