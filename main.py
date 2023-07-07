import os.path

import requests
from flask import Flask, request
from markdown_it import MarkdownIt

from makeprompt import make_prompt


app = Flask(__name__)
md = (MarkdownIt('commonmark', {'breaks': True, 'html': True, 'linkify': True}).disable('code'))

host = f'http://localhost:5000/api/v1/generate'
stream_host = f'ws://localhost:5005/api/v1/stream'


async def create_page(path: str, canonpath: str):
    global host
    os.makedirs(os.path.dirname(canonpath), exist_ok=True)

    prompt, start, end, stop = make_prompt(path)

    request = {
        'prompt': prompt,
        'max_new_tokens': 1024,

        'do_sample': True,

        'seed': -1,
        'add_bos_token': False,
        'truncation_length': 2048,
        'ban_eos_token': True,
        'skip_special_tokens': True,
        'stopping_strings': [stop]
    }

    response = requests.post(host, json=request)

    if response.status_code == 200:
        result = md.render(response.json()['results'][0]['text'])
        page = start + result + end
        with open(canonpath, 'w', encoding='utf8') as f:
            f.write(page)
        return page
    return "Something went wrong during generation!", 500


async def get_if_exists_else_create(path: str, new: bool):
    canonpath = os.path.join('pages', path)
    if os.path.isfile(canonpath) and not new:
        return open(canonpath, 'r', encoding='utf8')
    else:
        return await create_page(path, canonpath)


@app.route('/<path:path>')
async def route_path(path: str):
    new = request.args.get("new")
    if not '.' in path:
        path = path + '.html'
    if path.endswith('.html'):
        return await get_if_exists_else_create(path, new)
    else:
        try:
            return open(os.path.join('static', path), 'r', encoding='utf8')
        except:
            return 'Page not found', 404


@app.route('/')
async def home():
    new = request.args.get("new")
    return await get_if_exists_else_create('index.html', new)


def start(h, sh, port):
    app.run(port=port)
    global host, stream_host
    host = h
    stream_host = sh


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--host', default='localhost:5000')
    parser.add_argument('--stream_host', default='localhost:5005')
    parser.add_argument('--port', default='9898')

    args = parser.parse_args()

    url = f'http://{args.host}/api/v1/generate'
    stream_url = f'ws://{args.stream_host}/api/v1/stream'
    start(url, stream_url, args.port)
