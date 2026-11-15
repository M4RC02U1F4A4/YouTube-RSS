# YouTube-RSS

## Description

This service is an alternative to YouTube's subscription page. You can decide which videos you want to keep and which videos you want to remove, giving you a list of content you want to watch.

![](img/home.png)

## Requirements

To get started, you will need to create a Google Cloud account, create a project, enable the `YouTube Data API v3` and generate a key.

## Installation

1. Download the `docker-compose.yml` file in the folder you want to use

    ```shell
    wget https://raw.githubusercontent.com/M4RC02U1F4A4/YouTube-RSS/main/docker-compose.yml
    ```

2. Set your API key in `G_API_KEY` in the `docker-compose.yml` file
3. Deploy the application

    ```
    docker compose up -d
    ```
4. You can now access the service on `http://127.0.0.1:8080`

## Scheduled jobs

The app does not schedule anything by itself: the `updater` service in `docker-compose.yml` calls these endpoints with cron.

| Endpoint | Schedule | What it does |
|---|---|---|
| `GET /update/videos` | every hour | Imports new videos from the channels' RSS feeds |
| `GET /update/channels` | once a day | Refreshes channel names, logos and counters |
| `GET /clean/videos` | once a day | Deletes videos watched more than 30 days ago |

On Kubernetes you can drop the `updater` and use a CronJob per endpoint instead, for example:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: ytrss-update-videos
spec:
  schedule: "0 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: update
              image: alpine
              command: ["wget", "-q", "-O", "-", "http://ytrss:8080/update/videos"]
```

Each `/update` call uses YouTube API quota, so avoid running them much more often than this.

## Development

The UI is a single static page, `app/static/index.html`, served by the Flask app together with the API. There is no build step.

To run the API checks you need a throwaway MongoDB:

```shell
docker run -d --rm -p 27017:27017 --name ytrss-test mongo
cd app && pip install -r requirements.txt
MONGODB_HOST=localhost MONGODB_PORT=27017 python test_main.py
```

## Releases

Every push to `main` is a release. `.github/workflows/release.yml` takes the latest version tag and bumps it once for each commit after it, read from the [Conventional Commits](https://www.conventionalcommits.org/) subject: `type!:` is major, `feat:` minor, anything else patch. It then publishes `ghcr.io/m4rc02u1f4a4/ytrss:<version>` and `:latest` for `linux/amd64` and `linux/arm64`, pushes the tag and writes the GitHub Release from the commit subjects. So the commit type decides the version number: use `feat:` only for something users can now do or see.

| Workflow | When | What |
|---|---|---|
| `release.yml` | every push to `main` | version, image, tag, GitHub Release |
| `verify.yml` | pull requests and pushes that touch `app/` | `test_main.py` against MongoDB, image build and smoke test; publishes nothing |
| `build-test.yml` | by hand, any branch | publishes `ytrss:dev` |
| `check_pr.yml` | pull requests | the title must be a Conventional Commit |
