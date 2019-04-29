# Непереведенная документация

## Settings

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

## Trainer

Trainer is enabled by setting `is_trainer` to `true`. Typically, you only need one trainer per a single database. It will perform training for all bots using the same database.

Arena model trainer could be run manually via:

```bash
python -m bestmobabot.trainer -v
```

Trained model is then saved back to the database.

## Prediction model

Random forest classifier is used to predict probability to win an arena (grand arena) battle. The input for this classifier is features of attackers and defenders such as: hero level, hero color and hero stars. [Secretary problem](https://en.wikipedia.org/wiki/Secretary_problem) optimal policy is then used to maximise win probability across possible enemies. The model is trained on past battles from the arena and grand arena journals.

## Arena and grand arena optimisation

A sort of genetic algorithm is used to find the best attackers (local optimum perhaps).

## Storage

SQLite database is used as a sort of key-value store to preserve state between restarts:

* Arena and grand arena battle results
* Arena and grand arena enemies
* Authentication credentials
* API session
* Picked up gifts
* Arena win probability prediction model

The same database can be used by multiple bots. Actually, it is _recommended_ that multiple bots use the same database in order to share the arena prediction model.

**Warning.** The database contains user IDs and Hero Wars API authentication tokens. Make sure that you remove them manually should you share your database.
