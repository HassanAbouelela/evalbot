from discord import AllowedMentions, Game, Intents
from discord.ext import commands

from bot import Bot, constants
from bot.log import setup_sentry

setup_sentry()

# Set up default bot settings
INTENTS = Intents.default()

if constants.bot_prefix is not None:
    prefix = commands.when_mentioned_or(constants.bot_prefix)
else:
    prefix = commands.when_mentioned


bot = Bot(
    command_prefix=prefix,
    case_insensitive=True,
    activity=Game(name="Python 3.10 Eval"),
    allowed_mentions=AllowedMentions(everyone=False),
    intent=INTENTS,
    max_messages=1_000
)


bot.load_extension("bot.exts.error_handler")
bot.load_extension("bot.exts.internal")
bot.load_extension("bot.exts.snekbox")


bot.run(constants.BOT_TOKEN)
