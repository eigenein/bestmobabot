# `latest`

* Farm offers
* Simplify expeditions code
* Check expeditions more frequently
* Gracefully handle offer farm error

# `1.0` «It's 1.0»

* **Completely redesign raids – spend all stamina**
* Optimise grand arena by keeping the best solutions during the entire search process
* Update translations
* Fix `ValueError: max() arg is an empty sequence` in arena
* Add `SPAM` logging level
* Allow stopping the hyper-parameters search process with Command+C

# `0.5` «Playground»

![](resources/strongford.jpg)

* Use `3.6.5-wee` docker image
* Switch to `pipenv`
* Add `ARENA_EARLY_STOP` parameter
* Add `GRAND_ARENA_GENERATIONS` parameter
* Add `ARENA_TEAMS_LIMIT` parameter
* Add `FRIENDS` parameter
* Model trainer is now using T-test to compare scores – it should decrease `n_estimators` and improve speed
* Caching selected arena attackers during the search
* Vacuum the database after training
* Delete `test` branch

# `v0.4.1`

* Stability improvements and game translations update

# `v0.4` «Arena Time»

![](resources/gw_arena_heroes.jpg)

* **Automatic arena model training**
* **Battle logs are moved to SQLite**
* **Configurable VK.com token**
* `BESTMOBABOT_ARENA_OFFSET` option to shift arena schedule
* TinyDB is replaced with SQLite
* Added early stop to arena enemy selection, early stop improvements
* Generated model is removed from the codebase
* Hardcoded VK.com token is revoked
* Workaround to speed up arena computations
* Save hero powers in the battle log
* Update game locale to `v0351`
* Shift raid schedules over day
* Add mirrored battles to the training data set

# `v0.3.1`

* Stability improvements and model updates

# `v0.3`

* Grand arena with predictive model
* Trainer command
* Shopping
* Stability improvements

# `v0.2` «Machine Learning»

![](resources/arena.png)

* Bot is able to use the prediction model to attack the best arena enemy

# `v0.1`

* The first pre-release that is more or less stable and performs common everyday tasks
