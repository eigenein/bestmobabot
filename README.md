### Running

```bash
# docker build -t eigenein/bestmobabot .

echo 'BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie' > .env
echo 'BESTMOBABOT_LOGFILE=/srv/bestmobabot/bestmobabot.log' >> .env
mkdir -p /srv/bestmobabot
docker-compose up -d
```

#### Multiple Instances

Prepare environment files for every user:

```bash
echo 'BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie-1' > user-1.env
echo 'BESTMOBABOT_LOGFILE=/srv/bestmobabot/bestmobabot-user-1.log' >> user-1.env

echo 'BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie-2' > user-2.env
echo 'BESTMOBABOT_LOGFILE=/srv/bestmobabot/bestmobabot-user-2.log' >> user-2.env
```

Change `docker-compose.yml` in a way like:

```yaml
version: "3.3"
services:
  bestmobabot-user-1:
    image: eigenein/bestmobabot
    restart: always
    env_file: user-1.env
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
  bestmobabot-user-2:
    image: eigenein/bestmobabot
    restart: always
    env_file: user-2.env
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
```

And then normally:

```bash
mkdir -p /srv/bestmobabot
docker-compose up -d
```
