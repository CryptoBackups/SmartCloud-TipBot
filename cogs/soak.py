import math
import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, checks, parsing
import random

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Soak:
    def __init__(self, bot):
        self.bot = bot
        soak_config = parsing.parse_json('config.json')['soak']
        config = parsing.parse_json('config.json')        
        '''
        soak_max_recipients sets the max recipients for a soak. chosen randomly.
        soak_min_received sets the minimum possible soak received for a user.
        The number of soak recipients will be adjusted to fit these constraints
        if enabled via use_max_recipients and use_min_received
        '''
        self.soak_max_recipients = soak_config["soak_max_recipients"]
        self.use_max_recipients = soak_config["use_max_recipients"]
        self.soak_min_received = soak_config["soak_min_received"]
        self.use_min_received = soak_config["use_min_received"]
        self.soak_minimum = soak_config['min_amount']        
        self.currency_symbol = config["currency_symbol"] 
        self.prefix = config["prefix"]                

    @commands.command(pass_context=True)
    @commands.check(checks.allow_soak)
    async def soak(self, ctx, amount: float, role_id=""):
        """Tip all online users"""
        if self.use_max_recipients and self.soak_max_recipients == 0:
            await self.bot.say("**:warning: max users for soak is set to 0! Talk to the config owner. :warning:**")
            return

        if amount < self.soak_minimum:
            await self.bot.say("**:warning: Amount {} for soak is less than minimum {} required! :warning:**".format(amount,self.soak_minimum))
            return

        snowflake = ctx.message.author.id

        mysql.check_for_user(snowflake)
        balance = mysql.get_balance(snowflake, check_update=True)

        if float(balance) < amount:
            await self.bot.say("{} **:warning:You cannot soak more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        users_list=[]
        if role_id=="" or role_id=="@everyone" or role_id=="@here" or role_id=="all":
            users_list = ctx.message.server.members
        else:
            server_roles = ctx.message.server.roles
            role=[x for x in server_roles if x.mention==role_id]
            if len(role)==0:
                await self.bot.say("{}, This role does not exist! To tip a single user, use {}tip command instead.".format(ctx.message.author.mention,self.prefix))
                return
            else:
                for user in ctx.message.server.members:
                    if role[0] in user.roles:
                        users_list.append(user)       

        if role_id=="all":
            online_users = [x for x in users_list]
        else:
            online_users = [x for x in users_list if x.status == discord.Status.online]

        if ctx.message.author in online_users:
            online_users.remove(ctx.message.author)

        online_users=[x for x in online_users if x.bot==False]

        if self.use_max_recipients:
            len_receivers = min(len(online_users), self.soak_max_recipients)
        else:
            len_receivers = len(online_users)

        if self.use_min_received:
            len_receivers = min(len_receivers, amount / self.soak_min_received)

        if len_receivers == 0:
            await self.bot.say("{}, you are all alone if you don't include bots! Trying soaking when people are online.".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len_receivers) / 1e8
        if amount_split == 0:
            await self.bot.say("{} **:warning:{} is not enough to split between {} users:warning:**".format(ctx.message.author.mention, amount, len_receivers))
            return

        if role_id != "all" and role_id!="@everyone" and role_id!="@here":
            receivers = []
            for i in range(len_receivers):
                user = random.choice(online_users)
                receivers.append(user)
                online_users.remove(user)
                mysql.check_for_user(user.id)
                mysql.add_tip(snowflake, user.id, amount_split)

            long_soak_msg = "{} **Soaked {} {} on {} [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), self.currency_symbol, ', '.join([x.mention for x in receivers]), str(amount))

            if len(long_soak_msg) > 2000:
                await self.bot.say("{} **Soaked {} {} on {} users [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), self.currency_symbol, len_receivers, str(amount)))
            else:
                await self.bot.say(long_soak_msg)
        else:
            await self.bot.say("{} **Soaked {} {} on {} users [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), self.currency_symbol, len_receivers, str(amount)))

    @commands.command()
    async def soak_info(self):        
        if self.use_max_recipients:
            st_max_users = str(self.soak_max_recipients)
        else:
            st_max_users = "<disabled>"

        if self.use_min_received:
            st_min_received = str(self.soak_min_received)
        else:
            st_min_received = "<disabled>"
            
        await self.bot.say("Soak info: max recipients {}, min amount receivable {}".format(st_max_users, st_min_received))

def setup(bot):
    bot.add_cog(Soak(bot))
