# URL Generator

## Introduction
This project contains a VERY SIMPLE REST API service that can generate short URLs for URLs of any size, and retrieve back the original URL from a shortened one. 

Just for clarification, the project does not contain the frontend as offered by companies like bit.ly or ow.ly.

There are numerous ways to improve the project, being the most notable:
* switching from Flask to FastAPI, which offers better performance and paralellism
* switching from a local file-based database like SQLite3 to a key-value store like Redis or AWS DynamoDB
* Use the container provided to offer the API through a service with resource elasticity, like Kubernetes or Amazon EKS, setting a Load Balancer in front.

## Environment
The code and tests have been developed using Python, and assume an existing installation of python3 and pip3 in the system. To generate the adequate environment, execute:
```
CD into the folder containing the source code ("src" folder)

python3 -m venv my_venv

source my_venv/bin/activate

pip3 install -r requirements.txt
```

## Testing
A small set of unit tests has been generated to make sure the basic functionalities are working fine. To execute the test, execute:

```
CD into the folder containing the source code ("src" folder)

python -m unittest
```

## Execution
There are two ways to execute the API server.

### Simple execution
For a very simple, debug-oriented, server, just execute: 

```
CD into the folder containing the source code ("src" folder)

python3 main.py
```

### More robust execution
A working docker environment is necessary for the steps described in this section. A Dockerfile is provided to build and execute the server as a docker container. 

First of all, build the docker image:

```
CD into the project root folder, that contains the Dockerfile file.

docker build -t url_shortener:1.0 ./
```

You can change the name "url_shortener" and the version "1.0" to whatever you may prefer, just remember to use it as the docker image name in the following steps.

Then, to execute the container, run:

```
docker run -d -p 5000:80 -v short_urls_db:/app/db --rm url_shortener:1.0
```

where:

* -p 5000:80 connects port 80 in the container to your local port 5000. You can choose any other local port of your preference.
* -v short_urls_db:/app/db creates a docker volume that stores the database making it persistent along container executions. The container can be run without this parameter but in that case the database will start empty every time the container is run.
* --rm causes the container to be deleted after being stopped, just to tidy up the environment. It is optional.





