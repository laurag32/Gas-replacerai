import httpx, asyncio
from web3 import Web3

BEEFY_API = "https://api.beefy.finance/vaults"
BEEFY_STRATEGY_ABI = [
    {"inputs": [], "name": "harvest", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

class BeefyAdapter:
    def __init__(self, executor, watcher):
        self.executor = executor
        self.watcher = watcher
        self.web3 = executor.web3

    async def run(self):
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(BEEFY_API)
                vaults = resp.json()

            for vault in vaults:
                if vault.get("chain") != "polygon":
                    continue
                earn_apr = vault.get("apy", {}).get("net_apy", 0)
                if not earn_apr or earn_apr < 0.05:
                    continue
                strategy = vault.get("strategy")
                if not strategy:
                    continue

                contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(strategy),
                    abi=BEEFY_STRATEGY_ABI
                )

                try:
                    gas_estimate = contract.functions.harvest().estimate_gas({"from": self.executor.wallet_address})
                except Exception:
                    self.watcher.log_info(f"Vault {vault['id']} not profitable or empty.")
                    continue

                gas_price = self.web3.eth.gas_price
                est_cost = gas_estimate * gas_price / 1e18
                if est_cost > 0.01:
                    self.watcher.log_info(f"Skipped {vault['id']} (gas too high: {est_cost:.4f} MATIC)")
                    continue

                self.watcher.record_harvest(est_cost, vault['id'])
                tx = contract.functions.harvest().build_transaction({
                    "from": self.executor.wallet_address,
                    "nonce": self.web3.eth.get_transaction_count(self.executor.wallet_address),
                    "gas": gas_estimate,
                    "gasPrice": gas_price,
                })
                await self.executor.send_tx(tx)
                await asyncio.sleep(5)

        except Exception as e:
            self.watcher.log_error(f"BeefyAdapter error: {e}")
