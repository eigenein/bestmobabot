Bot playing a MOBA-like game on [VK.com](https://vk.com). The bot uses pure reverse-engineered Hero Wars JSON API. No Flash-emulator is used. No browser is needed.

### Settings

At the moment settings are described only in `settings.py`. Here is an example of `settings.yaml`:

```yaml
vk:
  remixsid: <VK.com `remixsid` cookie>
  access_token: <VK.com API access token>
bot:
  no_experience: no  # do not farm experience quests
  is_trainer: yes  # train arena prediction model nightly
  arena:
    schedule_offset: 01:00:00  # shift time from the default one
  friend_ids:
  - 123456789
  - 123456790
  shops:
  - Печать пастыря
  - Орион
  - Йорген
  - Зелье титана
  - Драконий щит - рецепт
  - Рука славы
  - Изначальное слово - рецепт
  raid_missions:
  - Чащоба Каданг
```

## Running with Docker

```bash
docker volume create bestmobabot
sudo nano /var/lib/docker/volumes/bestmobabot/_data/settings.yaml
docker run \
    --detach \
    --restart always \
    --name bestmobabot \
    -v bestmobabot:/app \
    -e TZ=Europe/Amsterdam
    eigenein/bestmobabot -v --settings settings.yaml
```

### `docker-compose.yml`

```yaml
version: '3.7'
services:
  bestmobabot:
    image: eigenein/bestmobabot:latest
    volumes:
    - 'bestmobabot:/app'
    - '/root/settings.yaml:/app/settings.yaml:ro'
    environment:
      TZ: 'Europe/Amsterdam'
      BESTMOBABOT_VERBOSITY: '1'
    restart: always
volumes:
  bestmobabot:
```

Or:

```yaml
version: '3.7'
services:
  bestmobabot:
    image: eigenein/bestmobabot:latest
    volumes:
    - '/root/bestmobabot.sqlite3:/app/db.sqlite3:rw'
    - '/root/settings.yaml:/app/settings.yaml:ro'
    environment:
      TZ: 'Europe/Amsterdam'
      BESTMOBABOT_VERBOSITY: '1'
    restart: always
volumes:
  bestmobabot:
```

You may also need to run `chown nobody:nogroup bestmobabot.sqlite3`.

## Tasks

Bot uses its own cron-like scheduler to perform game tasks. There're tasks that performed daily at particular time and there're periodic tasks that performed every N minutes/hours. They're spread over a day to decrease game API requests frequency.

Also, for expeditions the bot tries to pick up a reward and start the next expedition as soon as possible, given that the bot is not restarted in the meantime.

## Trainer

Trainer is enabled by setting `is_trainer` to `true`. Typically, you only need one trainer per a single database. It will perform training for all bots using the same database.

Arena model trainer could be run manually via:

```bash
python -m bestmobabot.trainer -v
```

Trained model is then saved back to the database.

### Prediction model

Random forest classifier is used to predict probability to win an arena (grand arena) battle. The input for this classifier is features of attackers and defenders such as: hero level, hero color and hero stars. [Secretary problem](https://en.wikipedia.org/wiki/Secretary_problem) optimal policy is then used to maximise win probability across possible enemies. The model is trained on past battles from the arena and grand arena journals.

### Arena optimisation

To find the best attackers, top N most powerful teams are fed into the classifier. The best one is then chosen as attackers. Usually, it's a global optimum when N is large enough (say 20000-40000).

### Grand arena optimisation

Grand arena is a bit special because the total number of hero combinations is too large to run the estimator on all of them (there're `N choose 5 × (N - 5) choose 5 × (N - 10) choose 5` possible attackers combinations). Thus, a sort of genetic algorithm is used to find the best attackers (local optimum perhaps).

## Storage

SQLite database is used as a sort of key-value store to preserve state between restarts:

* Arena and grand arena battle results
* Authentication credentials
* API session
* Picked up gifts
* Arena win probability prediction model

The same database can be used by multiple bots. Actually, it is _recommended_ that multiple bots use the same database in order to share the arena prediction model.

**Warning.** The database contains user IDs and Hero Wars API authentication tokens. Make sure that you remove them manually should you share your database. You can use the following statement to delete everything except of battle results:

```sql
DELETE FROM "default" WHERE "index" <> 'replays';
```

## Authors

* [Pavel Perestoronin](https://github.com/eigenein)

## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nc-nd/4.0/).

![Creative Commons License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)
