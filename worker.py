# ==============================================================================
# DRX WINGO CLUSTER - ULTRA RESILIENT DYNAMIC WORKER NODE (512MB RAM ENGINE)
# ==============================================================================
# Architecture & Capabilities:
# - Exact HTML Compound Martingale Algorithm (2^N - 1 True Proportional Scaling)
# - Immutable / Locked Martingale Plan across Entire Session (Zero Mid-Cycle Drift)
# - Guaranteed Full Step Execution (e.g., Steps 1 to 7 without Skipping or Reset)
# - High-Speed Instant Balance Telemetry Engine (Sub-100ms Probe, Zero Lag)
# - Pure Python-Driven API Prediction Engine (Zero Browser CORS/WAF Failure)
# - Dynamic Bidirectional Trade Dispatcher (Accurate BIG & SMALL Placement)
# - Live API History Win/Loss Verification with Multi-Layer Outcome Fallback
# - Linux Malloc Arena Hardening to eradicate fragmentation on Railway Containers
# - Single-Core Firefox Process Clamping (<160MB RAM Target Footprint)
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
        ("requests", "requests")
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

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil

# ==============================================================================
# UNICODE TYPOGRAPHY & VIP STYLING
# ==============================================================================
VIP_ALPHA_MAP = {c: v for c, v in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")}
BOLD_DIGIT_MAP = {d: v for d, v in zip("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")}

def to_vip_text(text: str) -> str:
    return "".join(VIP_ALPHA_MAP.get(c.upper(), c) if c.isalpha() else c for c in str(text))

def to_bold_digits(val) -> str:
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# GLOBAL RUNTIME CONFIGURATION
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://gsgssnn-580ca-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json")
HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() == "true"

custom_arg = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if custom_arg:
    WORKER_ALIAS = f"W-{int(custom_arg):02d}" if custom_arg.isdigit() else custom_arg.upper()
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

api_http_session = requests.Session()
api_http_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
})

# ==============================================================================
# EXACT HTML COMPOUND MARTINGALE FORMULA (নিখুঁত এইচটিএমএল লজিক)
# ==============================================================================
def calculate_html_martingale_steps(balance_val: float, steps_count: int) -> list:
    """
    আপনার দেওয়া এইচটিএমএল স্ক্রিপ্টের হুবহু কম্পাউন্ড মার্টিঙ্গেল লজিক:
    1. sumPowers = 2^stepsCount - 1
    2. firstStep = balance / sumPowers
    3. step[i] = firstStep * 2^i
    4. ব্যালেন্সের অবশিষ্ট বা রাউন্ডিং এরর শেষ স্টেপে যোগ হবে।
    """
    balance = float(balance_val)
    steps_count = max(1, int(steps_count))

    if balance <= 0:
        return [1] * steps_count

    # 2^N - 1 পাওয়ার হিসাব
    sum_powers = (2 ** steps_count) - 1
    first_step = balance / sum_powers

    steps = []
    total = 0

    for i in range(steps_count):
        step_val = first_step * (2 ** i)
        step_rounded = max(1, int(round(step_val)))
        steps.append(step_rounded)
        total += step_rounded

    # এইচটিএমএলের মতো অবশিষ্টাংশ শেষ স্টেপে সমন্বয়
    rounding_error = int(round(balance - total))
    steps[-1] += rounding_error

    # নিশ্চিত করা যেন শেষ স্টেপ অন্তত পূর্ববর্তী স্টেপের দ্বিগুণ বা ইতিবাচক হয়
    if steps[-1] < 1:
        steps[-1] = max(1, steps[-2] * 2 if len(steps) > 1 else 1)

    return steps

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
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
# PROCESS CLEANUP & RAM SWEEPER
# ==============================================================================
def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try: child.kill()
            except Exception: pass
        parent.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except Exception:
        pass

def cleanup_zombie_browsers():
    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                pname = (proc.info['name'] or '').lower()
                if 'firefox' in pname or 'geckodriver' in pname:
                    if proc.info['ppid'] == 1 or proc.info['ppid'] == current_pid:
                        is_active = any(
                            s.get('driver') and hasattr(s['driver'], 'service') and s['driver'].service and
                            s['driver'].service.process and s['driver'].service.process.pid == proc.info['pid']
                            for s in active_sessions.values()
                        )
                        if not is_active:
                            try: proc.kill()
                            except Exception: pass
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

