# ==============================================================================
# DRX WINGO CLUSTER - ULTRA RESILIENT WORKER NODE (512MB RAM PRODUCTION ENGINE)
# ==============================================================================
# Architecture & Capabilities:
# - Strict Single-Core Firefox Process Clamping (<160MB RAM Target Footprint)
# - Linux Malloc Arena Hardening to eradicate fragmentation on Railway Containers
# - Non-Destructive Martingale Math Engine with Uninterrupted 24/7 Cycle Loops
# - Smart State-Diff Telemetry Engine (Prevents Telegram UI Disappearance/FloodWait)
# - Direct New API Integration (next.size & history status for 100% accurate Win/Loss)
# - Python-First API Prediction Bridge with BST (UTC+6) Clock
# - Aggressive Zombie Subprocess Sweeper & Active Kernel-Level Memory Cleaner
# ==============================================================================

import os
import sys

# ০.৫ জিবি র‍্যামে কার্নেল মেমরি ফ্র্যাগমেন্টেশন ও মাল্টি-প্রসেস মেমরি লিক বন্ধকরণ
os.environ["MALLOC_ARENA_MAX"] = "1"
os.environ["MOZ_FORCE_DISABLE_E10S"] = "1"
os.environ["MOZ_HEADLESS"] = "1"
os.environ["PYTHONUNBUFFERED"] = "1"

import subprocess
import time
import threading
import shutil
import json
import socket
import gc
import urllib.request
import urllib.error
import uuid
import logging
import signal
from datetime import datetime, timezone, timedelta

# ==============================================================================
# BANGLADESH STANDARD TIME (BST / UTC+6) TIMEZONE CONFIGURATION
# ==============================================================================
BST_TZ = timezone(timedelta(hours=6))

def bst_now():
    """Returns current Bangladesh Standard Time."""
    return datetime.now(BST_TZ)

def bst_time_converter(*args):
    """Custom logging timestamp converter for BST."""
    return bst_now().timetuple()

logging.Formatter.converter = bst_time_converter

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s BST] [WORKER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WORKER_NODE")

# ==============================================================================
# AUTOMATIC DEPENDENCY BOOTSTRAPPER
# ==============================================================================
def ensure_dependencies():
    packages = [
        ("selenium", "selenium"),
        ("psutil", "psutil"),
        ("requests", "requests"),
        ("urllib3", "urllib3")
    ]
    for pkg_name, import_name in packages:
        try:
            __import__(import_name)
        except ImportError:
            logger.warning(f"Required package '{pkg_name}' missing. Installing...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "--upgrade", "--no-cache-dir", pkg_name
                ])
                logger.info(f"Package '{pkg_name}' successfully installed.")
            except Exception as e:
                logger.error(f"Installation failed for '{pkg_name}': {e}")

ensure_dependencies()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil

