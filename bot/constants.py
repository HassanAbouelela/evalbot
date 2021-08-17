import os

try:
    import dotenv
    dotenv.load_dotenv()
except ModuleNotFoundError:
    print("Not loading .env, since dotenv is not available.")
    pass


BOT_TOKEN = os.environ.get("BOT_TOKEN", None)

if BOT_TOKEN is None:
    raise ValueError("Bot token is not defined, can not start bot.")

admin_role = int(os.environ.get("ADMINS", 267628507062992896))
mod_role = int(os.environ.get("MODS", 267629731250176001))
channels = [int(channel) for channel in os.environ.get("CHANNELS", "563594791770914816").split(",")]
SNEKBOX_URL = os.environ.get("SNEKBOX_URL", "http://snekbox.default.svc.cluster.local/eval")
PASTEBIN = os.environ.get("PASTEBIN_URL", "https://paste.pythondiscord.com/{key}")
TRASHCAN = os.environ.get("TRASHCAN", "<:trashcan:637136429717389331>")

DEBUG_MODE = os.environ.get("DEBUG", "false").lower() == "true"
sentry_dsn = os.environ.get("BOT_SENTRY_DSN", None)
GIT_SHA = os.environ.get("GIT_SHA", "development")
log_filter = os.environ.get("LOG_FILTER", None)
bot_prefix = os.environ.get("BOT_PREFIX", None)