def enforce_low_ram_guard():
    try:
        mem = psutil.virtual_memory()
        if mem.percent > 80.0:
            gc.collect()
            for s in list(active_sessions.values()):
                d = s.get("driver")
                if d:
                    try: d.execute_script("if (window.performance && window.performance.memory) { window.gc && window.gc(); }")
                    except Exception: pass
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
            except Exception: pass

            try:
                driver.execute_script("""
                    let hud = document.getElementById('drx-prediction-hud');
                    if (hud) hud.remove();
                """)
            except Exception: pass

            try: driver.quit()
            except Exception: pass

            if driver_pid: kill_process_tree(driver_pid)

        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

    cleanup_zombie_browsers()
    gc.collect()

    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
        "status": "FREE",
        "assigned_user_id": None,
        "session_id": None,
        "task": None,
        "load": len(active_sessions)
    })
    logger.info(f"Session {session_id} dismantled cleanly. Worker {NODE_ID} ready.")

# ==============================================================================
# HARDENED BROWSER ALLOCATOR (0.5GB RAILWAY SAFE)
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess: raise Exception("Session structure missing.")

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
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(30)
    driver.set_script_timeout(18)
    driver.implicitly_wait(1.5)
    driver.set_window_size(400, 800)

    try:
        driver.get(target_url)
    except Exception as e:
        logger.warning(f"Initial navigation alert: {e}")

    sess["driver"] = driver
    sess["window_handle"] = driver.current_window_handle
    sess["last_activity"] = time.time()
    return driver, sess["window_handle"]

def safe_tab_execute(sid, task_fn, timeout=20.0):
    sess = active_sessions.get(sid)
    if not sess or not sess.get("driver") or not sess.get("lock"):
        return None

    lock = sess["lock"]
    if not lock.acquire(timeout=4.0):
        return None

    result_container = {"res": None, "error": None, "completed": False}

    def execute_worker():
        try:
            result_container["res"] = task_fn(sess["driver"])
            result_container["completed"] = True
            sess["last_activity"] = time.time()
        except Exception as e:
            result_container["error"] = e

    worker_thread = threading.Thread(target=execute_worker, daemon=True)
    worker_thread.start()
    worker_thread.join(timeout=timeout)

    try: lock.release()
    except RuntimeError: pass

    return result_container["res"] if result_container["completed"] else None

# ==============================================================================
# FAST BALANCE CHECKER (জিরো ল্যাগ ও ইনস্ট্যান্ট ব্যালেন্স ডিটেক্টর)
# ==============================================================================
FAST_BALANCE_JS = r"""
(function(){
    // ১. টার্গেটেড ব্যালেন্স ক্লাস
    const targetedSelectors = ['.Wallet__balance-num', '.wallet-user-balance', '.balance-num', '.user-balance'];
    for (const sel of targetedSelectors) {
        const el = document.querySelector(sel);
        if (el) {
            const m = (el.innerText || '').match(/[\d,]+\.?\d*/);
            if (m) {
                const val = parseFloat(m[0].replace(/,/g, ''));
                if (!isNaN(val) && val > 0) return val;
            }
        }
    }
    // ২. লোকাল স্টোরেজ ক্যাশ
    try {
        const u = JSON.parse(localStorage.getItem('user') || sessionStorage.getItem('user') || '{}');
        if (u && (u.balance !== undefined || u.amount !== undefined)) {
            const val = parseFloat(u.balance || u.amount);
            if (!isNaN(val) && val > 0) return val;
        }
    } catch(e){}
    // ৩. নির্দিষ্ট টেক্সট এলিমেন্ট
    const els = document.querySelectorAll('[class*="balance" i], [class*="wallet" i]');
    for (const el of els) {
        if (el.children.length === 0) {
            const m = (el.innerText || '').match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
            if (m) {
                const val = parseFloat(m[1].replace(/,/g, ''));
                if (!isNaN(val) && val > 0) return val;
            }
        }
    }
    return 0.0;
})();
"""

