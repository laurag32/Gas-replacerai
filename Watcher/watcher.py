import time

class Watcher:
    def __init__(self, notifier=None):
        self.start_time = time.time()
        self.harvests = 0
        self.replacements = 0
        self.total_saved_matic = 0.0
        self.total_spent_matic = 0.0
        self.errors = 0
        self.notifier = notifier
        self.last_summary_time = 0

    def log_info(self, msg):
        print(f"[INFO] {msg}")
        if self.notifier:
            self.notifier.send(f"ℹ️ {msg}")

    def log_error(self, msg):
        self.errors += 1
        print(f"[ERROR] {msg}")
        if self.notifier:
            self.notifier.send(f"❌ ERROR: {msg}")

    def record_harvest(self, cost, vault_id):
        self.harvests += 1
        self.total_spent_matic += cost
        msg = f"🌾 Harvested {vault_id} → Spent {cost:.4f} MATIC"
        print(msg)
        if self.notifier:
            self.notifier.send(msg)

    def record_replacement(self, savings, tx_hash):
        self.replacements += 1
        self.total_saved_matic += savings
        msg = f"🔄 Replaced Tx {tx_hash} → Saved {savings:.4f} MATIC"
        print(msg)
        if self.notifier:
            self.notifier.send(msg)

    def format_summary(self):
        uptime = (time.time() - self.start_time) / 3600
        net_profit = self.total_saved_matic - self.total_spent_matic
        return (
            f"=== 📊 BOT SUMMARY ===\n"
            f"Uptime: {uptime:.2f} hrs\n"
            f"Harvests: {self.harvests}\n"
            f"Replacements: {self.replacements}\n"
            f"Total Gas Spent: {self.total_spent_matic:.4f} MATIC\n"
            f"Total Gas Saved: {self.total_saved_matic:.4f} MATIC\n"
            f"Net Profit: {net_profit:.4f} MATIC\n"
            f"Errors: {self.errors}\n"
            f"====================="
        )

    def summary(self, force=False):
        now = time.time()
        if force or now - self.last_summary_time >= 86400:
            if self.notifier:
                self.notifier.send(self.format_summary())
            self.last_summary_time = now
        print(self.format_summary())
