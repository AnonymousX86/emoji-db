# -*- coding: utf-8 -*-
from os import listdir, sep
from os.path import realpath

from flask import Flask, Response, jsonify, send_file
from werkzeug.exceptions import HTTPException


class EmojiNotFound(HTTPException):
    code = 404
    description = 'Emoji does not exist.'


if __name__ == '__main__':
    app = Flask(__name__)
    path = f'{realpath(__file__)}assets{sep}img'.replace(
        '__main__.py', ''
    )

    def all_emoji_files_names() -> list[str]:
        return listdir(path)

    def remove_ext(file_name: str) -> list[str, str]:
        return list(file_name[::1].split('.', maxsplit=1)[::1])

    def remove_ext_from_list(files_list: list[str]) -> list[str]:
        return list(map(lambda f: remove_ext(f)[0], files_list))

    def emoji_files(emoji_id: str) -> list[str]:
        return list(filter(
            lambda e: e.startswith(emoji_id),
            all_emoji_files_names())
        )
    
    def emoji_exts(emoji_id: str) -> list[str]:
        return list(map(lambda e: remove_ext(e)[1], emoji_files(emoji_id)))

    def all_emoji_ids():
        return list(set(remove_ext_from_list(all_emoji_files_names())))

    @app.route('/')
    def home() -> Response:
        return jsonify({'data': 'Hello world!'})

    @app.route('/emoji')
    def emoji_index() -> Response:
        return jsonify({'data': [e for e in all_emoji_ids()]})
    
    @app.route('/emoji/meta/<emoji_id>')
    def emoji_meta_by_id(emoji_id: str) -> Response:
        if emoji_id not in all_emoji_ids():
            raise EmojiNotFound
        return jsonify({'data': {
            'id': emoji_id,
            'extensions': emoji_exts(emoji_id),
            'sizes': ['112', '112']
        }})
    
    @app.route('/emoji/<emoji_id>')
    def emoji_by_id(emoji_id: str) -> Response:
        if emoji_id not in all_emoji_ids():
            raise EmojiNotFound
        exts = emoji_exts(emoji_id)
        for ext in ['webp', 'png', 'gif', 'jpeg', 'jpg']:
            if ext in exts:
                return send_file(f'{path}{sep}{emoji_id}.{ext}')
        app.aborter(500, description='Emoji exists, but is badly configured.')
    
    @app.route('/emoji/<emoji_id>.<emoji_ext>')
    def emoji_qualified(emoji_id: str, emoji_ext: str) -> Response:
        if emoji_id not in all_emoji_ids():
            raise EmojiNotFound
        elif emoji_ext not in emoji_exts(emoji_id):
            return app.redirect(f'/emoji/{emoji_id}')
        return send_file(f'{path}{sep}{emoji_id}.{emoji_ext}')

    app.run(debug=True)
