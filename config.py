# coding: utf-8
DIR_LOGS = "log"

# Процент, который остается организаторам лотереи
ORG_PERCENT = 0.10

# Процент, который в любом случае отправляется стейкерам
REW_PERCENT = 0

# Процент, который идет на розыгрыш в лотерее
LOT_PERCENT = 0.90

# Количество выигрышных билетов
LOT_WINS = 3

# Таблица выигрышей (по коэффициентам)
LOT_WIN_TABLE = [0.50, 0.35, 0.15]

# Стоимость лотерейного билета в lamports
TICKET_COST = 1_000_000_000

# cluster = "solana-testnet"
cluster = "solana-mainnet"
# cluster = "velas-mainnet"

if cluster == "solana-mainnet":
    TICKET_COST = 1_000_000_000
    BINARY = "solana"
    RPC_URL = "https://api.mainnet-beta.solana.com"
    VOTE_ACCOUNT = "DEmZmtt9bDeDcBMExjKhpCFnA5yj46XbAkzu61CXPKFh"

    STAKERS_BLACKLIST = {
        "4ZJhPQAgUseCsWhKvJLTmmRRUV74fdoTpQLNfKoekbPY",
    }

elif cluster == "solana-testnet":
    TICKET_COST = 1_000_000_000
    BINARY = "solana"
    RPC_URL = "https://api.testnet.solana.com"
    VOTE_ACCOUNT = "9yGFrCLt4nkQsHq8E5QjWqVPkNgxZe7H3wJPjwbNvp91"

elif cluster == "velas-mainnet":
    TICKET_COST = 100_000_000_000

    BINARY = "velas"
    RPC_URL = "https://api.velas.com"
    VOTE_ACCOUNT = "33PS2djmVjaNm9qrRQ5SYX5qJEiogWzvnVFVaVsZNTci"

    STAKERS_BLACKLIST = {
        "88GDmcoBrU6WF82pSEcwtXhMi7gJFR4RuqMhM27DCeUy",
    }
