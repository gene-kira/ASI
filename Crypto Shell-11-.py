import sys, subprocess, requests, time, os
from io import BytesIO
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from matplotlib import pyplot as plt

def autoload():
    required = ['PyQt5', 'requests', 'matplotlib']
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

autoload()

def log_mutation(coin, price, delta, daemon_msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {coin.upper()} ${price:.2f} Δ={delta:.2f} → {daemon_msg}\n"
    os.makedirs("mutation_logs", exist_ok=True)
    with open(f"mutation_logs/{coin}.log", "a") as f:
        f.write(line)

def log_entanglement(state):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {state}\n"
    with open("mutation_logs/quantum.log", "a") as f:
        f.write(line)

def daemon_trigger(price, coin):
    thresholds = {
        'bitcoin': (30000, 25000),
        'ethereum': (2000, 1500),
        'solana': (30, 20),
        'cardano': (0.5, 0.3),
        'dogecoin': (0.1, 0.05),
    }
    high, low = thresholds.get(coin, (None, None))
    if high and price > high:
        return f"📈 {coin.upper()} Surge: Entangled with bullish phase."
    elif low and price < low:
        return f"📉 {coin.upper()} Collapse: Decoherence detected."
    return "🧠 Stable: Quantum equilibrium maintained."

def render_chart(coin, reference_price):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=7"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = requests.get(url, headers=headers).json()['prices']
        timestamps = [time.strftime('%m-%d', time.localtime(p[0] / 1000)) for p in data]
        prices = [p[1] for p in data]

        fig, ax = plt.subplots(figsize=(4, 2), dpi=100)
        color = 'lime' if prices[-1] >= prices[0] else 'red'
        ax.plot(timestamps, prices, color=color)
        ax.axhline(reference_price, color='cyan', linestyle='--', label='Live Price')
        ax.legend(loc='upper left', fontsize=8)
        ax.set_title(f"{coin.upper()} 7-Day Trend", color='white')
        ax.tick_params(axis='x', labelrotation=45)
        ax.set_facecolor('#111')
        fig.patch.set_facecolor('#111')
        for spine in ax.spines.values():
            spine.set_color('#0f0')
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())
        plt.close(fig)
        return pixmap
    except Exception as e:
        print(f"[CHART ERROR] {coin}: {e}")
        return None

def quantum_overlay(polarity, previous):
    directions = {}
    for coin in polarity:
        if coin in previous:
            directions[coin] = "up" if polarity[coin] > previous[coin] else "down"
    base = list(directions.values())[0] if directions else None
    entangled = [c for c, d in directions.items() if d == base]
    if len(entangled) >= 3:
        state = f"🔗 Entanglement: {' + '.join(entangled)} moving {base.upper()} together."
        print(state)
        log_entanglement(state)

class BorgQuantumMultiNode(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Borg ASI Shell — Quantum Multi-Node Mutation")
        self.setStyleSheet("background-color: #111; color: #0f0; font-size: 16px;")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.labels = {}
        self.images = {}
        self.coins = [
            'bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin',
            'polkadot', 'avalanche-2', 'chainlink', 'litecoin', 'uniswap',
            'stellar', 'vechain', 'tron', 'tezos', 'algorand'
        ]
        self.previous = {}
        self.feed_interval = 60
        self.last_feed_time = time.time()

        self.timer_label = QLabel("⏱️ Next feed in: syncing...")
        self.layout.addWidget(self.timer_label)

        self.init_gui()
        self.feed_timer = QTimer()
        self.feed_timer.timeout.connect(self.update_shell)
        self.feed_timer.start(self.feed_interval * 1000)

        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)

    def init_gui(self):
        for coin in self.coins:
            label = QLabel(f"{coin.upper()}: loading...")
            label.setToolTip("Initializing quantum overlay...")
            self.layout.addWidget(label)
            self.labels[coin] = label

            image = QLabel()
            image.setStyleSheet("border: 1px solid #0f0;")
            self.layout.addWidget(image)
            self.images[coin] = image

    def update_countdown(self):
        elapsed = time.time() - self.last_feed_time
        remaining = max(0, int(self.feed_interval - elapsed))
        self.timer_label.setText(f"⏱️ Next feed in: {remaining} seconds")

    def update_shell(self):
        try:
            ids = ",".join(self.coins)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.last_feed_time = time.time()
                polarity = {}
                for coin in self.coins:
                    label = self.labels[coin]
                    image = self.images[coin]

                    if coin in data and 'usd' in data[coin]:
                        price = data[coin]['usd']
                        daemon_msg = daemon_trigger(price, coin)
                        label.setText(f"{coin.upper()}: ${price}")
                        label.setToolTip(daemon_msg)
                        polarity[coin] = price

                        pixmap = render_chart(coin, price)
                        if pixmap:
                            image.setPixmap(pixmap)

                        delta = price - self.previous.get(coin, price)
                        log_mutation(coin, price, delta, daemon_msg)
                        self.previous[coin] = price
                    else:
                        label.setText(f"{coin.upper()}: ⚠️ No USD data")
                        label.setToolTip("🛡️ Mutation shield: API anomaly detected")

                if len(polarity) == len(self.coins):
                    quantum_overlay(polarity, self.previous)
            else:
                print(f"[FEED ERROR] Status code: {response.status_code}")
        except Exception as e:
            print(f"[EXCEPTION] {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = BorgQuantumMultiNode()
    shell.show()
    sys.exit(app.exec_())
