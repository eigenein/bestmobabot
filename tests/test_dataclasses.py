from __future__ import annotations

from orjson import loads
from pytest import mark

from bestmobabot import dataclasses_


@mark.parametrize('response', [
    # language=json
    '{"consumable":{"24":250}}',

    # language=json
    '{"dungeonActivity": 1,"consumable": {"20": 25}}',

    # language=json
    '{"coin": {"13": "2"}}',

    # language=json
    '{"dungeonActivity":5,"fragmentTitan":{"4012":1}}',
])
def test_reward(response: str):
    dataclasses_.Reward.parse_obj(loads(response)).log()


@mark.parametrize('response', [
    # language=json
    '{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"221","floorNumber":"221","floorType":"battle","states":{"titans":[]},"floor":{"userData":[{"defenderType":"hero","chance":1,"arenaHeroesPacked":"p:[{\\"color\\":4,\\"id\\":\\"4\\",\\"level\\":\\"39\\",\\"star\\":\\"3\\"},{\\"color\\":4,\\"id\\":\\"1\\",\\"level\\":\\"39\\",\\"star\\":\\"2\\"},{\\"color\\":4,\\"id\\":\\"9\\",\\"level\\":\\"39\\",\\"star\\":\\"1\\"},{\\"color\\":4,\\"id\\":\\"5\\",\\"level\\":\\"39\\",\\"star\\":\\"3\\"},{\\"color\\":4,\\"id\\":\\"19\\",\\"level\\":\\"39\\",\\"star\\":\\"3\\"}]","userId":"-560009","team":[{"color":4,"id":"4","level":"39","star":"3"},{"color":4,"id":"1","level":"39","star":"2"},{"color":4,"id":"9","level":"39","star":"1"},{"color":4,"id":"5","level":"39","star":"3"},{"color":4,"id":"19","level":"39","star":"3"}],"delta":770,"needPower":25679,"power":"24961","attackerType":"hero"}],"defenders":[],"state":1},"reward":[],"maxFloorReached":"230"}',  # noqa

    # language=json
    '{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"221","floorNumber":222,"floorType":"battle","states":{"titans":[]},"floor":{"userData":[{"defenderType":"earth","chance":75,"team":[{"id":4022,"level":30,"star":1},{"id":4020,"level":30,"star":1}],"userId":-3000687,"power":3645,"attackerType":"fire"}],"defenders":[],"state":1},"reward":[],"maxFloorReached":"230"}',  # noqa

    # language=json
    r'{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"221","floorNumber":"229","floorType":"battle","states":{"titans":{"4011":{"hp":51226,"energy":400,"isDead":false,"maxHp":51226},"4010":{"hp":700916,"energy":419,"isDead":false,"maxHp":730477},"4013":{"hp":706524,"energy":600,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":1000,"isDead":false,"maxHp":862389},"4021":{"hp":17045,"energy":200,"isDead":false,"maxHp":17045},"4022":{"hp":109001,"energy":600,"isDead":false,"maxHp":109001},"4020":{"hp":1427675,"energy":504,"isDead":false,"maxHp":1554744},"4002":{"hp":243568,"energy":700,"isDead":false,"maxHp":243568},"4001":{"hp":967440,"energy":400,"isDead":false,"maxHp":967440},"4000":{"hp":479939,"energy":541,"isDead":false,"maxHp":525315}}},"floor":{"userData":[{"defenderType":"hero","chance":1,"arenaHeroesPacked":"p:[{\"id\":7,\"level\":42,\"color\":6,\"star\":2},{\"id\":20,\"level\":41,\"color\":5,\"star\":1},{\"id\":15,\"level\":42,\"color\":6,\"star\":2},{\"id\":2,\"level\":42,\"color\":5,\"star\":1},{\"id\":4,\"level\":42,\"color\":6,\"star\":2}]","userId":"221807","team":[{"id":7,"level":42,"color":6,"star":2},{"id":20,"level":41,"color":5,"star":1},{"id":15,"level":42,"color":6,"star":2},{"id":2,"level":42,"color":5,"star":1},{"id":4,"level":42,"color":6,"star":2}],"delta":782,"needPower":26077,"power":"25365","attackerType":"hero"}],"defenders":[],"state":1},"reward":[],"maxFloorReached":"230"}',  # noqa

    # language=json
    r'{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"231","floorNumber":241,"floorType":"battle","states":{"titans":{"4011":{"hp":51226,"energy":600,"isDead":false,"maxHp":51226},"4010":{"hp":669236,"energy":1000,"isDead":false,"maxHp":730477},"4013":{"hp":706524,"energy":200,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":700,"isDead":false,"maxHp":862389},"4021":{"hp":17045,"energy":1000,"isDead":false,"maxHp":17045},"4022":{"hp":109001,"energy":1000,"isDead":false,"maxHp":109001},"4020":{"hp":1326222,"energy":500,"isDead":false,"maxHp":1554744},"4002":{"hp":243568,"energy":200,"isDead":false,"maxHp":243568},"4001":{"hp":967440,"energy":1000,"isDead":false,"maxHp":967440},"4000":{"hp":382462,"energy":861,"isDead":false,"maxHp":525315}}},"floor":{"userData":[{"defenderType":"hero","chance":1,"arenaHeroesPacked":"p:[{\"id\":2,\"level\":48,\"color\":6,\"star\":1},{\"id\":20,\"level\":49,\"color\":6,\"star\":1},{\"id\":4,\"level\":50,\"color\":6,\"star\":2},{\"id\":6,\"level\":50,\"color\":6,\"star\":1},{\"id\":7,\"level\":50,\"color\":6,\"star\":2}]","userId":"851135","team":[{"id":2,"level":48,"color":6,"star":1},{"id":20,"level":49,"color":6,"star":1},{"id":4,"level":50,"color":6,"star":2},{"id":6,"level":50,"color":6,"star":1},{"id":7,"level":50,"color":6,"star":2}],"delta":785,"needPower":26177,"power":"25462","attackerType":"hero"}],"defenders":[],"state":1},"reward":[],"maxFloorReached":241}',  # noqa

    # language=json
    r'{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"231","floorNumber":"250","floorType":"battle","states":{"titans":{"4011":{"hp":70340,"energy":200,"isDead":false,"maxHp":70340},"4010":{"hp":639100,"energy":629,"isDead":false,"maxHp":750366},"4013":{"hp":706524,"energy":600,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":1000,"isDead":false,"maxHp":862389},"4021":{"hp":17559,"energy":600,"isDead":false,"maxHp":17559},"4022":{"hp":151766,"energy":800,"isDead":false,"maxHp":151766},"4020":{"hp":1258064,"energy":709,"isDead":false,"maxHp":1554744},"4002":{"hp":326806,"energy":400,"isDead":false,"maxHp":326806},"4001":{"hp":967440,"energy":200,"isDead":false,"maxHp":967440},"4000":{"hp":436523,"energy":941,"isDead":false,"maxHp":708451}}},"floor":{"userData":[{"defenderType":"water","chance":50,"team":[{"id":4002,"level":26,"star":2},{"id":4000,"level":27,"star":2}],"userId":-1000915,"power":4377,"attackerType":"earth"},{"defenderType":"fire","chance":50,"team":[{"id":4012,"level":26,"star":2,"buffs":{"hp":3480.3921568627447,"physicalAttack":261.02941176470586}},{"id":4010,"level":26,"star":2,"buffs":{"hp":3480.3921568627447,"physicalAttack":261.02941176470586}}],"userId":-2000890,"power":4330,"attackerType":"water"}],"defenders":{"1":[[]]},"state":2},"reward":[],"maxFloorReached":"250"}',  # noqa
])
def test_dungeon(response: str):
    dataclasses_.Dungeon.parse_obj(loads(response))