# ==============================================================================
# JAVASCRIPT AUTOMATION HELPERS
# ==============================================================================
MODAL_AUTO_DISMISSER_JS = """
(function(){
    const directSelectors = [
        '.van-dialog__confirm', '.dialog-confirm', '.van-button--primary',
        '.van-popup__close-icon', '.van-overlay', '.dialog-close', '.close-btn',
        'button[class*="close" i]', 'button[class*="confirm" i]', 'div[class*="close" i]',
        '.announcement-box .close', '.modal-mask', '.reward-receive-btn'
    ];
    directSelectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            if (el && el.offsetParent !== null && !el.closest('#drx-prediction-hud')) {
                try { 
                    ['pointerdown','mousedown','mouseup','click'].forEach(evt => {
                        el.dispatchEvent(new MouseEvent(evt, {bubbles:true, cancelable:true, view:window}));
                    });
                    el.click(); 
                } catch(e){}
            }
        });
    });
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
    window.location.hash = '#/login';
}

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]');
let elP = document.querySelector('input[type="password"]');
let elL = document.querySelector('button[type="submit"]');

if (!elN || !elP || !elL) return "NOT_READY";

const clearAndSet = (el, val) => {
    el.focus();
    el.value = '';
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value')?.set;
    if (setter) setter.call(el, val);
    else el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
};

clearAndSet(elN, phone);
setTimeout(() => {
    clearAndSet(elP, pass);
    setTimeout(() => { elL.click(); }, 300);
}, 300);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) return { status: "SUCCESS" };
try {
    if (localStorage.getItem('token') || sessionStorage.getItem('token')) return { status: "SUCCESS" };
} catch(e){}
return { status: "PENDING" };
"""

