import discord
from discord import AllowedMentions, Game, Intents
from discord.ext import commands

from bot import Bot, constants
from bot.log import setup_sentry

setup_sentry()

# Set up a string of channel mentions for the error message.
CHANNELS = ""
for channel in constants.channels:
    CHANNELS += f"<#{channel}>, "
CHANNELS = CHANNELS.strip(" ,")
ERROR_MESSAGE = f"You can only use this command in the following channel(s): {CHANNELS}"

# Set up default bot settings
INTENTS = Intents.default()

if constants.bot_prefix is not None:
    prefix = commands.when_mentioned_or(constants.bot_prefix)
else:
    prefix = commands.when_mentioned


bot = Bot(
    command_prefix=prefix,
    case_insensitive=True,
    activity=Game(name=f"Python 3.10 Eval"),
    allowed_mentions=AllowedMentions(everyone=False),
    intent=INTENTS,
    max_messages=1_000
)


# Add a listener to prevent DM invocations, or invocations in non-approved channels
async def on_message(message: discord.Message) -> None:
    if message.author.bot:
        return

    if message.guild is None:
        await message.author.send(ERROR_MESSAGE)
    elif (
        constants.admin_role not in [role.id for role in message.author.roles]
        and message.channel.id not in constants.channels
        and not message.content.lstrip(constants.bot_prefix).startswith("help")
    ):
        await message.channel.send(ERROR_MESSAGE)
    else:
        await bot.process_commands(message)

    return

bot.on_message = on_message


bot.load_extension("bot.exts.error_handler")
bot.load_extension("bot.exts.internal")
bot.load_extension("bot.exts.snekbox")


bot.run(constants.BOT_TOKEN)
