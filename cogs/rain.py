import math
import discord, json, requests
from discord.ext import commands
from utils import output, helpers, parsing, mysql_module
import random

mysql = mysql_module.Mysql()

class Rain:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def rain(self, ctx, amount:float):
        """Rain all active users"""

        config = parsing.parse_json('config.json')   
        CURRENCY_SYMBOL = config["currency_symbol"] 

        rain_config = parsing.parse_json('config.json')['rain']
        RAIN_MINIMUM = rain_config['min_amount']
        RAIN_REQUIRED_USER_ACTIVITY_M = rain_config['user_activity_required_m']   
        USE_MAX_RECIPIENTS = rain_config['use_max_recipients']
        MAX_RECIPIENTS = rain_config['max_recipients']        

        message = ctx.message
        if helpers.is_private_dm(self.bot, message.channel):
            return

        if amount < RAIN_MINIMUM:
            await self.bot.say("**:warning: Amount {} for rain is less than minimum {} required! :warning:**".format(amount,RAIN_MINIMUM))
            return

        snowflake = ctx.message.author.id

        mysql.check_for_user(snowflake)
        balance = mysql.get_balance(snowflake, check_update=True)

        if float(balance) < amount:
            await self.bot.say("{} **:warning:You cannot rain more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        # Create tip list
        active_id_users = mysql.get_active_users_id(RAIN_REQUIRED_USER_ACTIVITY_M, True)
        if int(ctx.message.author.id) in active_id_users:
            active_id_users.remove(int(ctx.message.author.id))

        if USE_MAX_RECIPIENTS:
            len_receivers = min(len(active_id_users), MAX_RECIPIENTS)
        else:
            len_receivers = len(active_id_users)

        if len_receivers == 0:
            await self.bot.say("{}, you are all alone if you don't include bots! Trying raining when people are online and active.".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len_receivers) / 1e8
        if amount_split == 0:
            await self.bot.say("{} **:warning:{} is not enough to split between {} users:warning:**".format(ctx.message.author.mention, amount, len_receivers))
            return    
                     
        active_users = [x for x in ctx.message.server.members if int(x.id) in active_id_users and x.bot==False]

        receivers = []        
        for active_user in active_users:
            receivers.append(active_user.mention)
            mysql.check_for_user(active_user.id)
            mysql.add_tip(snowflake, active_user.id, amount_split)

        if len(receivers) == 0:
            await self.bot.say("{}, you are all alone if you don't include bots! Trying raining when people are online and active.".format(ctx.message.author.mention))
            return

        long_soak_msg = "{} **Rained {} {} on {} [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), CURRENCY_SYMBOL, ', '.join([x for x in receivers]), str(amount))

        if len(long_soak_msg) > 2000:
            await self.bot.say("{} **Rained {} {} on {} users [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), CURRENCY_SYMBOL, len_receivers, str(amount)))
        else:
            await self.bot.say(long_soak_msg)

def setup(bot):
    bot.add_cog(Rain(bot))
