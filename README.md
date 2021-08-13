# Eval Bot
A small discord bot to interface with [python-discord's](https://github.com/python-discord/)
[snekbox](https://github.com/python-discord/snekbox/).

This bot simply extracts the relevant functionality from [Python Discord's bot](https://github.com/python-discord/bot).

# Usage
To use this bot, you need to set up the following environment variables (you can use .env):

| Token        | Value  | Description                                                                              |
|--------------|--------|------------------------------------------------------------------------------------------|
| BOT_TOKEN    | str    | The discord token for your bot.                                                          |
| ADMINS       | int    | The ID of the "admins" role, which is used in certain permission checks.                 |
| MODS         | int    | The ID of the "mods" role, which is used in certain permission checks.                   |
| CHANNELS     | [int]  | A comma separated list of IDs for channel in which commands are enabled.                 |
| SNEKBOX_URL  | str    | The URL to use for API requests to snekbox. Should include the /eval portion of the URL. |
| PASTEBIN_URL | str    | The URL to use for pastebin. Of the shape: "<YOUR URL>/{key}" ({key} is a constant)      |
| TRASHCAN     | str    | An emoji to use as the "trashcan". Of the shape: <:trashcan:637136429717389331>          |


The following variables can optionally be set:

| Token          | Value | Description                                                                      |
|----------------|-------|----------------------------------------------------------------------------------|
| BOT_SENTRY_DSN | str   | To be used when logging in to sentry.                                            |
| LOG_FILTER     | str   |                                                                                  |
| BOT_PREFIX     | str   | An optional prefix to use for the bot. By default, only mentions will invoke it. |
