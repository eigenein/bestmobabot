### Running

#### Docker

```sh
mkdir -p /srv/bestmobabot
echo 'BESTMOBABOT_REMIXSID=VK.com-remixsid-cookie' > .env

docker build -t eigenein/bestmobabot .
docker-compose up -d
```
