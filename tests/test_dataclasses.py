from __future__ import annotations

from orjson import loads
from pytest import mark

from bestmobabot import dataclasses_
from bestmobabot.resources import get_library


def test_library():
    get_library()


@mark.parametrize('response', [
    # language=json
    r'{}',

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


@mark.parametrize('response', [
    # language=json
    r'{"id":4001,"xp":30420,"level":54,"star":4,"skills":{"4003":54},"power":12648,"artifacts":[{"level":34,"star":2},{"level":1,"star":1},{"level":1,"star":1}],"scale":0.80000000000000004}',  # noqa
])
def test_titan(response: str):
    dataclasses_.Titan.parse_obj(loads(response))


@mark.parametrize('response', [
    # language=json
    r'{"champions":{"5181775":{"userId":"5181775","place":1,"serverId":"7","clanId":"49207","score":"84229","power":"825499","cup":1,"info":{"name":"Faal","level":"130","avatarId":"386","frameId":3,"clanTitle":"Неудержимые NEW","clanIcon":{"flagColor1":16,"flagColor2":19,"flagShape":1,"iconColor":19,"iconShape":5},"serverId":"7","clanId":"49207"}},"5069714":{"userId":"5069714","place":2,"serverId":"2","clanId":"3980","score":"84210","power":"825436","cup":2,"info":{"name":"Бяка","level":"130","avatarId":"305","frameId":3,"clanTitle":"T-Grad","clanIcon":{"flagColor1":16,"flagColor2":0,"flagShape":1,"iconColor":3,"iconShape":10},"serverId":"2","clanId":"3980"}},"1207246":{"userId":"1207246","place":3,"serverId":"11","clanId":"8050","score":"84147","power":"825436","cup":2,"info":{"name":"isaac morris","level":"130","avatarId":"411","frameId":3,"clanTitle":"BewareUs","clanIcon":{"flagColor1":8,"flagColor2":19,"flagShape":14,"iconColor":7,"iconShape":31},"serverId":"11","clanId":"8050"}},"5176560":{"userId":"5176560","place":4,"serverId":"9","clanId":"23928","score":"84047","power":"825499","cup":2,"info":{"name":"68 RUS","level":"130","avatarId":"305","frameId":3,"clanTitle":"NFS","clanIcon":{"flagColor1":0,"flagColor2":3,"flagShape":14,"iconColor":0,"iconShape":46},"serverId":"9","clanId":"23928"}},"5222351":{"userId":"5222351","place":5,"serverId":"3","clanId":"45148","score":"84018","power":"825499","cup":2,"info":{"name":"Бог смерти Рюк","level":"130","avatarId":"374","frameId":3,"clanTitle":"Revolution","clanIcon":{"flagColor1":0,"flagColor2":19,"flagShape":3,"iconColor":8,"iconShape":2},"serverId":"3","clanId":"45148"}},"5355159":{"userId":"5355159","place":6,"serverId":"7","clanId":"49207","score":"83823","power":"825436","cup":2,"info":{"name":"ЛЕГИОН","level":"130","avatarId":"303","frameId":3,"clanTitle":"Неудержимые NEW","clanIcon":{"flagColor1":16,"flagColor2":19,"flagShape":1,"iconColor":19,"iconShape":5},"serverId":"7","clanId":"49207"}},"4944789":{"userId":"4944789","place":7,"serverId":"17","clanId":"20301","score":"83756","power":"820715","cup":2,"info":{"name":"Катастрофа","level":"130","avatarId":"385","frameId":3,"clanTitle":"Paradox","clanIcon":{"flagColor1":0,"flagColor2":0,"flagShape":14,"iconColor":19,"iconShape":12},"serverId":"17","clanId":"20301"}},"4534638":{"userId":"4534638","place":8,"serverId":"22","clanId":"23965","score":"83736","power":"825499","cup":2,"info":{"name":"М_А_К_С","level":"130","avatarId":"303","frameId":3,"clanTitle":"PROTEX","clanIcon":{"flagColor1":9,"flagColor2":7,"flagShape":0,"iconColor":5,"iconShape":14},"serverId":"22","clanId":"23965"}},"5069879":{"userId":"5069879","place":9,"serverId":"34","clanId":"19945","score":"83705","power":"825499","cup":2,"info":{"name":"Артем","level":"130","avatarId":"385","frameId":3,"clanTitle":"Brazzers","clanIcon":{"flagColor1":19,"flagColor2":19,"flagShape":5,"iconColor":3,"iconShape":27},"serverId":"34","clanId":"19945"}},"5182053":{"userId":"5182053","place":10,"serverId":"5","clanId":"24015","score":"83666","power":"821785","cup":2,"info":{"name":"Моль","level":"130","avatarId":"397","frameId":3,"clanTitle":"E-бобо","clanIcon":{"flagColor1":19,"flagColor2":7,"flagShape":14,"iconColor":19,"iconShape":17},"serverId":"5","clanId":"24015"}}},"bestOnServer":false,"bestGuildMembers":[],"result":{"place":"58774","cup":"5"},"key":1550865600,"next":null,"prev":1549850400,"trophy":{"cup":"5","week":"1550455200","place":"58774","serverId":"10","clanId":"15676","championReward":{"coin":{"19":"2"},"gold":"150000"},"championRewardFarmed":0,"serverReward":[],"serverRewardFarmed":0,"clanReward":[],"clanRewardFarmed":0}}',  # noqa
])
def test_hall_of_fame(response: str):
    dataclasses_.HallOfFame.parse_obj(loads(response))