# ==============================================================================
# UNICODE TYPOGRAPHY & VIP STYLING
# ==============================================================================
VIP_ALPHA_MAP = {
    c: v for c, v in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")
}
BOLD_DIGIT_MAP = {d: v for d, v in zip("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")}
SUBSCRIPT_DIGIT_MAP = {d: v for d, v in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉")}

def to_vip_text(text: str) -> str:
    return "".join(VIP_ALPHA_MAP.get(c.upper(), c) if c.isalpha() else c for c in str(text))

def to_bold_digits(val) -> str:
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

def to_subscript_digits(val) -> str:
    return "".join(SUBSCRIPT_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# GLOBAL RUNTIME CONFIGURATION (নতুন এপিআই সংযুক্ত)
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json")
HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() == "true"

custom_arg = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if custom_arg:
    if custom_arg.isdigit():
        WORKER_ALIAS = f"W-{int(custom_arg):02d}"
    else:
        WORKER_ALIAS = custom_arg.upper()
    NODE_ID = f"worker_{WORKER_ALIAS}_{uuid.uuid4().hex[:4]}"
else:
    WORKER_ALIAS = f"W-{uuid.uuid4().hex[:4].upper()}"
    NODE_ID = f"worker_{WORKER_ALIAS}_{os.getpid()}"

cached_latency = 45.0

PROFILES_BASE_DIR = os.path.expanduser("/tmp/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

active_sessions = {}
WORKER_ACTIVE = True

PLATFORMS = {
    "site_amarclub": {
        "name": "Amar Club",
        "login": "https://amarclub1.com/#/login",
        "wingo": "https://amarclub1.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_dkwin": {
        "name": "DK Win",
        "login": "https://dkwin6.com/#/login",
        "wingo": "https://dkwin6.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    }
}

# ==============================================================================
# DEVICE LOCAL HTML BRIDGE GENERATOR
# ==============================================================================
def create_local_prediction_bridge_html():
    """ডিভাইসে স্বয়ংক্রিয়ভাবে টাইমার এবং নতুন এপিআই সমন্বিত লোকাল HTML পেজ তৈরি করে।"""
    bridge_path = os.path.join(PROFILES_BASE_DIR, "drx_prediction_bridge.html")
    html_content = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DRX WINGO PREDICTION & TIMER ENGINE</title>
    <style>
        body {{
            background: #0d1117;
            color: #58a6ff;
            font-family: 'Courier New', monospace;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }}
        .card {{
            background: #161b22;
            border: 2px solid #30363d;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            width: 320px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
        }}
        #timer {{
            font-size: 42px;
            font-weight: bold;
            color: #39d353;
            margin: 15px 0;
            text-shadow: 0 0 10px rgba(57,211,83,0.5);
        }}
        .signal-box {{
            font-size: 24px;
            font-weight: bold;
            color: #f0883e;
            margin: 10px 0;
        }}
        .status {{
            font-size: 13px;
            color: #8b949e;
        }}
        .bst-clock {{
            font-size: 12px;
            color: #388bfd;
            margin-top: 8px;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div>⚡ DRX VIP TIMER ENGINE ⚡</div>
        <div id="timer">00:30</div>
        <div class="signal-box" id="prediction-box">PRED: WAITING</div>
        <div class="status" id="rate-box">CONFIDENCE: --%</div>
        <div class="status" id="status-box">SYSTEM READY</div>
        <div class="bst-clock" id="clock-bst">BST: --:--:--</div>
    </div>

    <script>
        const API_URL = "{PREDICTION_API_URL}";
        let lastTriggeredCycle = null;

        function getBSTDate() {{
            const d = new Date();
            const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
            return new Date(utc + (3600000 * 6));
        }}

        function updateTimer() {{
            const nowBst = getBSTDate();
            const seconds = nowBst.getSeconds();
            const remainingSeconds = 30 - (seconds % 30);
            const displaySec = remainingSeconds === 30 ? 0 : remainingSeconds;
            
            document.getElementById("timer").innerText = `00:${{String(displaySec).padStart(2, '0')}}`;
            
            const hours = String(nowBst.getHours()).padStart(2, '0');
            const minutes = String(nowBst.getMinutes()).padStart(2, '0');
            const secStr = String(seconds).padStart(2, '0');
            document.getElementById("clock-bst").innerText = `BST: ${{hours}}:${{minutes}}:${{secStr}}`;
            return displaySec;
        }}

        function resolvePrediction(data) {{
            if (data && data.next && data.next.size) {{
                let s = String(data.next.size).toUpperCase().trim();
                return s.includes('SMALL') ? 'SMALL' : 'BIG';
            }}
            if (data && data.next && data.next.pred) {{
                let s = String(data.next.pred).toUpperCase().trim();
                return s.includes('SMALL') ? 'SMALL' : 'BIG';
            }}
            return "BIG";
        }}

        async function fetchPrediction() {{
            try {{
                document.getElementById('status-box').innerText = "FETCHING SIGNAL...";
                let res = await fetch(API_URL + "?t=" + Date.now());
                if (!res.ok) return;
                let data = await res.json();
                let pred = resolvePrediction(data);
                let conf = (data.next && data.next.confidence) || (data.stats && data.stats.accuracy) || 85;
                
                document.getElementById('prediction-box').innerText = "PRED: " + pred;
                document.getElementById('rate-box').innerText = "CONFIDENCE: " + conf + "%";
                document.getElementById('status-box').innerText = "DISPATCHED TO WORKER";
                localStorage.setItem('drx_latest_pred', JSON.stringify({{ pred: pred, confidence: conf, period: (data.next ? data.next.period : ''), time: Date.now() }}));
            }} catch(e) {{
                document.getElementById('status-box').innerText = "FETCH ERROR - RETRYING";
            }}
        }}

        setInterval(() => {{
            let rem = updateTimer();
            let cycle = Math.floor(Date.now() / 30000);
            if (rem >= 16 && rem <= 22 && lastTriggeredCycle !== cycle) {{
                lastTriggeredCycle = cycle;
                fetchPrediction();
            }}
        }}, 1000);
        updateTimer();
    </script>
</body>
</html>
"""
    try:
        with open(bridge_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info(f"Local Prediction Bridge HTML generated at: {bridge_path}")
    except Exception as e:
        logger.error(f"Failed to generate bridge HTML: {e}")

create_local_prediction_bridge_html()

# ==============================================================================
# FIREBASE RESILIENT SYNCHRONIZER
# ==============================================================================
def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 3.5):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        raw_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=raw_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_content = response.read()
            if res_content:
                return json.loads(res_content.decode("utf-8"))
            return None
    except Exception:
        return None

def measure_network_latency(url: str, timeout: float = 3.0) -> float:
    try:
        start_ts = time.time()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response.read(128)
        return round((time.time() - start_ts) * 1000, 2)
    except Exception:
        return 9999.0

def emit_event_to_manager(event_type: str, data: dict):
    payload = {
        "type": event_type,
        "worker_id": NODE_ID,
        "timestamp": time.time(),
        "time_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST"),
        **data
    }
    firebase_sync_http(f"manager_events/{uuid.uuid4().hex[:10]}", "PUT", payload)

# ==============================================================================
# GUARANTEED PROCESS TEARDOWN & ACTIVE RAM SWEEPER
# ==============================================================================
def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.kill()
            except Exception:
                pass
        parent.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except Exception as e:
        logger.debug(f"Process kill notification: {e}")

def cleanup_zombie_browsers():
    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                pname = (proc.info['name'] or '').lower()
                if 'firefox' in pname or 'geckodriver' in pname:
                    if proc.info['ppid'] == 1 or proc.info['ppid'] == current_pid:
                        is_active = False
                        for s in list(active_sessions.values()):
                            d = s.get('driver')
                            if d and hasattr(d, 'service') and d.service and hasattr(d.service, 'process'):
                                if d.service.process and d.service.process.pid == proc.info['pid']:
                                    is_active = True
                                    break
                        if not is_active:
                            try:
                                proc.kill()
                            except Exception:
                                pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

def enforce_low_ram_guard():
    try:
        mem = psutil.virtual_memory()
        if mem.percent > 80.0:
            logger.warning(f"Memory threshold high: {mem.percent}%! Enforcing GC dump...")
            gc.collect()
            for s in list(active_sessions.values()):
                d = s.get("driver")
                if d:
                    try:
                        d.execute_script("if (window.performance && window.performance.memory) { window.gc && window.gc(); }")
                    except Exception:
                        pass
    except Exception:
        pass

def terminate_session_cleanly(session_id):
    logger.info(f"Initiating clean slot teardown for session: {session_id}")
    sess = active_sessions.pop(session_id, None)
    if sess:
        sess["is_trading"] = False
        driver = sess.get("driver")
        driver_pid = None

        if driver:
            try:
                if hasattr(driver, 'service') and driver.service and driver.service.process:
                    driver_pid = driver.service.process.pid
            except Exception:
                pass

            try:
                driver.execute_script("""
                    if (window.__WINGO_ST) {
                        window.__WINGO_ST.isRun = false;
                        if (window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt);
                        if (window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt);
                    }
                    let hud = document.getElementById('drx-prediction-hud');
                    if (hud) hud.remove();
                """)
            except Exception:
                pass

            try:
                driver.quit()
            except Exception:
                pass

            if driver_pid:
                kill_process_tree(driver_pid)

        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

    cleanup_zombie_browsers()
    gc.collect()

    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
        "status": "FREE",
        "assigned_user_id": None,
        "session_id": None,
        "task": None,
        "load": len(active_sessions)
    })
    logger.info(f"Slot cleared successfully. Worker {NODE_ID} ready for new tasks.")

# ==============================================================================
# HARDENED BROWSER SESSION ISOLATION (0.5GB RAILWAY SAFE)
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data structure missing.")

    cleanup_zombie_browsers()
    enforce_low_ram_guard()

    profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir, ignore_errors=True)
    os.makedirs(profile_dir, exist_ok=True)

    options = Options()
    if HEADLESS_MODE:
        options.add_argument("--headless")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--width=400")
    options.add_argument("--height=800")
    options.page_load_strategy = 'eager'
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("dom.ipc.processCount", 1)
    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 512)
    options.set_preference("javascript.options.mem.max", 24576)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("browser.cache.memory.capacity", 1024)
    options.set_preference("network.http.use-cache", False)
    options.set_preference("network.prefetch-next", False)
    options.set_preference("webgl.disabled", True)
    options.set_preference("accessibility.force_disabled", 1)
    options.set_preference("toolkit.telemetry.enabled", False)
    options.set_preference("dom.disable_open_during_load", True)
    options.set_preference("dom.popup_maximum", 0)
    options.set_preference("media.peerconnection.enabled", False)
    options.set_preference("media.navigator.enabled", False)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(18)
    driver.implicitly_wait(1.5)
    driver.set_window_size(400, 800)

    try:
        driver.get(target_url)
    except Exception as e:
        logger.warning(f"Initial navigation alert for {target_url}: {e}")

    sess["driver"] = driver
    sess["window_handle"] = driver.current_window_handle
    sess["last_activity"] = time.time()
    return driver, sess["window_handle"]

def safe_tab_execute(sid, task_fn, timeout=20.0):
    sess = active_sessions.get(sid)
    if not sess:
        return None

    lock = sess.get("lock")
    driver = sess.get("driver")

    if not driver or not lock:
        return None

    if not lock.acquire(timeout=4.0):
        return None

    result_container = {"res": None, "error": None, "completed": False}

    def execute_worker():
        try:
            result_container["res"] = task_fn(driver)
            result_container["completed"] = True
            sess["last_activity"] = time.time()
        except Exception as e:
            result_container["error"] = e

    worker_thread = threading.Thread(target=execute_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout)

    try:
        lock.release()
    except RuntimeError:
        pass

    if not result_container["completed"]:
        return None

    if result_container["error"]:
        err_msg = str(result_container["error"])
        if "unexpectedly closed" in err_msg or "connection" in err_msg:
            logger.error(f"Driver connection alert: {err_msg}")
        return None

    return result_container["res"]

# ==============================================================================
# INJECTED JAVASCRIPT AUTOMATION
# ==============================================================================
MODAL_AUTO_DISMISSER_JS = """
(function(){
    const sweepModals = () => {
        const targetBonusDialogs = document.querySelectorAll('.announcement-box, .dialog-box, .bonus-dialog, .van-popup, .van-dialog');
        targetBonusDialogs.forEach(dialog => {
            const txt = (dialog.innerText || '').toLowerCase();
            if (txt.includes('announcement') || txt.includes('bonus') || txt.includes('usdt') || txt.includes('notice') || txt.includes('welcome')) {
                const confBtn = dialog.querySelector('button, .van-button, .van-dialog__confirm, div[role="button"]');
                if (confBtn) {
                    try { confBtn.click(); } catch(e){}
                }
                try { dialog.remove(); } catch(e){}
            }
        });

        const directSelectors = [
            '.van-dialog__confirm', '.dialog-confirm', '.van-button--primary',
            '.van-popup__close-icon', '.van-overlay', '.dialog-close', '.close-btn',
            'button[class*="close" i]', 'button[class*="confirm" i]', 'div[class*="close" i]',
            '.announcement-box .close', '.modal-mask', '.reward-receive-btn',
            'button.van-dialog__cancel', '.van-button--danger'
        ];
        directSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                if (el && el.offsetParent !== null && !el.closest('#sys-core-fin') && !el.closest('#drx-prediction-hud')) {
                    try { 
                        ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
                            el.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window}));
                        });
                        el.click(); 
                    } catch(e){}
                }
            });
        });

        const clickableNodes = document.querySelectorAll('button, div[role="button"], span, p, a');
        clickableNodes.forEach(node => {
            if (node && node.offsetParent !== null && !node.closest('#sys-core-fin') && !node.closest('#drx-prediction-hud')) {
                const txt = (node.innerText || '').trim().toLowerCase();
                if (txt === 'confirm' || txt === 'receive' || txt === 'got it' || txt === '確定' || txt === 'close' || txt === 'ok') {
                    try { node.click(); } catch(e){}
                }
            }
        });

        document.querySelectorAll('.van-overlay, .van-dialog, .modal-backdrop').forEach(overlay => {
            if (overlay && overlay.offsetParent !== null && !overlay.closest('#sys-core-fin') && !overlay.closest('#drx-prediction-hud')) {
                try { overlay.remove(); } catch(e){}
            }
        });
    };

    sweepModals();
    if (!window.__SWEEPER_INTERVAL) {
        window.__SWEEPER_INTERVAL = setInterval(sweepModals, 1500);
    }
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
    window.location.hash = '#/login';
}

