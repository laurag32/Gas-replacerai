from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()

RPC = os.getenv("POLYGON_RPC")
PK = os.getenv("PRIVATE_KEY")

class Executor:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(RPC))
        self.wallet_address = self.web3.eth.account.from_key(PK).address

    async def send_tx(self, tx):
        signed = self.web3.eth.account.sign_transaction(tx, PK)
        tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        print(f"[TX SENT] {tx_hash.hex()}")
        return tx_hash
