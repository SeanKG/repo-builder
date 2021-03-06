import os
import git
import shutil
import tarfile
import requests_unixsocket
import requests
import json
from docker_creds import creds
import base64
from flask import Flask, jsonify, stream_with_context, request, Response

requests_unixsocket.monkeypatch()
app = Flask(__name__)

auth_header = base64.b64encode(json.dumps(creds).encode()).decode()

def docker_get(path='info'):
    print(path)
    return requests.get(docker_url(path))

def rm(path):
    try:
        shutil.rmtree(path)
    except:
        pass

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def local(path):
    return os.path.join(os.getcwd(), path)

def docker_url(path):
    return 'http+unix://%2Fvar%2Frun%2Fdocker.sock/' + path

def _id(id):
    return 'id: {}\n\n'.format(id)

def _data(dat):
    return 'data: {}\n\n'.format(json.dumps(dat) if isinstance(dat, dict) else dat)

def _section(name):
    yield _id(name)
    yield _data({'stream': name})

def _clone():
    yield from _section('cloning')
    repo_dir = local('repo')
    rm(repo_dir)
    git.Repo.clone_from(request.args['git_repo'], repo_dir, branch='master')
    yield from _section('compressing')
    make_tarfile(local('repo.tar.gz'), repo_dir + '/')

def _build():
    headers = {
        'Content-Type': 'application/tar'
    }
    r = requests.post(
        docker_url('build') + '?' + request.query_string.decode(),
        headers = headers,
        data = open(local('repo.tar.gz'), 'rb').read(),
        stream=True
    )
    yield from _section('building')
    for line in r.iter_lines():
        print(line)
        yield _data(line.decode())
    yield _data({ 'stream': 'done!'})

def _tag():
    yield from _section('tagging')
    name = request.args['t']
    url = docker_url('images/{}/tag'.format(name))
    qs = '?repo={}/{}'.format(creds['username'], name)
    print(name)
    print(url + qs)
    requests.post(url + qs)

def _push():
    yield from _section('pushing')
    name = request.args['t']
    url = docker_url('images/{}/{}/push'.format(creds['username'], name))
    print(url)
    requests.post(url, headers={'X-Registry-Auth': auth_header})

def work():
    yield from _section('starting!')
    yield from _clone()
    yield from _build()
    yield from _tag()
    yield from _push()
    yield from _section('DONE!')
    
@app.route('/build')
def build():
    if 'Last-Event-ID' in request.headers:
        # Hacky way to close the event stream when it tries to reconnect
        return '', 204
    return Response(stream_with_context(work()), mimetype="text/event-stream")

@app.route('/clone')
def clone():
    _clone()
    return local('')

@app.route('/docker/<path:docker_path>')
def docker(docker_path):
    return jsonify(docker_get(docker_path).json())