const dismissInitial = () => {
    document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm" i], .van-button--primary, .van-popup__close-icon').forEach(btn => {
        try { btn.click(); } catch(e){}
    });
};
dismissInitial();

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input');

let elP = document.querySelector('input[type="password"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input');

let elL = document.querySelector('button[type="submit"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');

if (!elN || !elP || !elL) {
    return "NOT_READY";
}

const clearAndSet = (el, val) => {
    el.focus();
    el.value = '';
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (setter) {
        setter.call(el, val);
    } else {
        el.value = val;
    }
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
};

clearAndSet(elN, phone);

setTimeout(() => {
    clearAndSet(elP, pass);
    setTimeout(() => {
        ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
            try { elL.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window})); } catch(e){}
        });
        elL.click();
    }, 350);
}, 350);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const dText = dialog.innerText || '';
    if (dText.includes('already logged in') || dText.includes('somewhere else') || 
        dText.includes('logged in') || dText.includes('22') || dText.includes('other device') ||
        dText.includes('Confirm') || dText.includes('Determine') || dText.includes('continue')) {
        const confirmBtn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm" i], .van-button--danger, .van-button--primary, button');
        if (confirmBtn) {
            try { confirmBtn.click(); } catch(e){}
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed device prompt" };
        }
    }
}

document.querySelectorAll('.van-dialog__confirm, .dialog-confirm, button[class*="confirm" i], button[class*="close" i], .van-popup__close-icon').forEach(b => {
    try { b.click(); } catch(e){}
});

try {
    const t1 = localStorage.getItem('token') || localStorage.getItem('token_str') || localStorage.getItem('auth');
    const t2 = sessionStorage.getItem('token') || sessionStorage.getItem('auth');
    if (t1 || t2) return { status: "SUCCESS" };
} catch(e){}

if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) {
    return { status: "SUCCESS" };
}

const toast = document.querySelector('.van-toast--text, .van-toast--fail, .van-toast');
if (toast && toast.innerText && toast.innerText.trim().length > 0) {
    const t = toast.innerText.trim();
    if (t.includes('already logged in') || t.includes('somewhere else') || t.includes('22')) {
        const loginBtn = document.querySelector('button[type="submit"], body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');
        if (loginBtn) {
            try { loginBtn.click(); } catch(e){}
        }
        return { status: "PENDING", message: "Handling session takeover..." };
    }
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('Account does not exist') || t.includes('frozen')) {
        return { status: "ERROR", message: t };
    }
}

return { status: "PENDING" };
"""

WINGO_PERSISTENT_NAV_JS = """
const targetUrl = arguments[0];

(function(){
    document.querySelectorAll('.announcement-box, .bonus-dialog, .van-overlay, .van-dialog').forEach(el => {
        try {
            const btn = el.querySelector('button, .van-button--primary');
            if (btn) btn.click();
            el.remove();
        } catch(e){}
    });

    const currentHash = window.location.hash || '';
    const currentHref = window.location.href || '';
    const bodyTxt = document.body ? document.body.innerText : '';

    if (currentHash.includes('WinGo') || currentHref.includes('WinGo') || bodyTxt.includes('Time remaining') || bodyTxt.includes('30S') || bodyTxt.includes('Win Go')) {
        return "ALREADY_VERIFIED";
    }

    try {
        if (!window.location.href.includes('WinGo')) {
            window.location.href = targetUrl;
        }
    } catch(e){}

    const s = [
        'img[src*="wingo" i]', 'img[alt*="wingo" i]',
        'body > div > div:nth-of-type(2) > div:nth-of-type(2) > div:nth-of-type(7) > div:nth-of-type(3) > div > div:nth-of-type(2) > div > div > div > img',
        'body > div > div:nth-of-type(3) > div:nth-of-type(5) > div:nth-of-type(2) > div:nth-of-type(3) > div > div > div > img',
        'body > div > div:nth-of-type(2) > div:nth-of-type(5) > div:nth-of-type(2) > div > div',
        'div[class*="lottery" i]', 'div[class*="wingo" i]'
    ];
    for (let i = 0; i < s.length; i++) {
        let el = document.querySelector(s[i]);
        if (el && el.offsetParent !== null) {
            ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
                try { el.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window})); } catch(err){}
            });
            try { el.click(); } catch(err){}
            return "CLICKED_SELECTOR";
        }
    }

    return "NAV_INJECTED";
})();
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';

document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close" i], .van-dialog button').forEach(btn => {
    try { btn.click(); } catch(e){}
});

if (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Win Go') || bodyText.includes('30S') || bodyText.includes('Time remaining')) {
    return true;
}
return false;
"""

FETCH_BALANCE_JS = r"""
let reloadBtn = document.querySelector('.van-icon-replay, .reload-icon, .Wallet__balance-icon, [class*="reload" i], [class*="refresh" i]');
if (reloadBtn) {
    try { reloadBtn.click(); } catch(e){}
}
let targetedEls = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
for (let i = 0; i < targetedEls.length; i++) {
    let txt = targetedEls[i].innerText || '';
    let match = txt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
    if (match) return parseFloat(match[1].replace(/,/g, ''));
}
let els = document.querySelectorAll('span, div, p');
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.includes('Wallet balance') || txt.includes('Balance')) {
        let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
        let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
        if (match) return parseFloat(match[1].replace(/,/g, ''));
    }
}
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)) {
        return parseFloat(txt.replace(/[^\d.]/g, ''));
    }
}
return 0.0;
"""

# ==============================================================================
# INTEGRATED ENGINE (নতুন এপিআই লজিক ও রিয়েল এপিআই উইন/লস কাউন্টিং)
# ==============================================================================
WINGO_CORE_JS = r"""
const autoTargetGoal = parseFloat(arguments[0]) || 0;
const autoTotalSteps = parseInt(arguments[1]) || 5;
const predictionApiUrl = arguments[2] || "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json";

