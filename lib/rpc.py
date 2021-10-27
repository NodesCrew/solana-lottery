# coding: utf-8
import json
import aiohttp


def fatal_error(message):
    """ Print error and exit
    """
    print("Fatal error: %s" % message)
    exit(1)


async def call_rpc(params, cluster_rpc):
    """ Send request to RPC endpoint and returns result
    """
    payload = {"jsonrpc": "2.0", "id": 1, **params}

    async with aiohttp.ClientSession() as http:
        async with http.post(cluster_rpc, json=payload) as resp:
            resp = await resp.json()
            return resp["result"]


async def get_epoch(cluster_rpc):
    """ Get current epoch number from testnet RPC
    """
    result = await call_rpc({"method": "getEpochInfo"}, cluster_rpc=cluster_rpc)
    return result["epoch"]
