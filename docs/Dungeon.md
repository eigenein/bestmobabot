# Dungeon

## `dungeonGetInfo`

```json
{"name":"dungeonGetInfo","args":{},"ident":"group_1_body"}
```

```json
{
    "date": 1551616579.361306,
    "results": [
        {
            "ident": "group_0_body",
            "result": {
                "response": [
                    true
                ]
            }
        },
        {
            "ident": "group_1_body",
            "result": {
                "response": {
                    "userId": "833061",
                    "elements": {
                        "prime": "fire",
                        "nonprime": [
                            "water",
                            "earth"
                        ]
                    },
                    "respawnFloor": "221",
                    "floorNumber": "221",
                    "floorType": "battle",
                    "states": {
                        "titans": []
                    },
                    "floor": {
                        "userData": [
                            {
                                "defenderType": "hero",
                                "chance": 1,
                                "arenaHeroesPacked": "p:[{\"color\":4,\"id\":\"4\",\"level\":\"39\",\"star\":\"3\"},{\"color\":4,\"id\":\"1\",\"level\":\"39\",\"star\":\"2\"},{\"color\":4,\"id\":\"9\",\"level\":\"39\",\"star\":\"1\"},{\"color\":4,\"id\":\"5\",\"level\":\"39\",\"star\":\"3\"},{\"color\":4,\"id\":\"19\",\"level\":\"39\",\"star\":\"3\"}]",
                                "userId": "-560009",
                                "team": [
                                    {
                                        "color": 4,
                                        "id": "4",
                                        "level": "39",
                                        "star": "3"
                                    },
                                    {
                                        "color": 4,
                                        "id": "1",
                                        "level": "39",
                                        "star": "2"
                                    },
                                    {
                                        "color": 4,
                                        "id": "9",
                                        "level": "39",
                                        "star": "1"
                                    },
                                    {
                                        "color": 4,
                                        "id": "5",
                                        "level": "39",
                                        "star": "3"
                                    },
                                    {
                                        "color": 4,
                                        "id": "19",
                                        "level": "39",
                                        "star": "3"
                                    }
                                ],
                                "delta": 770,
                                "needPower": 25679,
                                "power": "24961",
                                "attackerType": "hero"
                            }
                        ],
                        "defenders": [],
                        "state": 1
                    },
                    "reward": [],
                    "maxFloorReached": "230"
                }
            }
        }
    ]
}
```

## `dungeonStartBattle`

```json
{"calls":[{"name":"dungeonStartBattle","args":{"heroes":[39,25,35,13,29],"teamNum":0},"ident":"body"}]}
```

```json
{"name":"dungeonStartBattle","args":{"heroes":[4021,4022,4020],"teamNum":0},"ident":"group_1_body"}
```

```json
{"name":"dungeonStartBattle","args":{"heroes":[4021,4022,4020],"teamNum":1},"ident":"group_1_body"}
```

## `dungeonEndBattle`

