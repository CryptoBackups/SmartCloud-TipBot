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
        active_users = mysql.get_active_users_id(RAIN_REQUIRED_USER_ACTIVITY_M, True)
        if int(ctx.message.author.id) in active_users:
            output.info("Message user found in active users list. Removing "+str(ctx.message.author.id))
            active_users.remove(int(ctx.message.author.id))

        if USE_MAX_RECIPIENTS:
            len_receivers = min(len(active_users), MAX_RECIPIENTS)
        else:
            len_receivers = len(active_users)

        if len_receivers == 0:
            await self.bot.say("{}, you are all alone if you don't include bots! Trying raining when people are online and active.".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len_receivers) / 1e8
        if amount_split == 0:
            await self.bot.say("{} **:warning:{} is not enough to split between {} users:warning:**".format(ctx.message.author.mention, amount, len_receivers))
            return    

        receivers = []
        for i in range(len_receivers):
            active_user = random.choice(active_users)
            user=await self.bot.get_user_info(active_user)
            receivers.append(user.mention)
            active_users.remove(active_user)
            mysql.check_for_user(user.id)
            mysql.add_tip(snowflake, user.id, amount_split)

        long_soak_msg = "{} **Rained {} {} on {} [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), CURRENCY_SYMBOL, ', '.join([x for x in receivers]), str(amount))

        if len(long_soak_msg) > 2000:
            await self.bot.say("{} **Rained {} {} on {} users [{}] :moneybag:**".format(ctx.message.author.mention, str(amount_split), CURRENCY_SYMBOL, len_receivers, str(amount)))
        else:
            await self.bot.say(long_soak_msg)

    #     users_to_tip = list(set(users_to_tip))
    #     if len(users_to_tip) < 1:
    #         raise util.TipBotException("no_valid_recipient")
    #     if int(amount / len(users_to_tip)) < 1:
    #         raise util.TipBotException("invalid_tipsplit")
    #     user = db.get_user_by_id(message.author.id, user_name=message.author.name)
    #     if user is None:
    #         return
    #     balance = await wallet.get_balance(user)
    #     user_balance = balance['available']
    #     if user_balance < amount:
    #         await add_x_reaction(message)
    #         await post_dm(message.author, INSUFFICIENT_FUNDS_TEXT)
    #         return
    #     # At this point stash this as the last rain for this user
    #     if message.author.id not in last_rains:
    #         last_rains[message.author.id] = datetime.datetime.utcnow()
    #     else:
    #         rain_delta = (datetime.datetime.utcnow() - last_rains[message.author.id]).total_seconds()
    #         if RAIN_COOLDOWN > rain_delta:
    #             await post_dm(message.author, "You can rain again in {0:.2f} seconds", RAIN_COOLDOWN - rain_delta)
    #             return
    #     last_rains[message.author.id] = datetime.datetime.utcnow()
    #     # Distribute Tips
    #     tip_amount = int(amount / len(users_to_tip))
    #     # Recalculate actual tip amount as it may be smaller now
    #     real_amount = tip_amount * len(users_to_tip)
    #     # 1) Make all transactions first
    #     for member in users_to_tip:
    #         uid = str(uuid.uuid4())
    #         actual_amt = await wallet.make_transaction_to_user(user, tip_amount, member.id, member.name, uid)
    #     # 2) Add reaction
    #     await react_to_message(message, amount)
    #     await message.add_reaction('\U0001F4A6') # Sweat Drops
    #     # 3) Update tip stats
    #     db.update_tip_stats(user, real_amount,rain=True)
    #     db.mark_user_active(user)
    #     # 4) Send DMs (do this last because this takes the longest)
    #     for member in users_to_tip:
    #         if not db.muted(member.id, message.author.id):
    #             await post_dm(member, TIP_RECEIVED_TEXT, actual_amt, message.author.name, message.author.id)
    # except util.TipBotException as e:
    #     if e.error_type == "amount_not_found" or e.error_type == "usage_error":
    #         await post_usage(message, RAIN)
    #     elif e.error_type == "no_valid_recipient":
    #         await post_dm(message.author, RAIN_NOBODY)
    #     elif e.error_type == "invalid_tipsplit":
    #         await post_dm(message.author, TIPSPLIT_SMALL)  
def setup(bot):
    bot.add_cog(Rain(bot))
