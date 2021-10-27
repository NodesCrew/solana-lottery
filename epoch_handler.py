# coding: utf-8

import config

from lib.rpc import call_rpc
from lib.rpc import get_epoch
from lib.logging import get_logger

import os
import json
import uvloop
import asyncio
import subprocess

from lib.data import Stake
from lib.lottery import handle_tickets


os.makedirs(config.DIR_LOGS, exist_ok=True)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
loop = asyncio.get_event_loop()
logger = get_logger("epoch_handler")


async def get_active_stakes(vote_pubkey: str, epoch_no: int) -> list[Stake]:
    """ Returns all active stakes for vote account
    """
    active_stakes = []      # type: list[Stake]

    params = {
        "method": "getProgramAccounts",
        "params": [
            "Stake11111111111111111111111111111111111111",
            {
                "commitment": "confirmed",
                "encoding": "jsonParsed",
                "filters": [
                    {
                        "memcmp": {
                            "bytes": "3xyZh",
                            "encoding": "binary",
                            "offset": 0
                        }
                    },
                    {
                        "memcmp": {
                            "bytes": vote_pubkey,
                            "encoding": "binary",
                            "offset": 124
                        }
                    }
                ]
            }
        ]
    }

    logger.debug(f"Get stakes to {vote_pubkey}")
    resp = await call_rpc(cluster_rpc=config.RPC_URL, params=params)
    logger.debug(f"Found {len(resp)} stakes to {vote_pubkey}")

    for result in resp:
        stake = Stake.from_json(result)
        logger.debug(
            f"Stake {stake.stake_account} "
            f"{stake.stake_size} lamports "
            f"from {stake.staker} [auth: {stake.withdrawer}] "
            f"activated epoch #{stake.epoch_activated}, "
            f"deactivated epoch #{stake.epoch_deactivated}, "
            f"active in curr epoch: {stake.is_active_at(epoch_no)}, "
            f"active in prev epoch: {stake.is_active_at(epoch_no - 1)}"
        )

        if not stake.is_active_at(epoch_no=epoch_no - 1):
            logger.debug(f"Skip stake: not active in prev epoch")
            continue

        active_stakes.append(stake)

    return active_stakes


async def get_epoch_rewards(vote_pubkey: str, epoch_no: int) -> int:
    """ Get rewards for epoch (in lamports)
    """
    logger.debug(f"Get epoch #{epoch_no} rewards for {vote_pubkey}")

    command = [
        config.BINARY,
        "-um", "vote-account", vote_pubkey,
        "--with-rewards",
        "--num-rewards-epochs", "1",
        "--output", "json"
    ]

    data = subprocess.check_output(command)
    for epoch_info in json.loads(data.decode())["epochRewards"]:
        if epoch_info["epoch"] == epoch_no:
            return epoch_info["amount"]


async def main():
    """ Main function
    """
    logger.debug(f"Engine settings: "
                 f"ORG_PERCENT: {config.ORG_PERCENT}, "
                 f"REW_PERCENT: {config.REW_PERCENT}, "
                 f"LOT_PERCENT: {config.LOT_PERCENT}, "
                 f"TICKET_COST: {config.TICKET_COST}")

    epoch_curr = await get_epoch(config.RPC_URL)
    epoch_prev = epoch_curr - 1
    logger.debug(f"Got epoch #{epoch_curr} from {config.RPC_URL}")

    # Get stakes
    stakes = await get_active_stakes(vote_pubkey=config.VOTE_ACCOUNT,
                                     epoch_no=epoch_prev)
    total_stake = sum(stake.stake_size for stake in stakes)
    clean_stake = sum(stake.stake_size for stake in stakes
                      if stake.withdrawer not in config.STAKERS_BLACKLIST)
    clean_stake_percent = clean_stake / total_stake

    logger.debug(f"Found {len(stakes)} active stakes to {config.VOTE_ACCOUNT}. "
                 f"Total stake: {total_stake}, clean stake: {clean_stake}")

    # Get rewards
    total_rewards = await get_epoch_rewards(vote_pubkey=config.VOTE_ACCOUNT,
                                            epoch_no=epoch_prev)
    clean_rewards = int(clean_stake_percent * total_rewards)

    logger.debug(f"Rewards in epoch #{epoch_prev} for {config.VOTE_ACCOUNT}. "
                 f"Total rewards: {total_rewards}, "
                 f"clean rewards: {clean_rewards}")

    # Set pools
    lot_pool = []
    lot_fund = 0
    rew_pool = []
    for stake in stakes:
        # Skip blacklisted stakers
        if stake.withdrawer in config.STAKERS_BLACKLIST:
            continue

        # stake rewards %
        stake_percent = stake.stake_size / clean_stake
        stake_pie = int(stake_percent * clean_rewards)
        stake_org = int(stake_pie * config.ORG_PERCENT)

        if stake.stake_size > config.TICKET_COST:
            # Participate in lottery & rewards both
            stake_lot = int(stake_pie * config.LOT_PERCENT)
            stake_rew = int(stake_pie * config.REW_PERCENT)
            lot_fund += stake_lot
        else:
            # Do not participate in lottery, if staked less than ticket cost
            stake_lot = 0
            stake_rew = int(stake_pie * (config.REW_PERCENT +
                                         config.LOT_PERCENT))

        logger.debug(f"Staker {stake.withdrawer} extra: "
                     f"stake_pie: {stake_pie}, "
                     f"LOT: {stake_lot}, "
                     f"ORG: {stake_org}, "
                     f"REW: {stake_rew} ")

        if stake_rew:
            logger.debug(f"{stake.withdrawer} participates in rewards and will "
                         f"receive {stake_rew} lamports")
            rew_pool.append((stake, stake_rew))

        if stake_lot:
            tickets_count = int(stake.stake_size / config.TICKET_COST)
            logger.debug(f"{stake.withdrawer} participates in lottery and will "
                         f"receive {tickets_count} tickets")
            lot_pool.append((stake, tickets_count))

    handle_tickets(config.LOT_WIN_TABLE, lot_pool, lot_fund)


if __name__ == "__main__":
    print(config.REW_PERCENT + config.ORG_PERCENT + config.LOT_PERCENT)
    assert (config.REW_PERCENT + config.ORG_PERCENT + config.LOT_PERCENT) == 1


    try:
        srv = loop.run_until_complete(main())
    except KeyboardInterrupt:
        loop.close()
