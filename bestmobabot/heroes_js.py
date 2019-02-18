"""
Node.js & heroes.js interface.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from loguru import logger

from bestmobabot.constants import LIBRARY_URL, NODEJS_TIMEOUT
from bestmobabot.resources import get_heroes_js, get_resource, get_skills_sc


def run_battle(battle_data: Any) -> str:
    footer = FOOTER.format(
        battle_data=json.dumps(battle_data),
        skills_sc=get_skills_sc(),
        library=get_resource(LIBRARY_URL),
    )
    script = f'{HEADER}{get_heroes_js()}{footer}'
    return run_script(script)


def run_script(script: str) -> str:
    logger.info('Running Node.js…')
    process = subprocess.run(
        ['node'],
        input=script,
        encoding='utf-8',
        timeout=NODEJS_TIMEOUT,
        capture_output=True,
    )
    logger.info('Return code: {}.', process.returncode)
    if process.returncode:
        logger.error('Node.js error:\n{}', process.stderr)
    return process.stdout.strip()


HEADER = '''
var window = {
    document: {
        createElement: function() {
            return {
                getContext: function() {
                    return {
                        fillRect: function() {},
                    };
                },
            };
        },
    },
    navigator: {
        userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
    },
    performance: require('perf_hooks').performance,
};

var fs = require('fs');
'''

FOOTER = '''
(function(h) {{
    var response = {battle_data};

    console.error('Listing classes…');
    var Bytes = h['haxe.io.Bytes'];
    var BattleInstantPlay = h['game.battle.controller.instant.BattleInstantPlay'];
    var BattlePresets = h['game.battle.controller.thread.BattlePresets'];
    var DataStorage = h['game.data.storage.DataStorage'];
    var AssetStorage = h['game.assets.storage.AssetStorage'];
    var BattleAssetStorage = h['game.assets.storage.BattleAssetStorage'];
    var BattleLog = h['battle.BattleLog'];

    console.error('Loading skills.sc…');
    AssetStorage.battle = new BattleAssetStorage();
    AssetStorage.battle.loadEncodedCode(new Bytes({skills_sc}));

    console.error('Initialising Pako…');
    h.JsPakoCompression.init();
    pako = module.exports;

    console.error('Initialising data storage…');
    new DataStorage({library});

    console.error('Initialising battle instant play…');
    // TODO: pay attention to `get_tower` and `get_titan`.
    var presets = new BattlePresets(false, false, true, DataStorage.battleConfig.get_tower(), false);
    var play = new BattleInstantPlay(response, presets);
    play.battleData.attackers.initialize(AssetStorage.battle.skillFactory.bind(AssetStorage.battle));
    play.battleData.defenders.initialize(AssetStorage.battle.skillFactory.bind(AssetStorage.battle));

    console.error('Executing the battle…');
    play.executeBattle();

    console.error('Creating result…');
    // Avoid infinite loop in Pako.
    BattleLog.m.bytes.getEncodedString = function() {{ return this.bytes }};
    play.createResult();
    var result = play.get_result();

    console.log(JSON.stringify({{
        result: result.get_result(),
        progress: result.get_progress(),
    }}));
}})(window.h)
'''
