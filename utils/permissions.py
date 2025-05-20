from discord.ext.commands import check
import discord

def has_role(role_name):
    async def predicate(ctx):
        role = discord.utils.get(ctx.author.roles, name=role_name)
        return role is not None
    return check(predicate)
    
def is_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner
    return check(predicate)
