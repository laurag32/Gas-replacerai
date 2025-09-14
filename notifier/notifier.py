import requests
import time
import threading

class Notifier:
    def __init__(self, bot_token, chat_id, watcher=None):
        self.token = bot_token
        self.chat_id = chat_id
        self.watcher = watcher
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0

    def send(self, message: str):
        url = f"{self.api_url}/sendMessage"
        try:
            requests.post(url, json={"chat_id": self.chat_id, "text": message})
        except Exception as e:
            print(f"[Notifier ERROR] {e}")

    def _poll(self):
        while True:
            try:
                resp = requests.get(
                    f"{self.api_url}/getUpdates",
                    params={"offset": self.offset + 1, "timeout": 10}
                ).json()

                if "result" in resp:
                    for update in resp["result"]:
                        self.offset = update["update_id"]

                        if "message" in update and "text" in update["message"]:
                            text = update["message"]["text"].strip()
                            if text == "/start":
                                self.send("🤖 Bot is live and ready! Use /summary anytime to see your earnings.")
                            elif text == "/summary" and self.watcher:
                                self.send(self.watcher.format_summary())
            except Exception as e:
                print(f"[Notifier Poll ERROR] {e}")
            time.sleep(2)

    def start_listener(self):
        t = threading.Thread(target=self._poll, daemon=True)
        t.start()