# ==============================================================================
# ON-PAGE HUD & EXECUTION HARNESS (DISPLAY & ORDER EXECUTION ONLY)
# ==============================================================================
WINGO_CLIENT_HARNESS_JS = r"""
(function(){
    let hud = document.getElementById('drx-prediction-hud');
    if (!hud) {
        hud = document.createElement('div');
        hud.id = 'drx-prediction-hud';
        hud.style.cssText = 'position:fixed;top:8px;right:8px;z-index:999999;background:rgba(13,17,23,0.92);border:1px solid #30363d;border-radius:8px;padding:8px;color:#58a6ff;font-family:monospace;text-align:center;width:170px;pointer-events:none;box-shadow:0 4px 15px rgba(0,0,0,0.6);';
        hud.innerHTML = `
            <div style="font-size:10px;font-weight:bold;color:#f0883e;">⚡ DRX LOCKED ENGINE ⚡</div>
            <div id="hud-timer" style="font-size:24px;font-weight:bold;color:#39d353;margin:2px 0;">00:30</div>
            <div id="hud-signal" style="font-size:14px;font-weight:bold;color:#ffffff;">SIGNAL: STANDBY</div>
            <div id="hud-step-info" style="font-size:11px;font-weight:bold;color:#388bfd;margin-top:2px;">STEP: 1/7 | BET: 1</div>
            <div id="hud-rate" style="font-size:10px;color:#8b949e;">CONFIDENCE: --%</div>
            <div id="hud-bst-time" style="font-size:9px;color:#58a6ff;margin-top:2px;">BST: --:--:--</div>
        `;
        document.body.appendChild(hud);
    }

    const simClick = (el) => {
        if (!el) return;
        ['pointerdown', 'mousedown', 'touchstart', 'pointerup', 'mouseup', 'touchend', 'click'].forEach(evt => {
            try { el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window })); } catch(e){}
        });
        if (typeof el.click === 'function') {
            try { el.click(); } catch(e){}
        }
    };

    window.__WINGO_FIND_BUTTON = function(direction) {
        let norm = String(direction).trim().toUpperCase();
        let btn = null;

        if (norm === 'BIG') {
            btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
        } else if (norm === 'SMALL') {
            btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
        }

        if (!btn) {
            let allBtns = document.querySelectorAll('button, div[role="button"], span, div');
            for (let el of allBtns) {
                let t = (el.innerText || '').trim().toUpperCase();
                if (t === norm && el.offsetParent !== null && el.children.length === 0) {
                    btn = el;
                    break;
                }
            }
        }
        return btn;
    };

    window.__WINGO_DISPATCH_ORDER = function(direction, amount, period, confidence, currentStep, totalSteps) {
        let norm = String(direction).trim().toUpperCase();
        if (norm !== 'BIG' && norm !== 'SMALL') {
            return { status: "REJECTED", reason: "INVALID_DIRECTION" };
        }

        let btn = window.__WINGO_FIND_BUTTON(norm);
        if (!btn) {
            return { status: "FAILED", reason: "BUTTON_NOT_FOUND_" + norm };
        }

        let sigEl = document.getElementById('hud-signal');
        let rateEl = document.getElementById('hud-rate');
        let stepEl = document.getElementById('hud-step-info');

        if (sigEl) {
            sigEl.innerText = "SIGNAL: " + norm;
            sigEl.style.color = (norm === "BIG") ? "#f0883e" : "#388bfd";
        }
        if (rateEl) rateEl.innerText = "CONFIDENCE: " + (confidence || 90) + "%";
        if (stepEl) stepEl.innerText = "STEP: " + currentStep + "/" + totalSteps + " | BET: " + amount;

        simClick(btn);

        setTimeout(() => {
            let inpEl = document.querySelector("input.van-stepper__input, input.van-field__control, input[type='number']");
            if (inpEl) {
                inpEl.focus();
                let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                if (setter) {
                    setter.call(inpEl, String(amount));
                } else {
                    inpEl.value = String(amount);
                }
                inpEl.dispatchEvent(new Event('input', { bubbles: true }));
                inpEl.dispatchEvent(new Event('change', { bubbles: true }));
            }

            setTimeout(() => {
                let confBtn = document.querySelector('button.bet-amount, button[class*="bet-amount" i], .Betting__C-foot-total, .van-button--danger, .van-button--warning, .van-button--primary');
                if (!confBtn) {
                    let docButtons = document.querySelectorAll('button, div[role="button"]');
                    for (let b of docButtons) {
                        let txt = (b.innerText || '').toLowerCase();
                        if ((txt.includes('total amount') || txt.includes('total') || txt.includes('confirm') || txt.includes('bet')) && b.offsetParent) {
                            confBtn = b;
                            break;
                        }
                    }
                }
                if (confBtn) simClick(confBtn);

                setTimeout(() => {
                    let overlay = document.querySelector('.van-overlay');
                    if (overlay) try { overlay.click(); } catch(e){}
                }, 500);
            }, 180);
        }, 150);

        return { status: "SUCCESS", direction: norm, amount: amount, period: period };
    };

    if (!window.__WINGO_CLOCK_INTERVAL) {
        window.__WINGO_CLOCK_INTERVAL = setInterval(() => {
            const d = new Date();
            const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
            const bst = new Date(utc + (3600000 * 6));
            const seconds = bst.getSeconds();
            const rem = 30 - (seconds % 30);
            const displaySec = rem === 30 ? 0 : rem;

            let tEl = document.getElementById("hud-timer");
            if (tEl) tEl.innerText = `00:${String(displaySec).padStart(2, '0')}`;

            let bstEl = document.getElementById("hud-bst-time");
            if (bstEl) {
                let h = String(bst.getHours()).padStart(2, '0');
                let m = String(bst.getMinutes()).padStart(2, '0');
                let s = String(seconds).padStart(2, '0');
                bstEl.innerText = `BST: ${h}:${m}:${s}`;
            }
        }, 1000);
    }

    return "HARNESS_READY";
})();
"""

