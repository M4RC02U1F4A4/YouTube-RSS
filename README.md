# YouTube-RSS

## Description

This service is an alternative to YouTube's subscription page. You can decide which videos you want to keep and which videos you want to remove, giving you a list of content you want to watch.

![](img/home.png)
## Requirements

To get started, you will need to create a Google Cloud account, create a project, enable the `YouTube Data API v3` and generate a key.

## Installation

> In both steps, it is necessary to change the environment variables contained in the respective docker-compose files

There are two docker-compose files suggested by this project:
 - `docker-compose.yml` -> Uses the latest stable release taken directly from Docker Hub

For this method, all you need to do is download the `docker-compose.yml` file and run it with `docker-compose up -d`, then you can access the service from http://127.0.0.1.

- `docker-compose_build.yml` -> Build the project directly from the latest commit in the repo

For this method, you need to clone the repo and start the containers with the command `docker-compose -f docker-compose_build.yml up --build -d`, then you can access the service from http://127.0.0.1.


