import json
import logging
import sys
from collections import defaultdict
from itertools import chain
from typing import Any, DefaultDict, Dict, Iterable, List, Set, TextIO, Tuple

import click
import coloredlogs
from hyperopt import hp, tpe
from hyperopt.fmin import fmin
from sklearn.ensemble import RandomForestClassifier


@click.command()
@click.argument('log_files', type=click.File('rt'), nargs=-1, required=True)
def main(log_files: Iterable[TextIO]):
    """
    Train and generate arena prediction model.
    https://github.com/eigenein/bestmobabot/blob/master/research/bestmoba.ipynb
    """
    coloredlogs.install(fmt='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, stream=sys.stderr)

    battles = read_battles(log_files)
    ...


def read_battles(log_files: Iterable[TextIO]) -> List[Dict[str, Any]]:
    logging.info('Reading battles…')
    lines = list(chain.from_iterable(log_files))
    battle_set: Set[Tuple[Tuple[str, Any]]] = {tuple(sorted(parse_battle(line).items())) for line in lines}
    battles = [dict(battle) for battle in battle_set]
    logging.info('Read %s unique battles out of %s battles.', len(battles), len(lines))
    return battles


def parse_heroes(heroes: Iterable[Dict[str, int]], sign: int, result: DefaultDict[str, int]):
    for hero in heroes:
        result[f'level_{hero["id"]}'] += sign * hero['level']
        result[f'color_{hero["id"]}'] += sign * hero['color']
        result[f'star_{hero["id"]}'] += sign * hero['star']


def parse_battle(line: str) -> Dict[str, Any]:
    battle = json.loads(line)
    result = defaultdict(int)

    parse_heroes(battle.get('attackers') or battle['player'], +1, result)
    parse_heroes(battle.get('defenders') or battle['enemies'], -1, result)

    return {'win': battle['win'], **result}


if __name__ == '__main__':
    main()
