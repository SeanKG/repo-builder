import os
import git
import shutil
import tarfile
import requests_unixsocket
import requests
from flask import Flask, jsonify, stream_with_context, request, Response

requests_unixsocket.monkeypatch()
app = Flask(__name__)

git_repo = 'https://github.com/SeanKG/docker-hy.github.io.git'

@app.route('/clone')
def clone():
    repo_dir = local('repo')
    rm(repo_dir)
    git.Repo.clone_from(git_repo, repo_dir, branch='master')
    make_tarfile(local('repo.tar.gz'), repo_dir + '/')
    return local('')

@app.route('/build')
def build():
    def generate():
        headers = {
            'Content-Type': 'application/tar'
        }
        r = requests.post(
            docker_url('build') + '?' + request.query_string.decode(),
            headers = headers,
            data = open(local('repo.tar.gz'), 'rb').read(),
            stream=True
        )
        for line in r.iter_lines():
            print(line)
            yield line.decode() + '\n'
    return Response(stream_with_context(generate()))

@app.route('/push')
def push():

    return ''

@app.route('/docker/<path:docker_path>')
def docker(docker_path):
    return jsonify(docker_get(docker_path).json())

def docker_get(path='info'):
    print(path)
    return requests.get(docker_url(path))

def rm(path):
    try:
        shutil.rmtree(path)
    except:
        pass

def local(path):
    return os.path.join(os.getcwd(), path)

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def docker_url(path):
    return 'http+unix://%2Fvar%2Frun%2Fdocker.sock/' + path