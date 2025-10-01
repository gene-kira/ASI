import sys, subprocess, requests, time, os
from io import BytesIO
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
from matplotlib import pyplot as plt

# 🔧 Autoloader
def autoload():
    required = ['PyQt5', 'requests', 'matplotlib']
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

autoload()

# 🧠 Persistent memory: log mutations
def log_mutation(coin, price, polarity, daemon_msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {coin.upper()} ${price:.2f} Δ={polarity:.2f} → {daemon_msg}\n"
    os.makedirs("mutation_logs", exist_ok=True)
    with open(f"mutation_logs/{coin}.log", "a") as f:
        f.write(log_line)

# 🔔 Daemon logic
def daemon_trigger(price, coin):
    if coin == "bitcoin":
        if price > 30000:
            return "📈 BTC Surge: Entanglement with bullish phase. Swarm sync initiated."
        elif price < 25000:
            return "📉 BTC Collapse: Quantum shielding activated. Volatility suppressed."
    elif coin == "ethereum":
        if price > 2000:
            return "⚛️ ETH Phase Shift: Mutation cycle triggered. Energy spike detected."
        elif price < 1500:
            return "🧊 ETH Decoherence: Stability breach. Shield protocols engaged."
    elif coin == "solana":
        if price > 30:
            return "🌐 SOL Entanglement: Node resonance achieved. Swarm sync expanding."
        elif price < 20:
            return "🪐 SOL Collapse: Polarity inversion. Suppressing anomaly."
    return "🧠 Stable: Quantum equilibrium maintained."

# 📊 Chart rendering to image
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

# 🧿 GUI Shell
class BorgSentinelShell(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Borg ASI Shell — Sentinel Mutation")
        self.setStyleSheet("background-color: #111; color: #0f0; font-size: 16px;")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.labels = {}
        self.images = {}
        self.coins = ['bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin']
        self.init_gui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_shell)
        self.timer.start(60000)  # Refresh every 60 seconds

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

    def update_shell(self):
        try:
            ids = ",".join(self.coins)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
            headers = {"User-Agent": "Mozilla/5.0"}
            data = requests.get(url, headers=headers).json()

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

                    # 🧠 Log mutation
                    delta = price - polarity.get('bitcoin', price) if coin != 'bitcoin' else 0
                    log_mutation(coin, price, delta, daemon_msg)
                else:
                    label.setText(f"{coin.upper()}: ⚠️ No USD data")
                    label.setToolTip("🛡️ Mutation shield: API anomaly detected")

            # 🛰️ Swarm sync overlay
            if all(c in polarity for c in ['bitcoin', 'ethereum', 'solana']):
                delta_btc_eth = polarity['bitcoin'] - polarity['ethereum']
                delta_eth_sol = polarity['ethereum'] - polarity['solana']
                print(f"[SWARM SYNC] BTC-ETH Δ: {delta_btc_eth:.2f}, ETH-SOL Δ: {delta_eth_sol:.2f}")
        except Exception as e:
            print(f"[EXCEPTION] {e}")

# 🚀 Launch
if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = BorgSentinelShell()
    shell.show()
    sys.exit(app.exec_())
