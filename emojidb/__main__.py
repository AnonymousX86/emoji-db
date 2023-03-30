# -*- coding: utf-8 -*-
from logging import INFO, basicConfig, getLogger
from pathlib import Path

from flask import Flask, Response, jsonify, send_file
from rich.logging import RichHandler
from werkzeug.exceptions import NotFound


class EmojiNotFound(NotFound):
    description = 'Emoji does not exist.'


app = Flask(__name__)

IMG_FOLDER = Path.cwd().joinpath('assets', 'img')


def all_emoji_files() -> list[Path]:
    return [d for d in IMG_FOLDER.iterdir()]


def split_ext(file_name: str) -> list[str, str]:
    """Return a list of file name (which is also its ID) and its extension.

    :param file_name: File full name. For example: "image.webp".
    :return: List of file name and its extension.
             For example: ["image", "webp"].
    """
    return list(file_name[::1].split('.', maxsplit=1)[::1])


def all_emoji_ids() -> list[str]:
    return [split_ext(file.name)[0] for file in all_emoji_files()]


@app.route('/')
def home() -> Response:
    # TODO Log app info?
    return jsonify({'data': 'Hello world!'})


@app.route('/emoji')
def emoji_index() -> Response:
    return jsonify({'data': [e for e in all_emoji_ids()]})


@app.route('/emoji/<emoji_id>')
def emoji_by_id(emoji_id: str) -> Response:
    if emoji_id not in all_emoji_ids():
        raise EmojiNotFound
    for ext in ['webp', 'png', 'gif', 'jpeg', 'jpg']:
        breakpoint()
        if (emoji := IMG_FOLDER.joinpath(f'{emoji_id}.{ext}')).exists():
            return send_file(emoji)
    app.aborter(500, description='Emoji exists, but is badly configured.')


if __name__ == '__main__':
    basicConfig(
        level=INFO,
        format='%(message)s',
        datefmt='[%x]',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    getLogger(app.name).setLevel(INFO)
    getLogger('werkzeug').setLevel(INFO)
    app.run()
