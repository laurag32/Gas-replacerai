from web3 import Web3
import asyncio

class MempoolAdapter:
    def __init__(self, executor, watcher):
        self.executor = executor
        self.watcher = watcher
        self.web3 = executor.web3

    async def run(self):
        try:
            block = self.web3.eth.get_block("pending", full_transactions=True)
            if not block or "transactions" not in block:
                return

            for tx in block.transactions[:5]:
                try:
                    if not hasattr(tx, "gasPrice") or tx.gasPrice is None:
                        continue
                    current_gas = self.web3.eth.gas_price
                    if tx.gasPrice <= current_gas * 2:
                        continue

                    est_cost_orig = (tx.gas * tx.gasPrice) / 1e18
                    est_cost_new = (tx.gas * current_gas) / 1e18
                    savings = est_cost_orig - est_cost_new
                    if savings < 0.001:
                        continue

                    self.watcher.record_replacement(savings, tx.hash.hex())
                    new_tx = {
                        "from": self.executor.wallet_address,
                        "to": tx.to,
                        "value": tx.value,
                        "gas": tx.gas,
                        "gasPrice": current_gas,
                        "nonce": self.web3.eth.get_transaction_count(self.executor.wallet_address),
                    }
                    await self.executor.send_tx(new_tx)
                    await asyncio.sleep(2)

                except Exception as inner_e:
                    self.watcher.log_error(f"Mempool inner error: {inner_e}")

        except Exception as e:
            self.watcher.log_error(f"MempoolAdapter error: {e}")
