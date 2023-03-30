# -*- coding: utf-8 -*-
from hashlib import md5
from logging import INFO, basicConfig, getLogger
from os import getenv
from pathlib import Path

from discord import Intents, Embed, Option, ApplicationContext, Color
from discord.ext.commands import Bot, Context
from requests import get as requests_get
from rich.logging import RichHandler

IMG_FOLDER = Path.cwd().joinpath('assets', 'img')


def name_parse(name: str) -> str:
    return name.replace('-', '_').replace(' ', '_')[:16]


def checksum_lookup(content: bytes) -> tuple[bool, Path or None]:
    """Checks if file exists but under different name.

    :param content: Binary content of a file.
    :return: If file exists 'True' with file's path,
    or 'False' and None if it doesn't exist.
    """
    new_checksum = md5(content).hexdigest()
    for dir_ in IMG_FOLDER.iterdir():
        with open(dir_, 'br') as file:
            if new_checksum == md5(file.read()).hexdigest():
                return True, dir_
    return False, None


class EmojiMeta:
    def __init__(self, emoji_raw: str):
        emoji_raw = emoji_raw[1:-1].split(':')
        self.format: str = 'gif' if emoji_raw[0] == 'a' else 'png'
        self.name: str = name_parse(emoji_raw[1])
        self.id: int = int(emoji_raw[2])

    @property
    def url(self) -> str:
        return f'https://cdn.discordapp.com/emojis/{self.id}' \
               f'.{self.format}'

    @property
    def path(self) -> Path:
        return IMG_FOLDER.joinpath(f'{self.name}.{self.format}')

    def update_name(self, new_name: str):
        self.name = name_parse(new_name)


def main() -> None:
    rich_log = getLogger('rich')

    if not (token := getenv('BOT_TOKEN')):
        raise RuntimeError('Please set "BOT_TOKEN" environment variable')

    bot = Bot(intents=Intents.default())

    @bot.event
    async def on_ready() -> None:
        rich_log.info(f'Logged in as "{bot.user}"')
        await bot.sync_commands()
        rich_log.info('Commands synced')

    @bot.slash_command(
        name='upload',
        description='Yoinks emoji from Discord.'
    )
    async def upload_emoji(
            ctx: ApplicationContext,
            emoji_raw: Option(
                str,
                'Just emoji',
                name='emoji',
                required=True
            ),
            emoji_name: Option(
                str,
                'Optional name of emoji. Preferred "snake_case" If not'
                ' present emoji name will be used.',
                name='emoji_name',
                max_length=16,
                default=None,
                required=False
            )
    ):
        # noinspection GrazieInspection
        """Emoji uploader.

        :type ctx: Context
        :type emoji_raw: str
        :type emoji_name: str or None
        """
        await ctx.send_response(embed=Embed(
            description='Fetching emoji...',
            color=Color.blurple()
        ))
        emoji = EmojiMeta(emoji_raw)
        if emoji_name is not None:
            emoji.update_name(emoji_name)
        filename = IMG_FOLDER.joinpath('{0.name}.{0.format}'.format(emoji))
        if filename.exists():
            await ctx.edit(
                embed=Embed(
                    description=f'`{emoji.name}` already exists.',
                    color=Color.blurple()
                ).add_field(
                    name='Link',
                    value='*[Click](https://youtu.be/dQw4w9WgXcQ'
                          ' "Just click, don\'t think too much")*'
                ).set_thumbnail(
                    url=emoji.url
                )
            )
            return
        await ctx.edit(embed=Embed(
            description='Downloading from friends server...',
            color=Color.blurple()
        ))
        res = requests_get(emoji.url)
        if res.status_code != 200:
            await ctx.edit(embed=Embed(
                description="Friends' server is unavailable",
                color=Color.blurple()
            ))
            return
        checksum_exists, file_location = checksum_lookup(res.content)
        if checksum_exists:
            await ctx.edit(
                embed=Embed(
                    description=f'This emoji (`{emoji.name}`) already exists,'
                                f' but is named `{file_location.name}`'
                ).add_field(
                    name='Link',
                    value='*[Click](https://youtu.be/dQw4w9WgXcQ'
                          ' "Just click, don\'t think too much")*'
                ).set_thumbnail(
                    url=emoji.url
                )
            )
            return
        try:
            with open(filename, 'x'):
                pass
        except FileExistsError:
            pass
        finally:
            with open(filename, 'bw') as file:
                file.write(res.content)
        await ctx.edit(embed=Embed(
            description='Saved `{}kB` to `{}`.'.format(
                int(res.headers.get('Content-Length', 0)) // 1000,
                filename
            ),
            color=Color.blurple()
        ).add_field(
            name='Link',
            value='*[Click](https://youtu.be/dQw4w9WgXcQ'
                  ' "Just click, don\'t think too much")*'
        ).set_thumbnail(
            url=emoji.url
        ))
        rich_log.info(f'"{ctx.user.name}" downloaded "{filename}"')

    bot.run(token)


if __name__ == '__main__':
    basicConfig(
        level=INFO,
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    main()