(function(){
    let hud = document.getElementById('drx-prediction-hud');
    if (!hud) {
        hud = document.createElement('div');
        hud.id = 'drx-prediction-hud';
        hud.style.cssText = 'position:fixed;top:8px;right:8px;z-index:999999;background:rgba(13,17,23,0.92);border:1px solid #30363d;border-radius:8px;padding:8px;color:#58a6ff;font-family:monospace;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.6);width:155px;pointer-events:none;';
        hud.innerHTML = `
            <div style="font-size:10px;font-weight:bold;color:#f0883e;">DRX VIP ENGINE (BST)</div>
            <div id="timer" style="font-size:24px;font-weight:bold;color:#39d353;margin:2px 0;">00:30</div>
            <div id="hud-signal" style="font-size:13px;font-weight:bold;color:#ffffff;">SIGNAL: --</div>
            <div id="hud-rate" style="font-size:10px;color:#8b949e;">CONFIDENCE: --%</div>
            <div id="hud-bst-time" style="font-size:9px;color:#58a6ff;margin-top:2px;">BST: --:--:--</div>
        `;
        document.body.appendChild(hud);
    }

    let ghostContainer = document.getElementById('sys-core-fin');
    if (!ghostContainer) {
        ghostContainer = document.createElement('div');
        ghostContainer.id = 'sys-core-fin';
        ghostContainer.setAttribute('style', 'display: none !important; opacity: 0 !important; pointer-events: none !important; position: fixed !important; top: -9999px !important; left: -9999px !important; width: 0 !important; height: 0 !important; z-index: -9999 !important; overflow: hidden !important;');
        document.body.appendChild(ghostContainer);
    }

    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, autoTotalSteps);
        if (autoTargetGoal > 0) {
            window.__WINGO_ST.tgtAmt = autoTargetGoal;
        }
        return "ALREADY_RUNNING_UPDATED";
    }

    if (window.__WINGO_ST) {
        if (window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt);
        if (window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt);
    }

    const st = {
        isRun: true,
        tgtAmt: autoTargetGoal,
        startBal: 0.0,
        curBal: 0.0,
        autoInt: null,
        timerInt: null,
        isTrd: false,
        targetReached: false,
        stpIdx: 0,
        steps: Math.max(1, autoTotalSteps),
        dynSeq: [],
        tradesDone: 0,
        lastPred: null,
        lastBetPeriod: null,
        lastBetAmt: 0,
        preBetBalance: 0.0,
        evaluatedPeriod: null,
        lastTriggeredCycle: null,
        circuitBreakerTriggered: false,
        w: 0,
        l: 0,
        cur_w_streak: 0,
        cur_l_streak: 0,
        max_w_streak: 0,
        max_l_streak: 0
    };
    window.__WINGO_ST = st;

    function getBSTDate() {
        const d = new Date();
        const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
        return new Date(utc + (3600000 * 6));
    }

    function triggerBalanceRefresh() {
        try {
            let refreshBtns = document.querySelectorAll('.van-icon-replay, .reload-icon, .Wallet__balance-icon, [class*="reload" i], [class*="refresh" i], img[src*="reload" i]');
            for (let b of refreshBtns) {
                if (b && b.offsetParent !== null) {
                    b.click();
                    break;
                }
            }
        } catch(e){}
    }

    function chkBal() {
        try {
            triggerBalanceRefresh();
            let targeted = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
            for (let i = 0; i < targeted.length; i++) {
                let txt = targeted[i].innerText || '';
                let match = txt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                if (match) {
                    let num = parseFloat(match[1].replace(/,/g, ''));
                    if (num > 0) {
                        st.curBal = num;
                        return num;
                    }
                }
            }
            let els = document.querySelectorAll('span, div, p');
            for (let i = 0; i < els.length; i++) {
                let txt = els[i].innerText || '';
                if (txt.includes('Wallet balance') || txt.includes('Balance')) {
                    let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
                    let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                    if (match) {
                        st.curBal = parseFloat(match[1].replace(/,/g, ''));
                        return st.curBal;
                    }
                }
            }
        } catch(e) {}
        return st.curBal || 0.0;
    }

    function isTargetAchieved() {
        if (st.targetReached) return true;
        let b = chkBal();
        if (st.tgtAmt > 0 && st.startBal > 0 && (b >= st.tgtAmt || st.curBal >= st.tgtAmt)) {
            st.targetReached = true;
            st.isRun = false;
            st.isTrd = false;
            if (st.autoInt) clearInterval(st.autoInt);
            if (st.timerInt) clearInterval(st.timerInt);
            return true;
        }
        return false;
    }

    function updateTimer() {
        const nowBst = getBSTDate();
        const seconds = nowBst.getSeconds();
        const remainingSeconds = 30 - (seconds % 30);
        const displaySec = remainingSeconds === 30 ? 0 : remainingSeconds;

        let timerEl = document.getElementById("timer");
        if (timerEl) {
            timerEl.innerText = `00:${String(displaySec).padStart(2, '0')}`;
        }
        let bstEl = document.getElementById("hud-bst-time");
        if (bstEl) {
            let h = String(nowBst.getHours()).padStart(2, '0');
            let m = String(nowBst.getMinutes()).padStart(2, '0');
            let s = String(seconds).padStart(2, '0');
            bstEl.innerText = `BST: ${h}:${m}:${s}`;
        }
        return displaySec;
    }

    function getLiveRoundId() {
        try {
            let pEl = document.querySelector('.Game__C-title-sub, .Time__C-num, [class*="period" i], [class*="issue" i]');
            if (pEl) {
                let m = (pEl.innerText || '').match(/(\d{10,24})/);
                if (m) return m[1];
            }
            let allTextEls = document.querySelectorAll('div, span, p, h3');
            for (let i = 0; i < allTextEls.length; i++) {
                let t = (allTextEls[i].innerText || '').trim();
                if (/^20\d{10,20}$/.test(t) && allTextEls[i].children.length === 0) {
                    return t;
                }
            }
        } catch(e){}
        return 'EPOCH_' + Math.floor(Date.now() / 30000);
    }

    const calcSeq = (balanceVal, stepsCountVal) => {
        let balance = parseFloat(balanceVal) || 100;
        let stepsCount = parseInt(stepsCountVal) || 5;
        if (stepsCount < 1) stepsCount = 1;

        const sumPowers = Math.pow(2, stepsCount) - 1;
        const firstStep = balance / sumPowers;

        let steps = [];
        let total = 0;

        for (let i = 0; i < stepsCount; i++) {
            let step = firstStep * Math.pow(2, i);
            let roundedStep = Math.max(1, Math.round(step));
            steps.push(roundedStep);
            total += roundedStep;
        }

        const roundingError = Math.round(balance - total);
        if (roundingError !== 0 && steps.length > 0) {
            steps[stepsCount - 1] = Math.max(1, steps[stepsCount - 1] + roundingError);
        }
        return steps;
    };

    const drx_simClick = (el) => {
        if (!el) return;
        ['pointerdown', 'mousedown', 'touchstart', 'pointerup', 'mouseup', 'touchend', 'click'].forEach(evt => {
            try {
                el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            } catch(e) {}
        });
        if (typeof el.click === 'function') {
            try { el.click(); } catch(e) {}
        }
    };

    // নতুন এপিআই থেকে সরাসরি প্রেডিকশন এক্সট্র্যাক্টর
    function resolvePredictionFromApi(rawJson) {
        if (!rawJson) return { pred: 'BIG', rate: 80, period: null, pattern: '' };

        if (rawJson.next) {
            let rawP = String(rawJson.next.size || rawJson.next.pred || '').toUpperCase().trim();
            let normP = rawP.includes('SMALL') ? 'SMALL' : 'BIG';
            let conf = parseInt(rawJson.next.confidence) || (rawJson.stats ? parseInt(rawJson.stats.accuracy) : 85);
            return {
                pred: normP,
                rate: conf,
                period: rawJson.next.period ? String(rawJson.next.period) : null,
                pattern: rawJson.next.pattern || ''
            };
        }

        if (rawJson.top_engine && rawJson.top_engine.prediction) {
            let p = String(rawJson.top_engine.prediction).toUpperCase().trim();
            return { pred: p.includes('SMALL') ? 'SMALL' : 'BIG', rate: 70, period: null, pattern: '' };
        }
        return { pred: 'BIG', rate: 50, period: null, pattern: '' };
    }

    const exeTrdFast = (pred, amt, cb) => {
        if (isTargetAchieved() || !st.isRun) {
            if (cb) cb(false);
            return;
        }

        try {
            let lingeringDialog = document.querySelector('.van-dialog, .announcement-box');
            if (lingeringDialog) {
                let cBtn = lingeringDialog.querySelector('.van-dialog__confirm, button');
                if (cBtn) try { cBtn.click(); } catch(e){}
                try { lingeringDialog.remove(); } catch(e){}
            }

            let targetText = String(pred).toLowerCase().trim();
            let btn = null;
            let btns = document.querySelectorAll('button, div, span');
            for (let i = 0; i < btns.length; i++) {
                let t = (btns[i].innerText || '').trim().toLowerCase();
                if (t === targetText && btns[i].offsetParent && !btns[i].children.length) {
                    btn = btns[i];
                    break;
                }
            }
            if (!btn) {
                if (targetText === 'big') btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
                else if (targetText === 'small') btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
            }
            if (!btn) {
                if (cb) cb(false);
                return;
            }

            drx_simClick(btn);

            setTimeout(() => {
                if (isTargetAchieved() || !st.isRun) {
                    if (cb) cb(false);
                    return;
                }

                let inpEl = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input");
                if (inpEl) {
                    inpEl.focus();
                    let setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                    if (setV) setV.call(inpEl, String(amt));
                    else inpEl.value = amt;
                    inpEl.dispatchEvent(new Event('input', { bubbles: true }));
                    inpEl.dispatchEvent(new Event('change', { bubbles: true }));
                }

                setTimeout(() => {
                    if (isTargetAchieved() || !st.isRun) {
                        if (cb) cb(false);
                        return;
                    }

                    let dEl = document.querySelector('button.bet-amount, button[class*="bet-amount"], .Betting__C-foot-total, .van-button--danger, .van-button--warning, .van-button--primary');
                    if (!dEl) {
                        let docButtons = document.querySelectorAll('button, div[role="button"]');
                        for (let b of docButtons) {
                            let txt = (b.innerText || '').toLowerCase();
                            if ((txt.includes('total amount') || txt.includes('total') || txt.includes('confirm') || txt.includes('bet')) && b.offsetParent) {
                                dEl = b;
                                break;
                            }
                        }
                    }
                    if (dEl) drx_simClick(dEl);

                    setTimeout(() => {
                        let overlay = document.querySelector('.van-overlay');
                        if (overlay) try { overlay.click(); } catch(e){}
                        if (cb) cb(true);
                    }, 1000);
                }, 200);
            }, 150);
        } catch(e) {
            if (cb) cb(false);
        }
    };

    window.__WINGO_EXECUTE_TRADE = (forcedPred) => {
        if (!st.isRun || isTargetAchieved() || st.isTrd) return;
        executeCycleTradeWorkflow(forcedPred);
    };

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    st.dynSeq = calcSeq(initialBal > 0 ? initialBal : 100, st.steps);
    st.stpIdx = 0;

    let isFetchingApi = false;

    const executeCycleTradeWorkflow = async (overridePred = null) => {
        if (isTargetAchieved() || isFetchingApi || st.isTrd) return;

        let liveB = chkBal();
        if (liveB > 0 && st.startBal <= 0) {
            st.startBal = liveB;
            st.dynSeq = calcSeq(liveB, st.steps);
        }
        if (isTargetAchieved()) return;

        isFetchingApi = true;

        try {
            let fetchUrl = predictionApiUrl + (predictionApiUrl.includes('?') ? '&' : '?') + "t=" + Date.now();
            let rawJson = null;

            try {
                let res = await fetch(fetchUrl);
                if (res.ok) rawJson = await res.json();
            } catch(fetchErr) {}

            if (!rawJson) {
                try {
                    let localItem = localStorage.getItem('drx_latest_pred');
                    if (localItem) {
                        let pObj = JSON.parse(localItem);
                        if (Date.now() - pObj.time < 28000) {
                            rawJson = { next: { size: pObj.pred, confidence: pObj.confidence || 85, period: pObj.period } };
                        }
                    }
                } catch(e){}
            }

            let histArray = [];
            if (rawJson && Array.isArray(rawJson.history)) {
                histArray = rawJson.history;
            } else if (rawJson && rawJson.data && Array.isArray(rawJson.data.history)) {
                histArray = rawJson.data.history;
            }

            // =================================================================
            // REAL API WIN / LOSS EVALUATION (উইন-লস সরাসরি এপিআই হিস্ট্রি থেকে)
            // =================================================================
            if (st.lastBetPeriod && st.lastBetAmt > 0 && st.evaluatedPeriod !== st.lastBetPeriod) {
                st.evaluatedPeriod = st.lastBetPeriod;
                triggerBalanceRefresh();
                
                await new Promise(r => setTimeout(r, 800));
                let freshBal = chkBal();
                let won = false;
                let evaluatedMethod = "NONE";

                // Layer 1 (PRIMARY): Realtime EdgeOne API History Verification
                if (histArray && histArray.length > 0) {
                    let targetPeriodStr = String(st.lastBetPeriod).trim();
                    let finishedItem = histArray.find(h => {
                        let hp = String(h.period || h.pid || h.issue || '').trim();
                        return hp === targetPeriodStr || (targetPeriodStr.length >= 5 && hp.endsWith(targetPeriodStr.slice(-5)));
                    });

                    if (finishedItem) {
                        let itemStatus = String(finishedItem.status || '').toUpperCase().trim();
                        let actualSize = '';
                        if (finishedItem.actual_size) actualSize = String(finishedItem.actual_size).toUpperCase().trim();
                        else if (finishedItem.size) actualSize = String(finishedItem.size).toUpperCase().trim();
                        else if (typeof finishedItem.actual === 'number') actualSize = finishedItem.actual >= 5 ? 'BIG' : 'SMALL';

                        if (itemStatus === 'WIN' || itemStatus === 'LOSS') {
                            won = (itemStatus === 'WIN');
                            evaluatedMethod = "API_STATUS_" + itemStatus;
                        } else if (actualSize) {
                            won = (st.lastPred === actualSize);
                            evaluatedMethod = "API_ACTUAL_SIZE";
                        }
                    }
                }

                // Layer 2: DOM Game History Fallback
                if (evaluatedMethod === "NONE") {
                    try {
                        let recordRows = document.querySelectorAll('.GameList__C-body-item, .van-row, tr, [class*="record-item" i], [class*="history-item" i], .van-table__row');
                        for (let r of recordRows) {
                            let txt = (r.innerText || '').trim();
                            let pStr = String(st.lastBetPeriod);
                            let pShort = pStr.length > 5 ? pStr.slice(-5) : pStr;
                            if (txt.includes(pShort)) {
                                if (txt.includes('Big') || txt.includes('BIG') || txt.includes('大')) {
                                    won = (st.lastPred === 'BIG');
                                    evaluatedMethod = "DOM_RECORD";
                                    break;
                                } else if (txt.includes('Small') || txt.includes('SMALL') || txt.includes('小')) {
                                    won = (st.lastPred === 'SMALL');
                                    evaluatedMethod = "DOM_RECORD";
                                    break;
                                } else {
                                    let mNum = txt.match(/\b([0-9])\b/);
                                    if (mNum) {
                                        let n = parseInt(mNum[1]);
                                        won = (st.lastPred === (n >= 5 ? 'BIG' : 'SMALL'));
                                        evaluatedMethod = "DOM_RECORD";
                                        break;
                                    }
                                }
                            }
                        }
                    } catch(e){}
                }

                // Layer 3: Balance Differential Fallback
                if (evaluatedMethod === "NONE" && st.preBetBalance > 0 && freshBal > 0) {
                    let netDiff = freshBal - st.preBetBalance;
                    if (netDiff >= -(st.lastBetAmt * 0.15)) {
                        won = true;
                        evaluatedMethod = "BALANCE_GAIN";
                    } else {
                        won = false;
                        evaluatedMethod = "BALANCE_DROP";
                    }
                }

                // Update Continuous Martingale State
                if (won) {
                    st.w++;
                    st.cur_w_streak++;
                    st.cur_l_streak = 0;
                    if (st.cur_w_streak > st.max_w_streak) st.max_w_streak = st.cur_w_streak;
                    st.stpIdx = 0;
                    st.dynSeq = calcSeq(freshBal > 0 ? freshBal : st.curBal, st.steps);
                } else {
                    st.l++;
                    st.cur_l_streak++;
                    st.cur_w_streak = 0;
                    if (st.cur_l_streak > st.max_l_streak) st.max_l_streak = st.cur_l_streak;

                    // ২৪/৭ আনইন্টারাপ্টেড রিসাইকেল: ৫ স্টেপ পার হলে অটো স্টেপ ১-এ ফিরে যাবে
                    if (st.stpIdx >= st.steps - 1) {
                        st.stpIdx = 0;
                        st.dynSeq = calcSeq(freshBal > 0 ? freshBal : st.curBal, st.steps);
                    } else {
                        st.stpIdx = st.stpIdx + 1;
                    }
                }
            }

            if (isTargetAchieved()) {
                isFetchingApi = false;
                return;
            }

            let outcome = resolvePredictionFromApi(rawJson);
            let incomingPred = overridePred || outcome.pred || 'BIG';
            let incomingRate = outcome.rate || 80;

            let incomingPeriod = (outcome.period) ? String(outcome.period).trim() : getLiveRoundId();

            // STRICT ANTI-DOUBLE BETTING GUARD
            if (st.lastBetPeriod === incomingPeriod) {
                isFetchingApi = false;
                return;
            }

            let sEl = document.getElementById('hud-signal');
            let rEl = document.getElementById('hud-rate');
            if (sEl) sEl.innerText = "SIGNAL: " + incomingPred;
            if (rEl) rEl.innerText = "CONFIDENCE: " + incomingRate + "%";

            let betAmt = Math.floor(st.dynSeq[st.stpIdx]) || 1;

            st.isTrd = true;
            st.lastPred = incomingPred;
            st.lastBetPeriod = incomingPeriod;
            st.lastBetAmt = betAmt;
            st.preBetBalance = liveB;

            exeTrdFast(incomingPred, betAmt, (success) => {
                if (success) {
                    st.tradesDone++;
                }
                st.isTrd = false;
                isTargetAchieved();
            });

        } catch(err) {
            st.isTrd = false;
        }
        isFetchingApi = false;
    };

    const timerTick = () => {
        if (!st.isRun || isTargetAchieved()) return;
        const rem = updateTimer();
        const currentCycle = Math.floor(Date.now() / 30000);

        if (st.lastTriggeredCycle !== currentCycle && rem <= 20 && rem >= 8) {
            st.lastTriggeredCycle = currentCycle;
            executeCycleTradeWorkflow();
        }
    };

    updateTimer();
    st.timerInt = setInterval(timerTick, 1000);
    return "DRX_HTML_HUD_AND_TIMER_INTEGRATED";
})();
"""

# ==============================================================================
# PYTHON PARALLEL PREDICTION FETCH (নতুন এপিআই ফার্স্ট কল লজিক)
# ==============================================================================
def python_fetch_best_prediction():
    """নতুন API থেকে পাইথন দিয়ে সরাসরি 'next.size' এবং 'confidence' সিগন্যাল রিড করে।"""
    try:
        req = urllib.request.Request(
            f"{PREDICTION_API_URL}?t={int(time.time()*1000)}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as res:
            data = json.loads(res.read().decode("utf-8"))

        next_obj = data.get("next") or {}
        if next_obj:
            raw_pred = str(next_obj.get("size") or next_obj.get("pred") or "").upper().strip()
            if "SMALL" in raw_pred:
                return "SMALL"
            elif "BIG" in raw_pred:
                return "BIG"

        if "history" in data and len(data["history"]) > 0:
            last_pred = str(data["history"][0].get("pred", "")).upper()
            if "SMALL" in last_pred: return "SMALL"
            if "BIG" in last_pred: return "BIG"

        return "BIG"
    except Exception as e:
        logger.error(f"Error fetching prediction from API: {e}")
        return "BIG"

# ==============================================================================
# WORKER EXECUTION FLOWS
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 20,
        "text": "Initializing dedicated low-ram container...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    try:
        driver, handle = allocate_session_tab(sid, login_url)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    except Exception as e:
        logger.error(f"Failed to allocate session for {sid}: {e}")
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": str(e),
            "anim_msg_id": anim_msg_id
        })
        terminate_session_cleanly(sid)
        return

    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 40,
        "text": "Navigating to platform portal & bypassing guards...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    fill_ok = False
    for _ in range(60):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(1.2)
            break
        time.sleep(0.4)

    if not fill_ok:
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": "Login form not found or timed out.",
            "anim_msg_id": anim_msg_id
        })
        terminate_session_cleanly(sid)
        return

    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 60,
        "text": "Submitting encrypted authentication credentials...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    login_status = "PENDING"
    err_detail = ""
    for _ in range(35):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "CONFIRM_CLICKED":
                time.sleep(1.0)
                continue
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "Invalid credentials")
                break
        time.sleep(0.4)

    if safe_tab_execute(sid, lambda drv: drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")):
        login_status = "SUCCESS"

    if login_status == "ERROR":
        terminate_session_cleanly(sid)
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": err_detail,
            "anim_msg_id": anim_msg_id
        })
        return

    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 80,
        "text": "Dismissing announcements & securing session token...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    time.sleep(0.6)

    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 100,
        "text": "Authentication verified! Ready for trade setup.",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })
    time.sleep(0.4)

    emit_event_to_manager("LOGIN_SUCCESS", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "phone": phone,
        "worker_id": NODE_ID,
        "anim_msg_id": anim_msg_id
    })

def execute_worker_prepare_wingo(chat_id, sid, wingo_url, site_name):
    sess = active_sessions.get(sid)
    if not sess:
        return

    verified = False
    for _ in range(15):
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
        safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_PERSISTENT_NAV_JS, wingo_url))
        time.sleep(1.5)

        is_ready = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS))
        if is_ready:
            verified = True
            break
        time.sleep(0.6)

    if not verified:
        safe_tab_execute(sid, lambda drv: drv.get(wingo_url))
        time.sleep(2.0)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    current_bal = 0.0
    for _ in range(12):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.4)

    sess["current_balance"] = current_bal
    sess["cur_bal"] = current_bal
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    emit_event_to_manager("WINGO_READY", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "live_balance": current_bal
    })

def worker_monitor_trading_loop(chat_id, sid, site_name):
    last_py_cycle = None
    loop_tick_count = 0
    last_synced_state = {}

    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        loop_tick_count += 1
        enforce_low_ram_guard()

        def _check_logout(drv):
            return drv.execute_script("""
                const hash = window.location.hash || '';
                const href = window.location.href || '';
                if (hash.includes('login') || href.includes('/login')) {
                    return "LOGGED_OUT_URL";
                }
                const bodyText = document.body ? document.body.innerText : '';
                if (bodyText.includes('Token has expired') || 
                    bodyText.includes('please login again') || 
                    bodyText.includes('already logged in') ||
                    bodyText.includes('somewhere else') ||
                    bodyText.includes('Error: 147') ||
                    bodyText.includes('frozen')) {
                    return "LOGGED_OUT_MSG";
                }
                const token = localStorage.getItem('token') || localStorage.getItem('token_str') || sessionStorage.getItem('token');
                if (!token && !hash.includes('WinGo')) {
                    return "TOKEN_LOST";
                }
                return null;
            """)

        logout_reason = safe_tab_execute(sid, _check_logout)
        if logout_reason:
            logger.warning(f"Session {sid} logged out detected! Reason: {logout_reason}")
            emit_event_to_manager("ACCOUNT_LOGGED_OUT", {
                "session_id": sid,
                "chat_id": chat_id,
                "site_name": site_name,
                "reason": logout_reason,
                "message": "⚠️️ আপনার অ্যাকাউন্টটি অন্য ডিভাইসে লগইন করার কারণে এই সেশনটি লগআউট হয়ে গেছে। ওয়ার্কার স্লটটি মুক্ত করা হলো।"
            })
            terminate_session_cleanly(sid)
            break

        # =====================================================================
        # ব্যাকএন্ড পাইথন ডিরেক্ট এপিআই প্রেডিকশন হ্যান্ডলার
        # =====================================================================
        now_bst = bst_now()
        now_sec = now_bst.second
        rem_sec = 30 - (now_sec % 30)
        cur_cycle = int(time.time() // 30)

        # রাউন্ডের ১৬ থেকে ১৮ সেকেন্ডের ভেতর পাইথন সরাসরি নতুন এপিআই কল করে ব্রাউজারে ইনজেক্ট করবে
        if rem_sec in [16, 17, 18] and last_py_cycle != cur_cycle:
            last_py_cycle = cur_cycle
            best_pred = python_fetch_best_prediction()
            safe_tab_execute(sid, lambda drv: drv.execute_script(f"""
                if (window.__WINGO_EXECUTE_TRADE && window.__WINGO_ST && !window.__WINGO_ST.isTrd && window.__WINGO_ST.isRun) {{
                    window.__WINGO_EXECUTE_TRADE('{best_pred}');
                }}
            """))

        def _get_st(drv):
            return drv.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        isRun: window.__WINGO_ST.isRun,
                        circuitBreakerTriggered: window.__WINGO_ST.circuitBreakerTriggered || false,
                        curBal: window.__WINGO_ST.curBal || 0.0,
                        tgtAmt: window.__WINGO_ST.tgtAmt || 0.0,
                        startBal: window.__WINGO_ST.startBal || 0.0,
                        w: window.__WINGO_ST.w || 0,
                        l: window.__WINGO_ST.l || 0,
                        step: (window.__WINGO_ST.stpIdx || 0) + 1,
                        steps: window.__WINGO_ST.steps || 5,
                        tradesDone: window.__WINGO_ST.tradesDone || 0
                    };
                }
                return null;
            """)

        js_data = safe_tab_execute(sid, _get_st)

        if js_data:
            sess["cur_bal"] = float(js_data.get("curBal", sess.get("cur_bal", 0.0)))
            sess["current_balance"] = sess["cur_bal"]
            sess["wins"] = js_data.get("w", 0)
            sess["losses"] = js_data.get("l", 0)
            tgt_amt = float(js_data.get("tgtAmt", 0.0))
            start_b = float(js_data.get("startBal") or sess.get("start_bal", 0.0))
            is_run = js_data.get("isRun", False)
            circuit_breaker = js_data.get("circuitBreakerTriggered", False)
            step_idx = js_data.get("step", 1)
            tot_steps = js_data.get("steps", sess.get("total_steps", 5))

            current_signature = {
                "bal": sess["cur_bal"],
                "w": sess["wins"],
                "l": sess["losses"],
                "s": step_idx,
                "r": is_run
            }

            state_changed = (current_signature != last_synced_state)
            if state_changed or (loop_tick_count % 8 == 0):
                last_synced_state = current_signature
                task_payload = {
                    "chat_id": chat_id,
                    "session_id": sid,
                    "site_name": site_name,
                    "status": "RUNNING" if is_run else "PAUSED",
                    "start_balance": start_b,
                    "current_balance": sess["cur_bal"],
                    "target_amount": tgt_amt,
                    "step": step_idx,
                    "total_steps": tot_steps,
                    "wins": sess["wins"],
                    "losses": sess["losses"],
                    "currency": "BDT",
                    "updated_at": time.time(),
                    "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
                }
                firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

            if circuit_breaker:
                safe_tab_execute(sid, lambda drv: drv.execute_script("""
                    if (window.__WINGO_ST) {
                        window.__WINGO_ST.circuitBreakerTriggered = false;
                        window.__WINGO_ST.isRun = true;
                        window.__WINGO_ST.stpIdx = 0;
                    }
                """))

            if tgt_amt > 0 and sess["cur_bal"] >= tgt_amt and start_b > 0:
                logger.info(f"Target achieved! Goal: {tgt_amt} | Bal: {sess['cur_bal']}. Terminating gracefully...")
                sess["is_trading"] = False
                task_payload = {
                    "chat_id": chat_id,
                    "session_id": sid,
                    "site_name": site_name,
                    "status": "COMPLETED",
                    "start_balance": start_b,
                    "current_balance": sess["cur_bal"],
                    "target_amount": tgt_amt,
                    "step": step_idx,
                    "total_steps": tot_steps,
                    "wins": sess["wins"],
                    "losses": sess["losses"],
                    "currency": "BDT",
                    "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
                }
                firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

                emit_event_to_manager("TARGET_ACHIEVED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": start_b,
                    "final_balance": sess["cur_bal"],
                    "wins": sess["wins"],
                    "losses": sess["losses"]
                })
                terminate_session_cleanly(sid)
                break
            elif not is_run and not circuit_breaker:
                sess["is_trading"] = False
                break

        if loop_tick_count % 25 == 0:
            gc.collect()

        time.sleep(1.8)

