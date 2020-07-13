# repo-builder

## What?

Pulls and builds any git repo with a working docker file. Then pushes the dockerfile to a docker repo

#### Setup:

Rename `docker_creds.example.py` to `docker_creds.py` and fill in docker repo credentials

#### Running locally:

`python3 -m venv venv`

`. venv/bin/activate`

`pip install -r requirements.txt`

`flask run`

#### Running in docker:

`docker build -t pybuild .`

`docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock pybuild`

##### Usage:

tag = tagname for docker repo

git_repo = https url to clone repo

`GET http://localhost:5000/build?t={tag}&git_repo={repo_url}`

Example:
`GET http://localhost:5000/build?t=testing123&git_repo=https://github.com/docker-hy/docker-hy.github.io.git`
