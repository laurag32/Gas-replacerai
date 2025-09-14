import asyncio
from beefy_adapter import BeefyAdapter
from mempool_adapter import MempoolAdapter
from executor import Executor
from watcher import Watcher
from notifier import Notifier

import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

executor = Executor()
watcher = Watcher()
notifier = Notifier(BOT_TOKEN, CHAT_ID, watcher)
watcher.notifier = notifier
notifier.start_listener()

beefy = BeefyAdapter(executor, watcher)
mempool = MempoolAdapter(executor, watcher)

async def main():
    print("🚀 Bot starting on Polygon...")
    while True:
        try:
            await beefy.run()
            await mempool.run()
        except Exception as e:
            watcher.log_error(f"MAIN LOOP ERROR: {e}")
        finally:
            watcher.summary()
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