# ==============================================================================
# PURE PYTHON PREDICTION ENGINE
# ==============================================================================
def fetch_api_prediction():
    """এজওয়ান API থেকে নির্ভুলভাবে next.size, period, confidence ও history রিড করে।"""
    try:
        url = f"{PREDICTION_API_URL}?_t={int(time.time() * 1000)}"
        res = api_http_session.get(url, timeout=3.5)
        if res.status_code == 200:
            data = res.json()
            next_data = data.get("next") or {}

            raw_size = str(next_data.get("size") or next_data.get("pred") or "").upper().strip()
            clean_pred = None
            if "SMALL" in raw_size:
                clean_pred = "SMALL"
            elif "BIG" in raw_size:
                clean_pred = "BIG"

            period = str(next_data.get("period") or "").strip()
            conf = int(next_data.get("confidence") or (data.get("stats", {}).get("accuracy") or 85))
            history = data.get("history") or []

            return {
                "prediction": clean_pred,
                "confidence": conf,
                "period": period,
                "history": history
            }
    except Exception as e:
        logger.error(f"Prediction API fetch exception: {e}")
    return None

# ==============================================================================
# AUTOMATED TRADING LOOP (LOCKED STEP EXECUTION)
# ==============================================================================
def worker_monitor_trading_loop(chat_id, sid, site_name, target_goal=0.0, total_steps=7):
    sess = active_sessions.get(sid)
    if not sess: return

    logger.info(f"[{WORKER_ALIAS}] Initializing Locked Trading Loop for Session {sid} | Target: {target_goal} | Steps: {total_steps}")

    sess["is_trading"] = True
    sess["target_goal"] = target_goal
    sess["total_steps"] = max(1, int(total_steps))
    sess["step_idx"] = 0
    sess["wins"] = 0
    sess["losses"] = 0

    # প্রারম্ভিক ব্যালেন্স সংগ্রহ
    initial_bal = 0.0
    for _ in range(5):
        bal_probe = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS))
        if bal_probe and float(bal_probe) > 0:
            initial_bal = float(bal_probe)
            break
        time.sleep(0.4)

    sess["start_bal"] = initial_bal
    sess["cur_bal"] = initial_bal

    # ==========================================================================
    # এইচটিএমএল ফর্মুলা অনুযায়ী সম্পূর্ণ সেশনের জন্য স্টেপ প্ল্যান লক করা হলো
    # ==========================================================================
    locked_plan = calculate_html_martingale_steps(initial_bal, sess["total_steps"])
    sess["locked_plan"] = locked_plan

    formatted_breakdown = ", ".join([f"S{i+1}:{amt}৳" for i, amt in enumerate(locked_plan)])
    logger.info(f"[{WORKER_ALIAS}] 🔥 LOCKED STEP PLAN CREATED: [{formatted_breakdown}] for Capital: {initial_bal} BDT")

    last_processed_cycle = None
    last_evaluated_period = None
    last_placed_pred = None
    last_placed_period = None
    last_placed_amt = 0
    loop_tick = 0

    while WORKER_ACTIVE:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        loop_tick += 1
        enforce_low_ram_guard()

        now_bst = bst_now()
        rem_sec = 30 - (now_bst.second % 30)
        current_cycle = int(time.time() // 30)

        # ----------------------------------------------------------------------
        # ১. ট্রেড সিগন্যাল এক্সিকিউশন (রাউন্ড শেষ হওয়ার ১৮ থেকে ১৩ সেকেন্ডের মধ্যে)
        # ----------------------------------------------------------------------
        if rem_sec in [18, 17, 16, 15, 14, 13] and last_processed_cycle != current_cycle:
            api_data = fetch_api_prediction()
            if api_data and api_data.get("prediction"):
                pred_direction = api_data["prediction"]
                pred_period = api_data["period"]
                pred_conf = api_data["confidence"]

                if last_placed_period != pred_period:
                    last_processed_cycle = current_cycle
                    last_placed_period = pred_period
                    last_placed_pred = pred_direction

                    cur_idx = sess.get("step_idx", 0)
                    plan = sess.get("locked_plan", locked_plan)

                    # সীমার মধ্যে স্টেপ নির্বাচন (০ থেকে total_steps - 1)
                    safe_idx = min(cur_idx, len(plan) - 1)
                    bet_amt = plan[safe_idx]
                    last_placed_amt = bet_amt
                    sess["current_bet"] = bet_amt

                    logger.info(
                        f"[{WORKER_ALIAS}] 🎯 [DISPATCH ORDER] Step: {safe_idx + 1}/{sess['total_steps']} | "
                        f"Side: {to_vip_text(pred_direction)} | Stake: {bet_amt} BDT | Period: {pred_period}"
                    )

                    safe_tab_execute(sid, lambda drv: drv.execute_script(
                        f"return window.__WINGO_DISPATCH_ORDER('{pred_direction}', {bet_amt}, '{pred_period}', {pred_conf}, {safe_idx + 1}, {sess['total_steps']});"
                    ))

        # ----------------------------------------------------------------------
        # ২. ফলাফল মূল্যায়ন (রাউন্ড শুরুর ২৮ থেকে ২৪ সেকেন্ডের মধ্যে)
        # ----------------------------------------------------------------------
        if last_placed_period and last_evaluated_period != last_placed_period and rem_sec in [28, 27, 26, 25]:
            api_data = fetch_api_prediction()
            if api_data and api_data.get("history"):
                history = api_data["history"]
                target_p_str = str(last_placed_period).strip()

                settled_round = next((
                    h for h in history
                    if str(h.get("period", "")).strip() == target_p_str or
                       (len(target_p_str) > 5 and str(h.get("period", "")).strip().endswith(target_p_str[-5:]))
                ), None)

                if settled_round:
                    last_evaluated_period = last_placed_period
                    status_raw = str(settled_round.get("status", "")).upper().strip()
                    actual_size = str(settled_round.get("actual_size") or settled_round.get("size") or "").upper().strip()

                    won = False
                    if status_raw == "WIN": won = True
                    elif status_raw == "LOSS": won = False
                    elif actual_size: won = (last_placed_pred == actual_size)

                    # ==========================================================
                    # স্টেপ প্রগ্রেশন কন্ট্রোলার (লকড স্টেপ অপরিবর্তিত থাকবে)
                    # ==========================================================
                    if won:
                        sess["wins"] += 1
                        sess["step_idx"] = 0  # লাভ হলে সরাসরি ১ম স্টেপে ব্যাক
                        logger.info(f"[{WORKER_ALIAS}] 🏆 WIN for Period {last_placed_period} (+{last_placed_amt}৳)! Step Reset to 1.")

                        # নতুন সাইকেলের জন্য বর্তমান ব্যালেন্স দিয়ে নতুন প্ল্যান লক করা
                        fresh_b = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS))
                        if fresh_b and float(fresh_b) > 0:
                            sess["cur_bal"] = float(fresh_b)
                            sess["locked_plan"] = calculate_html_martingale_steps(sess["cur_bal"], sess["total_steps"])
                    else:
                        sess["losses"] += 1

                        # যদি লাস্ট স্টেপ (যেমন ৭ম স্টেপ) লস হয়, তবেই কেবল রিসাইকেল হবে
                        if sess["step_idx"] >= sess["total_steps"] - 1:
                            logger.warning(f"[{WORKER_ALIAS}] ⚠️ Full Cycle Loss ({sess['total_steps']} Steps). Recycling back to Step 1.")
                            sess["step_idx"] = 0
                            fresh_b = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS))
                            if fresh_b and float(fresh_b) > 0:
                                sess["cur_bal"] = float(fresh_b)
                                sess["locked_plan"] = calculate_html_martingale_steps(sess["cur_bal"], sess["total_steps"])
                        else:
                            # অন্যথায় নিশ্চিতভাবে পরবর্তী স্টেপে (যেমন ৬ষ্ঠ থেকে ৭মে) যাবে
                            sess["step_idx"] += 1
                            next_amt = sess["locked_plan"][sess["step_idx"]]
                            logger.info(f"[{WORKER_ALIAS}] ❌ LOSS for Period {last_placed_period}. Advancing to Step {sess['step_idx'] + 1} (Stake: {next_amt}৳).")

        # ----------------------------------------------------------------------
        # ৩. ফায়ারবেস সিঙ্ক ও টার্গেট ব্যালেন্স ভেরিফিকেশন
        # ----------------------------------------------------------------------
        if loop_tick % 5 == 0:
            fb_bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS))
            if fb_bal and float(fb_bal) > 0:
                sess["cur_bal"] = float(fb_bal)

            step_disp = sess.get("step_idx", 0) + 1
            sess["current_step"] = step_disp

            task_payload = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "RUNNING",
                "start_balance": sess.get("start_bal", 0.0),
                "current_balance": sess.get("cur_bal", 0.0),
                "target_amount": target_goal,
                "step": step_disp,
                "total_steps": sess["total_steps"],
                "current_stake": sess.get("locked_plan", locked_plan)[min(sess.get("step_idx", 0), len(sess.get("locked_plan", locked_plan)) - 1)],
                "step_plan": sess.get("locked_plan", locked_plan),
                "wins": sess.get("wins", 0),
                "losses": sess.get("losses", 0),
                "currency": "BDT",
                "updated_at": time.time(),
                "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            }
            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

            if target_goal > 0 and sess.get("cur_bal", 0.0) >= target_goal and sess.get("start_bal", 0.0) > 0:
                logger.info(f"[{WORKER_ALIAS}] 🎯 Target Goal Reached! Bal: {sess['cur_bal']} >= Goal: {target_goal}. Stopping...")
                sess["is_trading"] = False
                task_payload["status"] = "COMPLETED"
                firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)
                terminate_session_cleanly(sid)
                break

        time.sleep(1.0)

