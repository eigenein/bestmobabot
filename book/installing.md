# Запуск

В любом случае, вам понадобится конфиг. Детально про него можно почитать в [разделе с настройкой](configuring/README.md). Создайте текстовый файл `settings.yaml`. Минимально понадобятся такие настройки:

```yaml
vk:
  remixsid: ...  # значение cookie `remixsid` с вашего аккаунта на VK.com.
  access_token: ...  # создайте приложения на VK.com и скопируйте сюда сервисный ключ доступа
bot:
  arena: {}
```

Далее самый простой вариант запуска – это использование [Docker](https://www.docker.com/). С каждым обновлением бота я собираю публикую [готовый образ](https://hub.docker.com/r/eigenein/bestmobabot). Можно, конечно, и без Docker, но про это напишу позже.

## Docker

Команда для запуска выглядит примерно так:

```bash
docker run \
    --rm \
    --name bestmobabot \
    -it \
    -e TZ=Europe/Amsterdam \
    -v /Users/eigenein/GitHub/bestmobabot/settings.yaml:/app/settings.yaml:ro \
    -v /Users/eigenein/GitHub/bestmobabot/db.sqlite3:/app/db.sqlite3:rw \
    eigenein/bestmobabot -v
```

Вам нужно изменить пути к файлам на ваши собственные и указать верный часовой пояс. 
