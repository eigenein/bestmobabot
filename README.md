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
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
```