# ==============================================================================
# WORKER TASK AND ACTION LISTENER LOOP
# ==============================================================================
def worker_task_listener():
    logger.info(f"Worker task polling active on node: {NODE_ID}...")
    while WORKER_ACTIVE:
        try:
            task = firebase_sync_http(f"terminals/{NODE_ID}/task", "GET")
            if task and isinstance(task, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/task", "DELETE")
                t_type = task.get("type")

                if t_type == "LOGIN_AND_PREPARE":
                    sid = task["session_id"]
                    chat_id = task["chat_id"]
                    site_name = task.get("site_name", "Amar Club")
                    login_url = task["login_url"]
                    wingo_url = task["wingo_url"]
                    phone = task["phone"]
                    password = task["password"]

                    active_sessions[sid] = {
                        "chat_id": chat_id,
                        "session_id": sid,
                        "site_name": site_name,
                        "login_url": login_url,
                        "wingo_url": wingo_url,
                        "phone": phone,
                        "password": password,
                        "is_trading": False,
                        "current_balance": 0.0,
                        "cur_bal": 0.0,
                        "created_at": time.time(),
                        "last_activity": time.time(),
                        "lock": threading.RLock()
                    }

                    anim_msg_id = task.get("anim_msg_id")
                    threading.Thread(
                        target=execute_worker_login,
                        args=(chat_id, sid, phone, password, login_url, site_name, anim_msg_id),
                        daemon=True
                    ).start()

            action_pkt = firebase_sync_http(f"terminals/{NODE_ID}/action", "GET")
            if action_pkt and isinstance(action_pkt, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/action", "DELETE")
                kind = action_pkt.get("kind")
                sid = action_pkt.get("session_id")
                chat_id = action_pkt.get("chat_id")

                if kind in ["EMERGENCY_STOP", "EMERGENCY_STOP_ALL"]:
                    logger.warning(f"Emergency stop received: {kind}. Terminating all sessions!")
                    for s_id in list(active_sessions.keys()):
                        terminate_session_cleanly(s_id)
                    cleanup_zombie_browsers()

                elif kind == "PREPARE_WINGO" and sid in active_sessions:
                    sess = active_sessions[sid]
                    threading.Thread(
                        target=execute_worker_prepare_wingo,
                        args=(chat_id, sid, sess["wingo_url"], sess["site_name"]),
                        daemon=True
                    ).start()

                elif kind == "START_TRADING" and sid in active_sessions:
                    sess = active_sessions[sid]
                    target_goal = float(action_pkt.get("target_goal", 0.0))
                    total_steps = int(action_pkt.get("total_steps", 5))
                    pred_url = action_pkt.get("prediction_api_url") or PREDICTION_API_URL
                    sess["is_trading"] = True
                    sess["target_goal"] = target_goal
                    sess["total_steps"] = total_steps
                    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_CORE_JS, target_goal, total_steps, pred_url))

                    cur_b = sess.get("current_balance", 0.0)
                    sess["start_bal"] = cur_b
                    threading.Thread(
                        target=worker_monitor_trading_loop,
                        args=(chat_id, sid, sess["site_name"]),
                        daemon=True
                    ).start()

                elif kind == "REQUEST_TELEMETRY" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _tel(drv):
                        return drv.execute_script("""
                            if (window.__WINGO_ST) {
                                return {
                                    curBal: window.__WINGO_ST.curBal || 0.0,
                                    tgtAmt: window.__WINGO_ST.tgtAmt || 0.0,
                                    w: window.__WINGO_ST.w || 0,
                                    l: window.__WINGO_ST.l || 0,
                                    step: (window.__WINGO_ST.stpIdx || 0) + 1
                                };
                            }
                            return null;
                        """)
                    tel_data = safe_tab_execute(sid, _tel)
                    if tel_data:
                        emit_event_to_manager("LIVE_TELEMETRY", {
                            "session_id": sid,
                            "chat_id": chat_id,
                            "site_name": sess.get("site_name", ""),
                            "current_balance": tel_data.get("curBal", 0.0),
                            "target_total": tel_data.get("tgtAmt", 0.0),
                            "wins": tel_data.get("w", 0),
                            "losses": tel_data.get("l", 0),
                            "step": tel_data.get("step", 1)
                        })

                elif kind == "REQUEST_BALANCE" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _b(drv):
                        b = drv.execute_script("return (window.__WINGO_ST && window.__WINGO_ST.curBal) ? window.__WINGO_ST.curBal : null;")
                        if b is None or float(b) == 0:
                            b = drv.execute_script(FETCH_BALANCE_JS)
                        return b
                    bal_val = safe_tab_execute(sid, _b)
                    if bal_val is not None and float(bal_val) > 0:
                        sess["current_balance"] = float(bal_val)
                        sess["cur_bal"] = float(bal_val)
                    emit_event_to_manager("BALANCE_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "call_id": action_pkt.get("call_id"),
                        "live_balance": sess.get("current_balance", 0.0)
                    })

                elif kind == "REQUEST_STATS" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _s(drv):
                        return drv.execute_script("""
                            if (window.__WINGO_ST) {
                                return {
                                    w: window.__WINGO_ST.w || 0,
                                    l: window.__WINGO_ST.l || 0,
                                    step: (window.__WINGO_ST.stpIdx || 0) + 1,
                                    steps: window.__WINGO_ST.steps || 5,
                                    curBal: window.__WINGO_ST.curBal || 0.0,
                                    tgtAmt: window.__WINGO_ST.tgtAmt || 0.0,
                                    tradesDone: window.__WINGO_ST.tradesDone || 0,
                                    cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                                    cur_l_streak: window.__WINGO_ST.cur_l_streak || 0,
                                    max_w_streak: window.__WINGO_ST.max_w_streak || 0,
                                    max_l_streak: window.__WINGO_ST.max_l_streak || 0
                                };
                            }
                            return null;
                        """)
                    s_data = safe_tab_execute(sid, _s)
                    if s_data:
                        emit_event_to_manager("STATS_RESPONSE", {
                            "session_id": sid,
                            "chat_id": chat_id,
                            "data": s_data
                        })

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    safe_tab_execute(sid, lambda drv: drv.execute_script("""
                        if(window.__WINGO_ST){ 
                            window.__WINGO_ST.isRun = false; 
                            if(window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt); 
                            if(window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt);
                        }
                    """))
                    active_sessions[sid]["is_trading"] = False

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick alert: {e}")
        time.sleep(0.8)