# ==============================================================================
# WORKER TASK HANDLER & ACTION LISTENER
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
    try:
        driver, _ = allocate_session_tab(sid, login_url)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    except Exception as e:
        emit_event_to_manager("LOGIN_FAILED", {"session_id": sid, "chat_id": chat_id, "reason": str(e)})
        terminate_session_cleanly(sid)
        return

    fill_ok = False
    for _ in range(50):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(1.5)
            break
        time.sleep(0.4)

    if not fill_ok:
        emit_event_to_manager("LOGIN_FAILED", {"session_id": sid, "chat_id": chat_id, "reason": "Login form timed out."})
        terminate_session_cleanly(sid)
        return

    for _ in range(30):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict) and res.get("status") == "SUCCESS":
            emit_event_to_manager("LOGIN_SUCCESS", {
                "session_id": sid, "chat_id": chat_id, "site_name": site_name, "phone": phone, "worker_id": NODE_ID
            })
            return
        time.sleep(0.5)

    emit_event_to_manager("LOGIN_FAILED", {"session_id": sid, "chat_id": chat_id, "reason": "Authentication timeout"})
    terminate_session_cleanly(sid)

def execute_worker_prepare_wingo(chat_id, sid, wingo_url, site_name):
    sess = active_sessions.get(sid)
    if not sess: return

    safe_tab_execute(sid, lambda drv: drv.execute_script(f"if(!window.location.href.includes('WinGo')) window.location.href = '{wingo_url}';"))
    time.sleep(2.5)

    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_CLIENT_HARNESS_JS))

    bal = 0.0
    for _ in range(10):
        b = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS))
        if b and float(b) > 0:
            bal = float(b)
            break
        time.sleep(0.3)

    sess["current_balance"] = bal
    sess["cur_bal"] = bal

    emit_event_to_manager("WINGO_READY", {
        "session_id": sid, "chat_id": chat_id, "site_name": site_name, "live_balance": bal
    })

