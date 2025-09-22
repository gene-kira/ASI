import re, win32gui, subprocess, sys, importlib

# --- Auto-load Selenium if missing ---
def ensure_selenium():
    try:
        importlib.import_module("selenium")
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
        importlib.import_module("selenium")

def get_youtube():
    urls = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            m = re.search(r"(https://www\.youtube\.com/watch\?v=[\w-]+)", t)
            if m: urls.append(m.group(1))
    win32gui.EnumWindows(cb, urls)
    return urls[0] if urls else "https://www.youtube.com/?app=desktop"

def setup_browser():
    ensure_selenium()
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    for arg in [
        "--disable-infobars", "--mute-audio", "--start-maximized",
        "--disable-notifications", "--disable-popup-blocking"
    ]:
        opts.add_argument(arg)
    driver = webdriver.Chrome(options=opts)
    driver.get(get_youtube())

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        """
    })
    return driver

def is_ad(driver):
    try:
        return driver.execute_script("return document.querySelector('.video-ads')?.childElementCount > 0")
    except:
        return False

def skip_ad(driver):
    try:
        driver.execute_script("""
            let attempts = 0;
            let interval = setInterval(() => {
                let btn = document.querySelector('.ytp-ad-skip-button');
                if (btn) {
                    btn.click();
                    clearInterval(interval);
                }
                attempts++;
                if (attempts > 10) clearInterval(interval);
            }, 500);
        """)
        driver.execute_script("""
            let video = document.querySelector('video');
            if (video && video.paused) video.play();
        """)
        driver.execute_script("""
            document.querySelectorAll('.video-ads, .ytp-ad-module, .ytp-ad-player-overlay').forEach(e => e.remove());
        """)
    except:
        pass

def inject_js(driver, stealth=False):
    driver.execute_script(f"""
        window.addEventListener('load', () => {{
            setTimeout(() => {{
                let cloak = document.createElement('div');
                let shadow = cloak.attachShadow({{mode: 'closed'}});
                document.body.appendChild(cloak);
                document.querySelectorAll('[id*="ad"], [class*="ad"], iframe[src*="ads"]').forEach(e => {{
                    e.style.position = 'absolute';
                    e.style.left = '-9999px';
                    shadow.appendChild(e);
                }});
                {'let bait = document.createElement("div"); bait.className = "adsbox"; bait.style.height = "1px"; bait.style.display = "block"; document.body.appendChild(bait);' if stealth else ''}
            }}, Math.random() * 3000 + 2000);
        }});
    """)
