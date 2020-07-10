import os
import git
import shutil
import tarfile
import requests_unixsocket
import requests
from flask import Flask, jsonify

requests_unixsocket.monkeypatch()
app = Flask(__name__)

git_repo = 'git@github.com:SeanKG/docker-hy.github.io.git'

@app.route('/')
def clone():
    repo_dir = local( 'repo')
    rm(repo_dir)
    git.Repo.clone_from(git_repo, repo_dir, branch='master')
    make_tarfile(local('repo.tar.gz'), repo_dir)
    return local('')

@app.route('/info')
def info():
    r = docker_get()
    return r.json()

@app.route('/docker/<path:docker_path>')
def docker(docker_path):
    return jsonify(docker_get(docker_path).json())

def docker_get(path='info'):
    print(path)
    return requests.get('http+unix://%2Fvar%2Frun%2Fdocker.sock/' + path)

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


