(function(h) {
    var BattleInstantPlay = h['game.battle.controller.instant.BattleInstantPlay'];
    var BattlePresets = h['game.battle.controller.thread.BattlePresets'];
    var DataStorage = h['game.data.storage.DataStorage'];

    var response = {
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
    };
    var presets = new BattlePresets(!1, !1, !0, DataStorage.battleConfig.get_titan(), !1);
    var play = new BattleInstantPlay(response, presets);
})(window.h)
