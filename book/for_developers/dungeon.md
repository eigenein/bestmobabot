# Подземелье

## `clanGetActivityStat`

```json
{"name":"clanGetActivityStat","args":{},"ident":"group_1_body"}
```

```json
{"clanActivity":8918,"dungeonActivity":842,"stat":{"todayActivity":148,"activitySum":148,"dungeonActivitySum":150,"todayRaid":[],"todayItemsActivity":0,"todayDungeonActivity":150,"activityForRuneAvailable":false}}
```

## `titanGetAll`

```json
{"ident":"titanGetAll","result":{"response":{"4001":{"id":4001,"xp":30420,"level":54,"star":4,"skills":{"4003":54},"power":12648,"artifacts":[{"level":34,"star":2},{"level":1,"star":1},{"level":1,"star":1}],"scale":0.80000000000000004},"4020":{"id":4020,"xp":32210,"level":55,"star":4,"skills":{"4019":55},"power":14063,"artifacts":[{"level":43,"star":2},{"level":4,"star":2},{"level":10,"star":1}],"scale":0.80000000000000004},"4002":{"id":4002,"xp":6580,"level":29,"star":3,"skills":{"4005":29},"power":3333,"artifacts":[{"level":1,"star":0},{"level":1,"star":0},{"level":1,"star":0}],"scale":0.80000000000000004},"4010":{"id":4010,"xp":32210,"level":55,"star":3,"skills":{"4010":55},"power":11042,"artifacts":[{"level":42,"star":1},{"level":10,"star":1},{"level":1,"star":1}],"scale":0.80000000000000004},"4012":{"id":4012,"xp":30420,"level":54,"star":4,"skills":{"4014":54},"power":12653,"artifacts":[{"level":28,"star":3},{"level":3,"star":1},{"level":2,"star":1}],"scale":0.80000000000000004},"4011":{"id":4011,"xp":2310,"level":15,"star":2,"skills":{"4012":15},"power":1015,"artifacts":[{"level":1,"star":0},{"level":1,"star":0},{"level":1,"star":0}],"scale":0.80000000000000004},"4022":{"id":4022,"xp":3060,"level":18,"star":2,"skills":{"4023":18},"power":1290,"artifacts":[{"level":1,"star":0},{"level":1,"star":0},{"level":1,"star":0}],"scale":0.80000000000000004},"4000":{"id":4000,"xp":19200,"level":46,"star":3,"skills":{"4001":46},"power":8545,"artifacts":[{"level":37,"star":1},{"level":7,"star":1},{"level":2,"star":1}],"scale":0.80000000000000004},"4013":{"id":4013,"xp":32210,"level":55,"star":3,"skills":{"4016":55,"4017":55},"power":11260,"artifacts":[{"level":37,"star":3},{"level":7,"star":1},{"level":1,"star":1}],"scale":0.80000000000000004},"4021":{"id":4021,"xp":0,"level":1,"star":2,"skills":{"4021":1},"power":162,"artifacts":[{"level":1,"star":0},{"level":1,"star":0},{"level":1,"star":0}],"scale":0.80000000000000004}}}}
```

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

```json
{
    "date": 1551651295.916583,
    "results": [
        {
            "ident": "body",
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
                    "respawnFloor": "231",
                    "floorNumber": "250",
                    "floorType": "battle",
                    "states": {
                        "titans": {
                            "4011": {
                                "hp": 70340,
                                "energy": 200,
                                "isDead": false,
                                "maxHp": 70340
                            },
                            "4010": {
                                "hp": 639100,
                                "energy": 629,
                                "isDead": false,
                                "maxHp": 750366
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
                            },
                            "4021": {
                                "hp": 17559,
                                "energy": 600,
                                "isDead": false,
                                "maxHp": 17559
                            },
                            "4022": {
                                "hp": 151766,
                                "energy": 800,
                                "isDead": false,
                                "maxHp": 151766
                            },
                            "4020": {
                                "hp": 1258064,
                                "energy": 709,
                                "isDead": false,
                                "maxHp": 1554744
                            },
                            "4002": {
                                "hp": 326806,
                                "energy": 400,
                                "isDead": false,
                                "maxHp": 326806
                            },
                            "4001": {
                                "hp": 967440,
                                "energy": 200,
                                "isDead": false,
                                "maxHp": 967440
                            },
                            "4000": {
                                "hp": 436523,
                                "energy": 941,
                                "isDead": false,
                                "maxHp": 708451
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
                                        "id": 4002,
                                        "level": 26,
                                        "star": 2
                                    },
                                    {
                                        "id": 4000,
                                        "level": 27,
                                        "star": 2
                                    }
                                ],
                                "userId": -1000915,
                                "power": 4377,
                                "attackerType": "earth"
                            },
                            {
                                "defenderType": "fire",
                                "chance": 50,
                                "team": [
                                    {
                                        "id": 4012,
                                        "level": 26,
                                        "star": 2,
                                        "buffs": {
                                            "hp": 3480.3921568627447,
                                            "physicalAttack": 261.02941176470586
                                        }
                                    },
                                    {
                                        "id": 4010,
                                        "level": 26,
                                        "star": 2,
                                        "buffs": {
                                            "hp": 3480.3921568627447,
                                            "physicalAttack": 261.02941176470586
                                        }
                                    }
                                ],
                                "userId": -2000890,
                                "power": 4330,
                                "attackerType": "water"
                            }
                        ],
                        "defenders": {
                            "1": [
                                []
                            ]
                        },
                        "state": 2
                    },
                    "reward": [],
                    "maxFloorReached": "250"
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
