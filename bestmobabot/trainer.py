import logging
import sys
import warnings

import click

import bestmobabot.logger
from bestmobabot import constants
from bestmobabot.database import Database
from bestmobabot.model import Trainer


@click.command()
@click.option('verbosity', '-v', '--verbose', count=True, help='Increase verbosity.')
@click.option('--n-splits', type=int, default=constants.MODEL_N_SPLITS, help='K-fold splits.')
def main(verbosity: int, n_splits: int):
    """
    Train and generate arena prediction model.
    """
    bestmobabot.logger.install_logging(logging.getLogger(), verbosity, sys.stderr)
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    with Database(constants.DATABASE_NAME) as db:
        Trainer(db, n_splits=n_splits, logger=logging.getLogger()).train()


if __name__ == '__main__':
    main()