# ==============================================================================
# HEARTBEAT & MONITORING LOOP
# ==============================================================================
def latency_monitor_loop():
    global cached_latency
    while WORKER_ACTIVE:
        try:
            cached_latency = measure_network_latency(PLATFORMS["site_amarclub"]["login"])
        except Exception:
            pass
        time.sleep(30.0)

def worker_register_node():
    node_payload = {
        "status": "FREE",
        "heartbeat": time.time(),
        "assigned_user_id": None,
        "session_id": None,
        "task": None,
        "node_id": NODE_ID,
        "alias": WORKER_ALIAS,
        "load": len(active_sessions),
        "latency_ms": cached_latency,
        "registered_at": time.time(),
        "registered_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)
    logger.info(f"Node registered in cluster as: {NODE_ID} (Alias: {WORKER_ALIAS})")

def worker_heartbeat_loop():
    while WORKER_ACTIVE:
        try:
            status_val = "BUSY" if any(s.get("is_trading") for s in active_sessions.values()) else "FREE"
            hb_data = {
                "heartbeat": time.time(),
                "status": status_val,
                "load": len(active_sessions),
                "alias": WORKER_ALIAS,
                "latency_ms": cached_latency,
                "time_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            }
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", hb_data)
        except Exception:
            pass
        time.sleep(3.0)

def continuous_24h_watchdog():
    while WORKER_ACTIVE:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                if item.get("is_trading"):
                    continue
                last_act = item.get("last_activity", now)
                if now - last_act > 7200 and not item.get("is_trading"):
                    terminate_session_cleanly(sid)
        except Exception:
            pass
        time.sleep(300)

def handle_shutdown_signals(sig, frame):
    global WORKER_ACTIVE
    logger.info(f"Shutdown signal received on {WORKER_ALIAS}. Initiating clean cluster teardown...")
    WORKER_ACTIVE = False
    try:
        firebase_sync_http(f"terminals/{NODE_ID}", "DELETE")
    except Exception:
        pass
    for s in list(active_sessions.keys()):
        terminate_session_cleanly(s)
    cleanup_zombie_browsers()
    sys.exit(0)

# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown_signals)
    signal.signal(signal.SIGTERM, handle_shutdown_signals)

    print(f"[*] {to_vip_text('DRX WINGO CLUSTER WORKER ACTIVE')} [{WORKER_ALIAS} | {NODE_ID}]...")
    worker_register_node()
    threading.Thread(target=latency_monitor_loop, daemon=True).start()
    threading.Thread(target=worker_heartbeat_loop, daemon=True).start()
    threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

    try:
        worker_task_listener()
    except KeyboardInterrupt:
        handle_shutdown_signals(None, None)
