import logging

from discord.ext.commands import Context

from bot import constants

log = logging.getLogger(__name__)

# Set up a string of channel mentions for the error message.
__CHANNELS = ""
for channel in constants.channels:
    __CHANNELS += f"<#{channel}>, "
__CHANNELS = __CHANNELS.strip(" ,")
CHANNEL_ERROR_MESSAGE = f"You can only use this command in the following channel(s): {__CHANNELS}"


async def check_whitelist(ctx: Context) -> bool:
    """
    Ensure a command can only be invoked in a whitelisted context.

    Return True if a command should exit early.
    """
    if ctx.channel.id not in constants.channels:
        if any(role.id in [constants.admin_role, constants.mod_role] for role in ctx.author.roles):
            log.debug(f"{ctx.author} bypassed the channel check, since they have a whitelisted role.")
            return False
        else:
            log.debug(f"Command invocation blocked for {ctx.author}, since they are not in a whitelisted context.")
            await ctx.send(CHANNEL_ERROR_MESSAGE)
            return True
