The bot playing [Hero Wars](https://vk.com/app5327745) MOBA-like game on [VK.com](https://vk.com).

### Running with Docker Compose

```bash
mkdir -p /srv/bestmobabot
docker-compose up -d
```

#### `docker-compose.yml`

```yaml
version: "3.3"
services:
  bestmobabot-user-1:
    image: eigenein/bestmobabot
    restart: always
    environment:
      - BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie-1
      - BESTMOBABOT_LOGFILE=/srv/bestmobabot/bestmobabot-user-1.log
      - BESTMOBABOT_NO_EXPERIENCE=true
      - BESTMOBABOT_RAID=16 3 57 3
      - BESTMOBABOT_SHOP=1 4 1 5
      - BESTMOBABOT_TRAINER=true
      - BESTMOBABOT_VK_TOKEN=VK.com-API-token
      - BESTMOBABOT_ARENA_OFFSET=3600
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
  bestmobabot-user-2:
    image: eigenein/bestmobabot
    restart: always
    environment:
      - BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie-2
      - BESTMOBABOT_LOGFILE=/srv/bestmobabot/bestmobabot-user-2.log
      - BESTMOBABOT_NO_EXPERIENCE=false
      - BESTMOBABOT_VK_TOKEN=VK.com-API-token
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
```

### Trainer

Arena model trainer could be run manually via:

```bash
python -m bestmobabot.trainer -v
```

Trained model is then saved back to the database.

### Storage

SQLite database is used as a sort of key-value store to preserve state between restarts:

* Arena and grand arena battles
* Authentication credentials
* API session
* Picked up gifts
* Arena win probability prediction model
