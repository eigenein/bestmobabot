# Dungeon

## Methods

It all starts with `tryInstantBattle`:

```js
tryInstantBattle: function() {
    var a = this.get_isHeroBattle() ? new sj(!1, !1, !0, v.battleConfig.get_tower(), !1) : new sj(!1, !1, !0, v.battleConfig.get_titan(), !1);
    
    // vq = game.battle.controller.instant.BattleInstantPlay
    a = new vq(this.cmd.get_battleInfo(), a);
    
    a.signal_hasResult.add(e(this, this.handler_instantBattleComplete));
    
    a.start()
}
```

The latter `start` calls:

```js
instantReplay: function(a) {
    a = new rq(this.battleData);
    r.battle.requestAssetWithPreloader(a, e(this, this.handler_battleCodeReady))
}
```

Which leads to:

```js
executeBattle: function() {
    var a = new Er(this.battleData.seed);
    Ra.doLog = !0;
    var b = new Mf(this.sceneProxy);
    b.load(this.battleData, this.presets.get_config(), (p = r.battle,
        e(p, p.effectFactory)), e(a, a.generateInt));
    b.doNotInterruptTimeAdvancement = !0;
    b.replay();
    b.finishBattleSeries();
    Mf.purge()
}
```

## Start Battle

### Request

```json
{
    "calls": [
        {
            "name": "dungeonStartBattle",
            "args": {
                "heroes": [
                    4021,
                    4022,
                    4020
                ],
                "teamNum": 0
            },
            "ident": "body"
        }
    ]
}
```

### Response

```json
{
    "date": 1549574686.043991,
    "results": [
        {
            "ident": "body",
            "result": {
                "response": {
                    "userId": "833061",
                    "typeId": -1000553,
                    "attackers": {
                        "4021": {
                            "id": 4021,
                            "xp": 0,
                            "level": 1,
                            "star": 1,
                            "skills": {
                                "4021": 1
                            },
                            "power": 157,
                            "artifacts": [
                                {
                                    "level": 1,
                                    "star": 0
                                },
                                {
                                    "level": 1,
                                    "star": 0
                                },
                                {
                                    "level": 1,
                                    "star": 0
                                }
                            ],
                            "scale": 0.8,
                            "anticrit": 1,
                            "antidodge": 1,
                            "hp": 17045,
                            "physicalAttack": 1041,
                            "element": "earth",
                            "elementSpiritLevel": 1,
                            "elementSpiritStar": 0,
                            "state": {
                                "hp": 17045,
                                "energy": 600,
                                "isDead": false
                            }
                        },
                        "4022": {
                            "id": 4022,
                            "xp": 3060,
                            "level": 18,
                            "star": 1,
                            "skills": {
                                "4023": 18
                            },
                            "power": 926,
                            "artifacts": [
                                {
                                    "level": 1,
                                    "star": 0
                                },
                                {
                                    "level": 1,
                                    "star": 0
                                },
                                {
                                    "level": 1,
                                    "star": 0
                                }
                            ],
                            "scale": 0.8,
                            "anticrit": 1,
                            "antidodge": 1,
                            "hp": 109001.04,
                            "physicalAttack": 5450.05,
                            "element": "earth",
                            "elementSpiritLevel": 1,
                            "elementSpiritStar": 0,
                            "state": {
                                "hp": 109001,
                                "energy": 800,
                                "isDead": false
                            }
                        },
                        "4020": {
                            "id": 4020,
                            "xp": 32210,
                            "level": 55,
                            "star": 4,
                            "skills": {
                                "4019": 55
                            },
                            "power": 14063,
                            "artifacts": [
                                {
                                    "level": 43,
                                    "star": 2
                                },
                                {
                                    "level": 4,
                                    "star": 2
                                },
                                {
                                    "level": 10,
                                    "star": 1
                                }
                            ],
                            "scale": 0.8,
                            "anticrit": 1,
                            "antidodge": 1,
                            "hp": 1554744.26,
                            "physicalAttack": 51903.58,
                            "elementAttack": 33891.6,
                            "elementArmor": 939.6,
                            "element": "earth",
                            "elementSpiritLevel": 1,
                            "elementSpiritStar": 0,
                            "state": {
                                "hp": 1512035,
                                "energy": 1000,
                                "isDead": false
                            }
                        }
                    },
                    "defenders": [
                        {
                            "4002": {
                                "id": 4002,
                                "xp": 0,
                                "level": 26,
                                "star": 1,
                                "skills": {
                                    "4005": 26
                                },
                                "power": 1499,
                                "artifacts": [
                                    {
                                        "level": 1,
                                        "star": 0
                                    },
                                    {
                                        "level": 1,
                                        "star": 0
                                    },
                                    {
                                        "level": 1,
                                        "star": 0
                                    }
                                ],
                                "scale": 0.8,
                                "anticrit": 1,
                                "antidodge": 1,
                                "hp": 147041.51,
                                "physicalAttack": 11028.09,
                                "element": "water",
                                "elementSpiritLevel": 1,
                                "elementSpiritStar": 0
                            },
                            "4000": {
                                "id": 4000,
                                "xp": 0,
                                "level": 26,
                                "star": 1,
                                "skills": {
                                    "4001": 26
                                },
                                "power": 1504,
                                "artifacts": [
                                    {
                                        "level": 1,
                                        "star": 0
                                    },
                                    {
                                        "level": 1,
                                        "star": 0
                                    },
                                    {
                                        "level": 1,
                                        "star": 0
                                    }
                                ],
                                "scale": 0.8,
                                "anticrit": 1,
                                "antidodge": 1,
                                "hp": 161744.96,
                                "physicalAttack": 9992.07,
                                "element": "water",
                                "elementSpiritLevel": 1,
                                "elementSpiritStar": 0
                            }
                        }
                    ],
                    "effects": [],
                    "reward": {
                        "dungeonActivity": 5,
                        "fragmentTitan": {
                            "4012": 1
                        }
                    },
                    "startTime": 1549574686,
                    "seed": 2747195978,
                    "type": "dungeon_titan",
                    "rewardMultiplier": 1
                }
            }
        }
    ]
}
```