@mark.parametrize('response', [
    # language=json
    r'{"reward":{"dungeonActivity":2,"consumable":{"20":50}},"rewardMultiplier":2,"dungeon":{"userId":"833061","elements":{"prime":"fire","nonprime":["water","earth"]},"respawnFloor":"231","floorNumber":242,"floorType":"battle","states":{"titans":{"4011":{"hp":51226,"energy":600,"isDead":false,"maxHp":51226},"4010":{"hp":669236,"energy":1000,"isDead":false,"maxHp":730477},"4013":{"hp":706524,"energy":200,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":700,"isDead":false,"maxHp":862389},"4021":{"hp":17045,"energy":1000,"isDead":false,"maxHp":17045},"4022":{"hp":109001,"energy":1000,"isDead":false,"maxHp":109001},"4020":{"hp":1326222,"energy":500,"isDead":false,"maxHp":1554744},"4002":{"hp":243568,"energy":200,"isDead":false,"maxHp":243568},"4001":{"hp":967440,"energy":1000,"isDead":false,"maxHp":967440},"4000":{"hp":382462,"energy":861,"isDead":false,"maxHp":525315}}},"floor":{"userData":[{"defenderType":"earth","chance":75,"team":[{"id":4021,"level":25,"star":2},{"id":4020,"level":25,"star":2}],"userId":-3000763,"power":4039,"attackerType":"fire"}],"defenders":[],"state":1},"reward":[],"maxFloorReached":242},"states":{"titans":{"4011":{"hp":51226,"energy":600,"isDead":false,"maxHp":51226},"4010":{"hp":669236,"energy":1000,"isDead":false,"maxHp":730477},"4013":{"hp":706524,"energy":200,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":700,"isDead":false,"maxHp":862389},"4021":{"hp":17045,"energy":1000,"isDead":false,"maxHp":17045},"4022":{"hp":109001,"energy":1000,"isDead":false,"maxHp":109001},"4020":{"hp":1326222,"energy":500,"isDead":false,"maxHp":1554744},"4002":{"hp":243568,"energy":200,"isDead":false,"maxHp":243568},"4001":{"hp":967440,"energy":1000,"isDead":false,"maxHp":967440},"4000":{"hp":382462,"energy":861,"isDead":false,"maxHp":525315}}},"dungeonActivity":626}',  # noqa

    # language=json
    '{"reward":{"dungeonActivity":10,"fragmentTitan":{"4021":2}},"rewardMultiplier":2,"states":{"titans":{"4011":{"hp":51226,"energy":600,"isDead":false,"maxHp":51226},"4010":{"hp":669236,"energy":1000,"isDead":false,"maxHp":730477},"4013":{"hp":706524,"energy":200,"isDead":false,"maxHp":706524},"4012":{"hp":862389,"energy":700,"isDead":false,"maxHp":862389},"4021":{"hp":17045,"energy":1000,"isDead":false,"maxHp":17045},"4022":{"hp":109001,"energy":1000,"isDead":false,"maxHp":109001},"4020":{"hp":1326222,"energy":500,"isDead":false,"maxHp":1554744},"4002":{"hp":243568,"energy":200,"isDead":false,"maxHp":243568},"4001":{"hp":967440,"energy":1000,"isDead":false,"maxHp":967440},"4000":{"hp":382462,"energy":861,"isDead":false,"maxHp":525315}}},"dungeonActivity":624}',  # noqa
])
def test_end_dungeon_battle_response(response: str):
    dataclasses_.EndDungeonBattleResponse.parse_obj(loads(response))