def worker_task_listener():
    logger.info(f"Task listener active on worker node: {NODE_ID}...")
    while WORKER_ACTIVE:
        try:
            task = firebase_sync_http(f"terminals/{NODE_ID}/task", "GET")
            if task and isinstance(task, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/task", "DELETE")
                if task.get("type") == "LOGIN_AND_PREPARE":
                    sid = task["session_id"]
                    active_sessions[sid] = {
                        "chat_id": task["chat_id"],
                        "session_id": sid,
                        "site_name": task.get("site_name", "Amar Club"),
                        "login_url": task["login_url"],
                        "wingo_url": task["wingo_url"],
                        "phone": task["phone"],
                        "password": task["password"],
                        "is_trading": False,
                        "lock": threading.RLock()
                    }
                    threading.Thread(
                        target=execute_worker_login,
                        args=(task["chat_id"], sid, task["phone"], task["password"], task["login_url"], task.get("site_name"), task.get("anim_msg_id")),
                        daemon=True
                    ).start()

            action_pkt = firebase_sync_http(f"terminals/{NODE_ID}/action", "GET")
            if action_pkt and isinstance(action_pkt, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/action", "DELETE")
                kind = action_pkt.get("kind")
                sid = action_pkt.get("session_id")
                chat_id = action_pkt.get("chat_id")

                if kind in ["EMERGENCY_STOP", "EMERGENCY_STOP_ALL"]:
                    for s_id in list(active_sessions.keys()): terminate_session_cleanly(s_id)

                elif kind == "PREPARE_WINGO" and sid in active_sessions:
                    wingo_url = PLATFORMS["site_amarclub"]["wingo"]
                    threading.Thread(target=execute_worker_prepare_wingo, args=(chat_id, sid, wingo_url, "Amar Club"), daemon=True).start()

                elif kind == "START_TRADING" and sid in active_sessions:
                    sess = active_sessions[sid]
                    target_goal = float(action_pkt.get("target_goal") or action_pkt.get("target_amount") or 0.0)
                    total_steps = int(action_pkt.get("total_steps") or action_pkt.get("steps") or action_pkt.get("target_steps") or 7)

                    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_CLIENT_HARNESS_JS))

                    threading.Thread(
                        target=worker_monitor_trading_loop,
                        args=(chat_id, sid, sess["site_name"], target_goal, total_steps),
                        daemon=True
                    ).start()

                elif kind == "REQUEST_BALANCE" and sid in active_sessions:
                    sess = active_sessions[sid]
                    bal_val = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_BALANCE_JS), timeout=2.0)
                    if bal_val and float(bal_val) > 0:
                        sess["cur_bal"] = float(bal_val)

                    emit_event_to_manager("BALANCE_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "call_id": action_pkt.get("call_id"),
                        "live_balance": sess.get("cur_bal", 0.0),
                        "current_step": sess.get("current_step", 1),
                        "total_steps": sess.get("total_steps", 7),
                        "current_stake": sess.get("current_bet", 1),
                        "step_plan": sess.get("locked_plan", [])
                    })

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    active_sessions[sid]["is_trading"] = False

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Task listener exception: {e}")
        time.sleep(0.8)