## End Battle

### Request

```json
{
    "calls": [
        {
            "name": "dungeonEndBattle",
            "args": {
                "result": {
                    "win": true,
                    "stars": 3
                },
                "progress": [
                    {
                        "v": 150,
                        "b": 0,
                        "seed": -1547771318,
                        "attackers": {
                            "input": [
                                "auto",
                                0,
                                0
                            ],
                            "heroes": {
                                "4020": {
                                    "hp": 1469096,
                                    "energy": 1000,
                                    "isDead": false
                                },
                                "4021": {
                                    "hp": 17045,
                                    "energy": 1000,
                                    "isDead": false
                                },
                                "4022": {
                                    "hp": 109001,
                                    "energy": 1000,
                                    "isDead": false
                                }
                            }
                        },
                        "defenders": {
                            "input": [],
                            "heroes": {}
                        }
                    }
                ]
            },
            "ident": "body"
        }
    ]
}
```

### Response

```json
{
    "date": 1549574706.191558,
    "results": [
        {
            "ident": "body",
            "result": {
                "response": {
                    "reward": {
                        "dungeonActivity": 5,
                        "fragmentTitan": {
                            "4012": 1
                        }
                    },
                    "rewardMultiplier": 1,
                    "dungeon": {
                        "userId": "833061",
                        "elements": {
                            "prime": "fire",
                            "nonprime": [
                                "water",
                                "earth"
                            ]
                        },
                        "respawnFloor": "181",
                        "floorNumber": 189,
                        "floorType": "battle",
                        "states": {
                            "titans": {
                                "4011": {
                                    "hp": 51226,
                                    "energy": 800,
                                    "isDead": false,
                                    "maxHp": 51226
                                },
                                "4010": {
                                    "hp": 642876,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 691253
                                },
                                "4013": {
                                    "hp": 706524,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 706524
                                },
                                "4012": {
                                    "hp": 792844,
                                    "energy": 600,
                                    "isDead": false,
                                    "maxHp": 792844
                                },
                                "4001": {
                                    "hp": 889189,
                                    "energy": 0,
                                    "isDead": false,
                                    "maxHp": 889189
                                },
                                "4020": {
                                    "hp": 1469096,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 1554744
                                },
                                "4021": {
                                    "hp": 17045,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 17045
                                },
                                "4022": {
                                    "hp": 109001,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 109001
                                }
                            }
                        },
                        "floor": {
                            "userData": [
                                {
                                    "defenderType": "hero",
                                    "chance": 1,
                                    "arenaHeroesPacked": "p:[{\"star\":\"3\",\"color\":4,\"id\":\"4\",\"level\":\"36\"},{\"star\":\"3\",\"color\":4,\"id\":\"14\",\"level\":\"36\"},{\"star\":\"1\",\"color\":4,\"id\":\"7\",\"level\":\"36\"},{\"star\":\"1\",\"color\":4,\"id\":\"10\",\"level\":\"36\"},{\"star\":\"3\",\"color\":4,\"id\":\"8\",\"level\":\"36\"}]",
                                    "userId": "-200035",
                                    "team": [
                                        {
                                            "star": "3",
                                            "color": 4,
                                            "id": "4",
                                            "level": "36"
                                        },
                                        {
                                            "star": "3",
                                            "color": 4,
                                            "id": "14",
                                            "level": "36"
                                        },
                                        {
                                            "star": "1",
                                            "color": 4,
                                            "id": "7",
                                            "level": "36"
                                        },
                                        {
                                            "star": "1",
                                            "color": 4,
                                            "id": "10",
                                            "level": "36"
                                        },
                                        {
                                            "star": "3",
                                            "color": 4,
                                            "id": "8",
                                            "level": "36"
                                        }
                                    ],
                                    "delta": 707,
                                    "needPower": 23587,
                                    "power": "22881",
                                    "attackerType": "hero"
                                }
                            ],
                            "defenders": [],
                            "state": 1
                        },
                        "reward": [],
                        "maxFloorReached": "190"
                    },
                    "states": {
                        "titans": {
                            "4011": {
                                "hp": 51226,
                                "energy": 800,
                                "isDead": false,
                                "maxHp": 51226
                            },
                            "4010": {
                                "hp": 642876,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 691253
                            },
                            "4013": {
                                "hp": 706524,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 706524
                            },
                            "4012": {
                                "hp": 792844,
                                "energy": 600,
                                "isDead": false,
                                "maxHp": 792844
                            },
                            "4001": {
                                "hp": 889189,
                                "energy": 0,
                                "isDead": false,
                                "maxHp": 889189
                            },
                            "4020": {
                                "hp": 1469096,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 1554744
                            },
                            "4021": {
                                "hp": 17045,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 17045
                            },
                            "4022": {
                                "hp": 109001,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 109001
                            }
                        }
                    },
                    "dungeonActivity": 352
                },
                "quests": [
                    {
                        "id": 10021,
                        "state": 1,
                        "progress": 24,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 10022,
                        "state": 1,
                        "progress": 24,
                        "reward": {
                            "coin": {
                                "13": "2"
                            }
                        }
                    }
                ]
            }
        }
    ]
}
```
