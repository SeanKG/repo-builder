# repo-builder

`python3 -m venv venv`
`. venv/bin/activate`

`docker build -t pytest .`

`docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock pytest`

