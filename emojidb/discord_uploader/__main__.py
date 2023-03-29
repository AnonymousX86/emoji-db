# -*- codin: utf-8 -*-
from logging import INFO, basicConfig, getLogger
from os import getenv
from pathlib import Path

from discord import DiscordException, HTTPException, Intents, Message
from discord.ext.commands import Bot, Context, EmojiNotFound
from requests import get as requests_get
from rich.logging import RichHandler


def main() -> None:
    rich_log = getLogger('rich')
    intents = Intents.default()
    intents.message_content = True
    bot = Bot(
        command_prefix=';',
        help_command=None,
        intents=intents
    )

    @bot.event
    async def on_ready() -> None:
        rich_log.info(f'Logged in as "{bot.user}"')

    @bot.hybrid_command(
        name='upload',
        aliases=['up']
    )
    async def upload_emoji(ctx: Context, emoji_raw: str):
        msg: Message = await ctx.send('Fetching emoji...')
        is_animated, emoji_name, emoji_id = emoji_raw[1:-1].split(':')
        emoji_name = emoji_name.replace('-', '_')
        emoji_id = int(emoji_id)
        emoji_format = 'gif' if is_animated == 'a' else 'webp'
        emoji = bot.get_emoji(emoji_id)
        filename = Path.home().joinpath(
                'Downloads'
            ).joinpath(
                'Emoji DB Uploader'
            ).joinpath(
                '{}.{}'.format(emoji_name, emoji_format)
            )
        if not emoji:
            await msg.edit(content='Emoji unavailable, downloading from freinds server...')
            emoji_url = f' https://cdn.discordapp.com/emojis/{emoji_id}.' + \
                        f'{emoji_format}?size=128&quality=lossless'
            await ctx.send(content=f'`{emoji_name}`: {emoji_url}')
            res = requests_get(emoji_url)
            if not res.ok:
                await msg.edit("Firends' server is unavailable")
                return
            try:
                with open(filename, 'x'):
                    pass
            except FileExistsError:
                pass
            with open(filename, 'bw') as file:
                file.write(res.content)
            await msg.edit(content=f'Saved {int(res.headers.get("Content-Length", 0))//1000}kB.')
        else: 
            await msg.edit(content='Emoji found, downloading rfom OG servers...')
            try:
                bytes_saved: int = await emoji.save(filename)
            except EmojiNotFound:
                await msg.edit(content='Just kidding, emoji not found.')
            except DiscordException or HTTPException as e:
                await msg.edit(content=f'Saving failed because: ```diff\n- {e.__class__.__name__}:\n- {e}\n```')
            else:
                await msg.edit(content=f'Saved {bytes_saved//1000}kB.')

    if not (token := getenv('BOT_TOKEN')):
        raise RuntimeError('Please set "BOT_TOKEN" environment variable')

    bot.run(token)


if __name__ == '__main__':
    basicConfig(
        level=INFO,
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    main()
