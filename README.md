Bot playing [Hero Wars](https://vk.com/app5327745) MOBA-like game on [VK.com](https://vk.com). The bot uses pure reverse-engineered Hero Wars JSON API. No Flash-emulator is used.

## Running with Docker Compose

```bash
mkdir -p /srv/bestmobabot
docker-compose up -d
```

It's recommended that you copy `db.sqlite3` from a release to `/srv/bestmobabot`. Released databases already contain thousands of battle results which is very useful for arena automation.

### `docker-compose.yml`

```yaml
version: "3.3"
services:
  bestmobabot-user-1:
    image: eigenein/bestmobabot
    restart: always
    environment:
      - REMIXSID=VK.com-remixsid-cookie-1
      - LOGFILE=/srv/bestmobabot/bestmobabot-user-1.log
      - NO_EXPERIENCE=true
      - RAIDS=16 57
      - SHOPS=1 4 1 5
      - IS_TRAINER=true
      - VK_TOKEN=VK.com-API-token
      - ARENA_OFFSET=3600
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
  bestmobabot-user-2:
    image: eigenein/bestmobabot
    restart: always
    environment:
      - REMIXSID=VK.com-remixsid-cookie-2
      - LOGFILE=/srv/bestmobabot/bestmobabot-user-2.log
      - NO_EXPERIENCE=false
      - VK_TOKEN=VK.com-API-token
    volumes:
      - /srv/bestmobabot:/srv/bestmobabot
      - /etc/timezone:/etc/timezone:ro
      - /etc/localtime:/etc/localtime:ro
```

### Running with Docker

Of course, the bot could be run just with Docker. Run `docker run eigenein/bestmobabot --help` to see the possible options. Environment variables are accepted too.

## Tasks

Bot uses its own cron-like scheduler to perform game tasks. There're tasks that performed daily at particular time and there're periodic tasks that performed every N minutes/hours. They're spread over a day to decrease game API requests frequency.

Also, for expeditions the bot tries to pick up a reward and start the next expedition as soon as possible, given that the bot is not restarted in the meantime.

## Trainer

Trainer is enabled by setting `IS_TRAINER` to `true`. Typically, you only need one trainer per a single database. It will perform training for all bots using the same database.

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

Grand arena is a bit special because the total number of hero combinations is too large to run the estimator on all of them (there're `N choose 5 ⋅ (N - 5) choose 5 ⋅ (N - 10) choose 5` possible attackers combinations). Thus, a sort of genetic algorithm is used to find the best attackers (local optimum perhaps).

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
delete from "default" where "index" <> 'replays';
```

## Authors

* [Pavel Perestoronin](https://github.com/eigenein)

## License

This work is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](http://creativecommons.org/licenses/by-nc-nd/4.0/).

![Creative Commons License](https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png)