```json
{
    "date": 1551617810.169543,
    "results": [
        {
            "ident": "body",
            "result": {
                "response": {
                    "reward": {
                        "dungeonActivity": 1,
                        "consumable": {
                            "20": 25
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
                        "respawnFloor": "221",
                        "floorNumber": 222,
                        "floorType": "battle",
                        "states": {
                            "titans": []
                        },
                        "floor": {
                            "userData": [
                                {
                                    "defenderType": "earth",
                                    "chance": 75,
                                    "team": [
                                        {
                                            "id": 4022,
                                            "level": 30,
                                            "star": 1
                                        },
                                        {
                                            "id": 4020,
                                            "level": 30,
                                            "star": 1
                                        }
                                    ],
                                    "userId": -3000687,
                                    "power": 3645,
                                    "attackerType": "fire"
                                }
                            ],
                            "defenders": [],
                            "state": 1
                        },
                        "reward": [],
                        "maxFloorReached": "230"
                    },
                    "states": {
                        "titans": []
                    },
                    "dungeonActivity": 432
                },
                "quests": [
                    {
                        "id": 10021,
                        "state": 1,
                        "progress": 1,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 10022,
                        "state": 1,
                        "progress": 1,
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

```json
{
    "date": 1551619371.579586,
    "results": [
        {
            "ident": "group_0_body",
            "result": {
                "response": [
                    true,
                    true,
                    true,
                    true,
                    true
                ]
            }
        },
        {
            "ident": "group_1_body",
            "result": {
                "response": {
                    "reward": {
                        "dungeonActivity": 1,
                        "consumable": {
                            "20": 25
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
                        "respawnFloor": "221",
                        "floorNumber": 225,
                        "floorType": "battle",
                        "states": {
                            "titans": {
                                "4011": {
                                    "hp": 51226,
                                    "energy": 400,
                                    "isDead": false,
                                    "maxHp": 51226
                                },
                                "4010": {
                                    "hp": 700916,
                                    "energy": 419,
                                    "isDead": false,
                                    "maxHp": 730477
                                },
                                "4013": {
                                    "hp": 706524,
                                    "energy": 600,
                                    "isDead": false,
                                    "maxHp": 706524
                                },
                                "4012": {
                                    "hp": 862389,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 862389
                                }
                            }
                        },
                        "floor": {
                            "userData": [
                                {
                                    "defenderType": "water",
                                    "chance": 50,
                                    "team": [
                                        {
                                            "id": 4000,
                                            "level": 30,
                                            "star": 1
                                        },
                                        {
                                            "id": 4001,
                                            "level": 31,
                                            "star": 1
                                        }
                                    ],
                                    "userId": -1000754,
                                    "power": 3742,
                                    "attackerType": "earth"
                                },
                                {
                                    "defenderType": "neutral",
                                    "chance": 50,
                                    "team": [
                                        {
                                            "id": 4002,
                                            "level": 31,
                                            "star": 1
                                        },
                                        {
                                            "id": 4021,
                                            "level": 31,
                                            "star": 1
                                        }
                                    ],
                                    "userId": -4000703,
                                    "power": 3811,
                                    "attackerType": "neutral"
                                }
                            ],
                            "defenders": [],
                            "state": 1
                        },
                        "reward": [],
                        "maxFloorReached": "230"
                    },
                    "states": {
                        "titans": {
                            "4011": {
                                "hp": 51226,
                                "energy": 400,
                                "isDead": false,
                                "maxHp": 51226
                            },
                            "4010": {
                                "hp": 700916,
                                "energy": 419,
                                "isDead": false,
                                "maxHp": 730477
                            },
                            "4013": {
                                "hp": 706524,
                                "energy": 600,
                                "isDead": false,
                                "maxHp": 706524
                            },
                            "4012": {
                                "hp": 862389,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 862389
                            }
                        }
                    },
                    "dungeonActivity": 443
                },
                "quests": [
                    {
                        "id": 10021,
                        "state": 1,
                        "progress": 8,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 10022,
                        "state": 1,
                        "progress": 8,
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

```json
{
    "date": 1551630357.287681,
    "results": [
        {
            "ident": "body",
            "result": {
                "response": {
                    "reward": {
                        "dungeonActivity": 10,
                        "fragmentTitan": {
                            "4021": 2
                        }
                    },
                    "rewardMultiplier": 2,
                    "states": {
                        "titans": {
                            "4011": {
                                "hp": 51226,
                                "energy": 600,
                                "isDead": false,
                                "maxHp": 51226
                            },
                            "4010": {
                                "hp": 669236,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 730477
                            },
                            "4013": {
                                "hp": 706524,
                                "energy": 200,
                                "isDead": false,
                                "maxHp": 706524
                            },
                            "4012": {
                                "hp": 862389,
                                "energy": 700,
                                "isDead": false,
                                "maxHp": 862389
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
                            },
                            "4020": {
                                "hp": 1326222,
                                "energy": 500,
                                "isDead": false,
                                "maxHp": 1554744
                            },
                            "4002": {
                                "hp": 243568,
                                "energy": 200,
                                "isDead": false,
                                "maxHp": 243568
                            },
                            "4001": {
                                "hp": 967440,
                                "energy": 1000,
                                "isDead": false,
                                "maxHp": 967440
                            },
                            "4000": {
                                "hp": 382462,
                                "energy": 861,
                                "isDead": false,
                                "maxHp": 525315
                            }
                        }
                    },
                    "dungeonActivity": 624
                },
                "quests": [
                    {
                        "id": 10021,
                        "state": 2,
                        "progress": 90,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 10022,
                        "state": 1,
                        "progress": 90,
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

## `dungeonSaveProgress`

```json
{"calls":[{"name":"dungeonSaveProgress","args":{},"ident":"body"}]}
```

```json
{
    "date": 1551630539.122356,
    "results": [
        {
            "ident": "body",
            "result": {
                "response": {
                    "reward": {
                        "gold": 17200
                    },
                    "dungeon": {
                        "userId": "833061",
                        "elements": {
                            "prime": "fire",
                            "nonprime": [
                                "water",
                                "earth"
                            ]
                        },
                        "respawnFloor": "231",
                        "floorNumber": 241,
                        "floorType": "battle",
                        "states": {
                            "titans": {
                                "4011": {
                                    "hp": 51226,
                                    "energy": 600,
                                    "isDead": false,
                                    "maxHp": 51226
                                },
                                "4010": {
                                    "hp": 669236,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 730477
                                },
                                "4013": {
                                    "hp": 706524,
                                    "energy": 200,
                                    "isDead": false,
                                    "maxHp": 706524
                                },
                                "4012": {
                                    "hp": 862389,
                                    "energy": 700,
                                    "isDead": false,
                                    "maxHp": 862389
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
                                },
                                "4020": {
                                    "hp": 1326222,
                                    "energy": 500,
                                    "isDead": false,
                                    "maxHp": 1554744
                                },
                                "4002": {
                                    "hp": 243568,
                                    "energy": 200,
                                    "isDead": false,
                                    "maxHp": 243568
                                },
                                "4001": {
                                    "hp": 967440,
                                    "energy": 1000,
                                    "isDead": false,
                                    "maxHp": 967440
                                },
                                "4000": {
                                    "hp": 382462,
                                    "energy": 861,
                                    "isDead": false,
                                    "maxHp": 525315
                                }
                            }
                        },
                        "floor": {
                            "userData": [
                                {
                                    "defenderType": "hero",
                                    "chance": 1,
                                    "arenaHeroesPacked": "p:[{\"id\":2,\"level\":48,\"color\":6,\"star\":1},{\"id\":20,\"level\":49,\"color\":6,\"star\":1},{\"id\":4,\"level\":50,\"color\":6,\"star\":2},{\"id\":6,\"level\":50,\"color\":6,\"star\":1},{\"id\":7,\"level\":50,\"color\":6,\"star\":2}]",
                                    "userId": "851135",
                                    "team": [
                                        {
                                            "id": 2,
                                            "level": 48,
                                            "color": 6,
                                            "star": 1
                                        },
                                        {
                                            "id": 20,
                                            "level": 49,
                                            "color": 6,
                                            "star": 1
                                        },
                                        {
                                            "id": 4,
                                            "level": 50,
                                            "color": 6,
                                            "star": 2
                                        },
                                        {
                                            "id": 6,
                                            "level": 50,
                                            "color": 6,
                                            "star": 1
                                        },
                                        {
                                            "id": 7,
                                            "level": 50,
                                            "color": 6,
                                            "star": 2
                                        }
                                    ],
                                    "delta": 785,
                                    "needPower": 26177,
                                    "power": "25462",
                                    "attackerType": "hero"
                                }
                            ],
                            "defenders": [],
                            "state": 1
                        },
                        "reward": [],
                        "maxFloorReached": 241
                    }
                },
                "quests": [
                    {
                        "id": 329,
                        "state": 3,
                        "progress": 240,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 330,
                        "state": 3,
                        "progress": 240,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 331,
                        "state": 3,
                        "progress": 240,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 332,
                        "state": 3,
                        "progress": 240,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 333,
                        "state": 1,
                        "progress": 240,
                        "reward": {
                            "coin": {
                                "13": "1"
                            }
                        }
                    },
                    {
                        "id": 10034,
                        "state": 3,
                        "progress": 240,
                        "reward": {
                            "consumable": {
                                "81": "5"
                            }
                        }
                    },
                    {
                        "id": 10035,
                        "state": 1,
                        "progress": 240,
                        "reward": {
                            "consumable": {
                                "81": "5"
                            }
                        }
                    },
                    {
                        "id": 10036,
                        "state": 1,
                        "progress": 240,
                        "reward": {
                            "consumable": {
                                "81": "5"
                            }
                        }
                    }
                ]
            }
        }
    ]
}
```
