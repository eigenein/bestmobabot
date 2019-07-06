# Changelog

## `3.2.1`

- **Исправление**: логин в VK.com переставал работать примерно через сутки

## `3.2.0`

- **Исправление**: VK.com начал обновлять `remixsid` примерно раз в сутки, используйте авторизацию по паролю
- **Исправление**: `orjson` удален из-за сложной установки на Windows

## `3.1.0`

Первая общедоступная версия.

- **Новое**: [документация](https://eigenein.github.io/bestmobabot/)
- **Изменение**: `jsapi` удален из-за обфускации кода разработчиками игры
- **Изменение**: в предсказательную модель арены добавлены новые признаки
- **Исправление**: #7 обработка ошибки `NotEnoughError`
- **Исправление**: обновление `lib.json` и `ru.json`

## `3.0`

- Fix: `farm_expedition` return value
- Change: Check expeditions 2 times less frequently
- Change: element choice condition in dungeon
- Fix: work around `NotFoundError` `Battle with type clan_dungeon and typeId #XXXXXX`
- Fix: arena retries
- Change: resources `v0497`
- Opt: improve `heroes.js` monkeypatch
- Change: more frequent `raid_missions`
- Change: save additional hero attributes
- Fix: `hall_of_fame` crashes when trophy is empty
- Change: remove Google Analytics

## `3.0b3`

- Add dungeon APIs
- Add `dungeon_activity` reward
- Improve timezone logging
- Use single `requests.Session`
- Remake Telegram notifications
- Add initial dungeon implementation
- Handle `MemoryError`
- Fix `execute_battle_with_retry` return value
- Refactor API exception classes
- Upgrade resources to `v0490`
- Add mission APIs
- Farm Hall of Fame reward on Saturday
- Disable `backtrace`

## `3.0b2`

- First check if enemy user is `None`

## `3.0b1`

- **Automatically level up and drop titan hero gift**
- **Task retries are now persisted**
- **Retry arena if estimated win probability is too low**
- Use `orjson`
- New scheduler

## `3.0b0`

- **Automatic tower**
- **Auto-enchant rune**
- `heroes.js` interface
- Vendored game resources

## `2.4`

- Fix critical error in `send_expeditions`
- Set timeout on VK.com API
- Upgrade `numpy`
- Fix `numpy` warning
- Upgrade `pandas`
- Update `User-Agent`
- Add `i_am_alive` recurring task

## `2.4b11`

* fix: improve logging for `send_expeditions`
* feat: set `PYTHONOPTIMIZE=2` for the Python interpreter
* Upgrade `loguru`

## `2.4b10`

* **Send multiple expeditions at once**

## `2.4b9`

* Fix storing arena enemies in the database

## `2.4b7`

* Change `Database` interface. The model must be re-trained after deployment
* Store heroes of arena enemies in the database

## `2.4b6`

* Merge `index` and `key` columns in the database. Manual upgrade script:

```bash
litecli db.sqlite3
```

```sql
CREATE TABLE `new` (
    `key` TEXT PRIMARY KEY NOT NULL,
    value TEXT,
    modified_on DATETIME DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO `new` (`key`, value, modified_on) SELECT `index` || ':' || `key`, value, modified_on FROM `default`;
DROP TABLE IF EXISTS `backup`;
ALTER TABLE `default` RENAME TO `backup`;
ALTER TABLE `new` RENAME TO `default`;
```

## `2.4b5`

* **Hot fix for grand arena enemies at places under 100**

## `2.4b4`

* **Print arena win rating**

## `2.4b3`

* **Unified arena solver for arenas**

## `2.4b2`

* Fix critical bug in `bestmobabot.dataclasses_.ShopSlot`

## `2.4b1`

* **Unified arena solver for arenas, work in progress**
* Fix critical bug in `bestmobabot.dataclasses_.Tower`

## `2.4b0`

* **Send logging messages to Telegram (experimental)**
* **Support tower full skip for the 130th level**
* **Switch response classes to `pydantic`**
* Improve packaging, remove `--log-file` option and improve Docker integration
* Use `ujson` instead of `json`
* Update resources
* Use `loguru` for logging and improve testing
* Set default settings filename

## `2.3`

* Fix possible bug with grand arena enemy selection and/or logging
* Use last `N` battles for training
* Update `User-Agent`
* Upgrade `click` package

## `2.2`

* **Buy things by their names**
* **Raid missions by their names**
* **`grand_generations_cool_down` setting instead of `grand_generations`**
* Embed IPython
* Switch back to plain old `requirements.txt`
* Fix `--help`
* Use `pydantic` for response classes
* Make tasks parameterless
* Add shop #11
* Revert model without power features
* Refresh clan ID before running arena
* Improve arena logging

## `2.1`

* **Option to randomize grand arena defenders**
* **Add `grand_generate_solutions` and `grand_keep_solutions` options**
* Add required parameter to `friendsSendDailyGift`
* Update `User-Agent` and resources
* Add new features and improve prediction quality
* Remove de-duplication of battles (not needed anymore), filter out battles without hero powers
* Change logging format, remove emoji's
* Change `open_titan_artifact_chest` time
* Make `secretary_max` choose better _or equal_

## `2.0`

**Breaking change.** As I keep adding more and more configuration options, I decided to move them out from the command line and environment variables to a separate configuration file. If you upgraded to this version, make sure you properly move your settings.

* **New: introducing configuration file**
* **New: configure maximum number of arena pages during enemy search**
* **New: configure the model hyper-parameters**
* Change: distribute stamina evenly between heroic missions

## `2.0b`

* **Fix: forever cached user info**
* **New: farm shops #8 and #10**
* **New: option to skip particular clans in arena**
* **New: open titan artifact chests**
* Chore: improve logging code
* Opt: upgrade to Python 3.7
* Chore: upgrade game resources
* Opt: improve parameters validation

## `1.2`

* **New: raid bosses**
* Fix: offer farming

## `1.1`

* New: farm offers
* Chore: simplify expeditions code
* Change: check expeditions more frequently
* Fix: gracefully handle offer farm error
* Chore: update resources

## `1.0` «It's 1.0»

* **Change: completely redesign raids – spend all stamina**
* Opt: optimise grand arena by keeping the best solutions during the entire search process
* Opt: update translations
* Fix: `ValueError: max() arg is an empty sequence` in arena
* Chore: add `SPAM` logging level
* New: allow stopping the hyper-parameters search process with Command+C

## `0.5` «Playground»

![](resources/strongford.jpg)

* Opt: use `3.6.5-wee` docker image
* Chore: switch to `pipenv`
* New: add `ARENA_EARLY_STOP` parameter
* New: ddd `GRAND_ARENA_GENERATIONS` parameter
* New: add `ARENA_TEAMS_LIMIT` parameter
* New: add `FRIENDS` parameter
* New: model trainer is now using T-test to compare scores – it should decrease `n_estimators` and improve speed
* New: caching selected arena attackers during the search
* Opt: vacuum the database after training
* Chore: delete `test` branch

## `v0.4.1`

* Opt: stability improvements and game translations update

## `v0.4` «Arena Time»

![](resources/gw_arena_heroes.jpg)

* **New: automatic arena model training**
* **Change: battle logs are moved to SQLite**
* **New: configurable VK.com token**
* New: `BESTMOBABOT_ARENA_OFFSET` option to shift arena schedule
* Change: tinyDB is replaced with SQLite
* New: added early stop to arena enemy selection, early stop improvements
* Change: generated model is removed from the codebase
* Change: hardcoded VK.com token is revoked
* New: workaround to speed up arena computations
* New: save hero powers in the battle log
* Chore: update game locale to `v0351`
* Change: shift raid schedules over day
* Opt: add mirrored battles to the training data set

## `v0.3.1`

* Opt: stability improvements and model updates

## `v0.3`

* New: grand arena with predictive model
* New: trainer command
* New: shopping
* Opt: stability improvements

## `v0.2` «Machine Learning»

![](resources/arena.png)

* New: bot is able to use the prediction model to attack the best arena enemy

## `v0.1`

* New: the first pre-release that is more or less stable and performs common everyday tasks
