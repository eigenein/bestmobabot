import sys
import warnings

import click

import bestmobabot.logging_
from bestmobabot import constants
from bestmobabot.database import Database
from bestmobabot.model import Trainer


@click.command()
@click.option('verbosity', '-v', '--verbose', count=True, help='Increase verbosity.')
@click.option(
    '--n-splits',
    type=int,
    default=constants.MODEL_N_SPLITS, help='K-fold splits.',
    show_default=True,
)
@click.option(
    '--n-last-battles',
    type=int,
    default=constants.MODEL_N_LAST_BATTLES,
    help='Use N last battles for training.',
    show_default=True,
)
def main(verbosity: int, n_splits: int, n_last_battles: int):
    """
    Train and generate arena prediction model.
    """
    bestmobabot.logging_.install_logging(verbosity, sys.stderr)
    if not sys.warnoptions:
        warnings.simplefilter('ignore')

    with Database(constants.DATABASE_NAME) as db:
        Trainer(db, n_splits=n_splits, n_last_battles=n_last_battles).train()


if __name__ == '__main__':
    main()
