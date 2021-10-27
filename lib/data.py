# coding: utf-8
from dataclasses import dataclass

"""
{
"account": {
    "data": {
        "parsed": {
            "info": {
                "meta": {
                    "authorized": {
                        "staker": "8YwntmVByitV71NPUMZDdywwMdGFWEskDusevdt5LQMz",
                        "withdrawer": "EhYXq3ANp5nAerUpbSgd7VK2RRcxK1zNuSQ755G5Mtxx"
                    },
                    "lockup": {
                        "custodian": "3XdBZcURF5nKg3oTZAcfQZg8XEc5eKsx6vK8r3BdGGxg",
                        "epoch": 0,
                        "unixTimestamp": 1809648000
                    },
                    "rentExemptReserve": "2282880"
                },
                "stake": {
                    "creditsObserved": 640918,
                    "delegation": {
                        "activationEpoch": "236",
                        "deactivationEpoch": "18446744073709551615",
                        "stake": "997717120",
                        "voter": "DEmZmtt9bDeDcBMExjKhpCFnA5yj46XbAkzu61CXPKFh",
                        "warmupCooldownRate": 0.25
                    }
                }
            },
            "type": "delegated"
        },
        "program": "stake",
        "space": 200
    },
    "executable": false,
    "lamports": 1000000000,
    "owner": "Stake11111111111111111111111111111111111111",
    "rentEpoch": 236
},
"pubkey": "3vKiBnwPFkEtLDt11e3bKpEVU3sA2Ah6fopA5qnUk193"
}
"""


@dataclass
class Stake:
    stake_size: float
    stake_account: str

    staker: str
    withdrawer: str

    epoch_activated: int
    epoch_deactivated: int

    def is_active_at(self, epoch_no):
        """ Check if stake is active in epoch
        """

        # If stake activated since epoch X, it will be profitable in X + 1
        if epoch_no <= self.epoch_activated:
            # print(f"Not active 1: {epoch_no} <= {self.epoch_activated}")
            return False

        # If stake deactivated since epoch X, it well be removed in X + 1
        if epoch_no > self.epoch_deactivated:
            # print(f"Not active 2: {epoch_no} > {self.epoch_deactivated}")
            return False

        # Looks like an active stake
        return True

    @staticmethod
    def from_json(data):
        info = data["account"]["data"]["parsed"]["info"]
        delegation = info["stake"]["delegation"]

        staker = info["meta"]["authorized"]["staker"]
        withdrawer = info["meta"]["authorized"]["withdrawer"]

        stake_size = int(info["stake"]["delegation"]["stake"])
        epoch_activated = int(delegation["activationEpoch"])
        epoch_deactivated = int(delegation["deactivationEpoch"])

        return Stake(
            stake_size=stake_size,
            stake_account=data["pubkey"],

            epoch_activated=epoch_activated,
            epoch_deactivated=epoch_deactivated,

            staker=staker,
            withdrawer=withdrawer
        )