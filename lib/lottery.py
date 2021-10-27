# coding: utf-8

import random

from .data import Stake
from lib.logging import get_logger

logger = get_logger("lottery")


def handle_tickets(win_table: list, gamers: list[tuple], prize_fund: int):
    """ Handle lottery
    """
    tickets_all = []
    tickets_won = []

    # Check win_table is correct
    assert sum(win_table) == 1.

    if not gamers:
        logger.warn(f"No such tickets for lottery found")
        return

    # Make tickets
    for stake, tickets_count in gamers:
        tickets_all.extend([stake.withdrawer] * tickets_count)

    if not tickets_all:
        logger.warn(f"No such tickets for lottery found")
        return

    logger.debug(f"Total tickets count: "
                 f"{len(tickets_all)}, "
                 f"prize fund: {prize_fund}")

    max_wons = min(len(tickets_all), len(win_table))
    logger.debug(f"Max wons: {max_wons}")

    for pie in win_table:
        prize = int(prize_fund * pie)

        # Select random index of tickets
        idx = random.randint(0, len(tickets_all) - 1)
        logger.debug(f"Tickets random index: {idx}")

        pubkey = tickets_all.pop(idx)

        logger.debug(f"Congradulations for {pubkey}. Prize is {prize} lamports")
        tickets_won.append((pubkey, prize))

        if len(tickets_won) == max_wons:
            logger.debug("End of lottery round")
            break

    for ticket, prize in tickets_won:
        logger.debug(f"Send {prize} lamports to {pubkey}")



