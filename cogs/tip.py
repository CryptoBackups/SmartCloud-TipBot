import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing, checks

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Tip:
    def __init__(self, bot):
        self.bot = bot
        config = parsing.parse_json('config.json')         
        self.currency_symbol = config["currency_symbol"]  

    @commands.command(pass_context=True)
    @commands.check(checks.in_server)
    async def tip(self, ctx,  amount:float, *args: discord.Member):
        """Tip users coins. You can tip multiple users"""
        snowflake = ctx.message.author.id

        users=list(set(args))
        for user in users:

            tip_user = user.id
            if snowflake == tip_user:
                await self.bot.say("{} **:warning:You cannot tip yourself!:warning:**".format(ctx.message.author.mention))
                return

            if amount <= 0.0:
                await self.bot.say("{} **:warning:You cannot tip <= 0!:warning:**".format(ctx.message.author.mention))
                return

            mysql.check_for_user(snowflake)
            mysql.check_for_user(tip_user)

            balance = mysql.get_balance(snowflake, check_update=True)

            if float(balance) < amount:
                await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(ctx.message.author.mention))
            else:
                mysql.add_tip(snowflake, tip_user, amount)
                await self.bot.say("{} **Tipped {} {} {}! :moneybag:**".format(ctx.message.author.mention, user.mention, str(amount), self.currency_symbol))

def setup(bot):
    bot.add_cog(Tip(bot))
