import re, win32gui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_youtube():
    urls = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            m = re.search(r"(https://www\.youtube\.com/watch\?v=[\w-]+)", t)
            if m: urls.append(m.group(1))
    win32gui.EnumWindows(cb, urls)
    return urls[0] if urls else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def setup_browser():
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
        return "ad-showing" in driver.find_element("css selector", ".html5-video-player").get_attribute("class")
    except:
        return False

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
