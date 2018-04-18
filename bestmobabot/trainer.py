import logging
import sys
import warnings

import click
import coloredlogs

from bestmobabot import constants
from bestmobabot.database import Database
from bestmobabot.model import Trainer


@click.command()
@click.option('-v', '--verbose', is_flag=True, default=False, help='Increase verbosity.')
@click.option('-n', '--n-iterations', type=int, default=constants.N_ITERATIONS, help='Hyper-parameters search iterations.')
@click.option('--n-splits', type=int, default=constants.N_SPLITS, help='K-fold splits.')
def main(verbose: bool, n_iterations: int, n_splits: int):
    """
    Train and generate arena prediction model.
    https://github.com/eigenein/bestmobabot/blob/master/research/bestmoba.ipynb
    """
    coloredlogs.install(
        fmt='%(asctime)s %(levelname)s %(message)s',
        level=(logging.INFO if not verbose else logging.DEBUG),
        stream=sys.stderr,
    )
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    with Database(constants.DATABASE_NAME) as db:
        Trainer(db, n_iterations=n_iterations, n_splits=n_splits, logger=logging.getLogger()).train()


if __name__ == '__main__':
    main()
