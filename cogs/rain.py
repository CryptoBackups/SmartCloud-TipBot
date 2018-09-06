import discord, json, requests
from discord.ext import commands


class Rain:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def make_rain(self):
        """Rain code"""
        await self.bot.say("Doing some rain.")

def setup(bot):
    bot.add_cog(Rain(bot))
