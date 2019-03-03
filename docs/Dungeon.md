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