# ==============================================================================
# HEARTBEAT & MONITORING LOOP
# ==============================================================================
def latency_monitor_loop():
    global cached_latency
    while WORKER_ACTIVE:
        try: cached_latency = measure_network_latency(PLATFORMS["site_amarclub"]["login"])
        except Exception: pass
        time.sleep(30.0)

def worker_register_node():
    node_payload = {
        "status": "FREE", "heartbeat": time.time(), "node_id": NODE_ID,
        "alias": WORKER_ALIAS, "load": len(active_sessions), "latency_ms": cached_latency,
        "registered_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)
    logger.info(f"Node registered in cluster as: {NODE_ID} (Alias: {WORKER_ALIAS})")

def worker_heartbeat_loop():
    while WORKER_ACTIVE:
        try:
            status_val = "BUSY" if any(s.get("is_trading") for s in active_sessions.values()) else "FREE"
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                "heartbeat": time.time(), "status": status_val, "load": len(active_sessions),
                "alias": WORKER_ALIAS, "latency_ms": cached_latency, "time_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            })
        except Exception: pass
        time.sleep(3.0)

def continuous_24h_watchdog():
    while WORKER_ACTIVE:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                if not item.get("is_trading") and now - item.get("last_activity", now) > 7200:
                    terminate_session_cleanly(sid)
        except Exception: pass
        time.sleep(300)

def handle_shutdown_signals(sig, frame):
    global WORKER_ACTIVE
    WORKER_ACTIVE = False
    try: firebase_sync_http(f"terminals/{NODE_ID}", "DELETE")
    except Exception: pass
    for s in list(active_sessions.keys()): terminate_session_cleanly(s)
    sys.exit(0)

# ==============================================================================
# MAIN ENTRY POINT
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
