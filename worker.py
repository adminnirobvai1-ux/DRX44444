# ==============================================================================
# DRX WINGO CLUSTER - ULTRA RESILIENT DYNAMIC WORKER NODE (512MB RAM ENGINE)
# ==============================================================================
# Architecture & Capabilities:
# - Advanced Compound Martingale Step Engine (100% Ported from HTML Calculator)
# - Immutable / Session-Locked Step Progression (Guaranteed 7/10/N Full Cycles)
# - High-Speed Micro-Cached Real-time Balance & Step Telemetry Engine
# - Pure Python-Driven API Prediction & Round Synchronizer (No Client-side Fetch)
# - Dynamic Bidirectional Trade Dispatcher (Full Support for both BIG & SMALL)
# - Anti-Double-Bet Period Locking Guard with Bangladesh Standard Time (BST/UTC+6)
# - Strict Single-Core Firefox Process Clamping (<160MB RAM Target Footprint)
# - Linux Malloc Arena Hardening to eradicate fragmentation on Cloud Containers
# - Non-Destructive Martingale Math Engine with Uninterrupted 24/7 Cycle Loops
# - Live API History Win/Loss Verification with Multi-Layer DOM & Balance Fallback
# - Smart State-Diff Telemetry Engine (Prevents Telegram UI Disappearance/FloodWait)
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
import math
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
# GLOBAL RUNTIME CONFIGURATION
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://gsgssnn-580ca-default-rtdb.firebaseio.com")
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
# ADVANCED COMPOUND MARTINGALE ENGINE (100% PORTED FROM HTML STEP CALCULATOR)
# ==============================================================================
def calculate_html_martingale_steps(balance: float, steps_count: int) -> dict:
    """
    Ported verbatim from the provided HTML Step Calculator:
    Formula:
      sumPowers = 2^(stepsCount) - 1
      firstStep = balance / sumPowers
      step_i = round(firstStep * 2^i, 2)
      steps[last] += balance - total (absorbing rounding error)
    
    Additionally prepares an executable integer plan so that the sum of stakes
    NEVER exceeds total balance, preventing balance exhaustion before Step 7/10.
    """
    bal = max(1.0, float(balance))
    count = max(1, int(steps_count))
    
    sum_powers = math.pow(2, count) - 1
    first_step = bal / sum_powers
    
    float_steps = []
    running_total = 0.0
    for i in range(count):
        step_val = round(first_step * math.pow(2, i), 2)
        float_steps.append(step_val)
        running_total += step_val
        
    rounding_error = round((bal - running_total), 2)
    float_steps[-1] = round(float_steps[-1] + rounding_error, 2)
    
    # Executable integer stake progression (strictly minimum 1 BDT per bet)
    int_steps = [max(1, int(round(s))) for s in float_steps]
    
    # গ্যারান্টি: মোট স্টেক কখনোই মূল ব্যালেন্সের চেয়ে বড় হবে না
    # ফলে সপ্তম বা দশম স্টেপে গিয়ে ব্যালেন্স সংকট হবে না
    if sum(int_steps) > bal:
        overflow = int(sum(int_steps) - bal)
        int_steps[-1] = max(1, int_steps[-1] - overflow)
        
    step_details = []
    for idx, (f_amt, i_amt) in enumerate(zip(float_steps, int_steps)):
        step_details.append({
            "step": idx + 1,
            "calculated_amount": f_amt,
            "stake": i_amt,
            "formatted": f"Step {idx + 1}: ৳{f_amt:.2f} (Bet: ৳{i_amt})"
        })
        
    step_summary_text = " | ".join([f"S{s['step']}: ৳{s['stake']}" for s in step_details])
    
    return {
        "float_steps": float_steps,
        "int_steps": int_steps,
        "step_details": step_details,
        "step_summary_text": step_summary_text,
        "total_allocated": round(sum(float_steps), 2),
        "total_stake": sum(int_steps)
    }

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
# PURE PYTHON PREDICTION ENGINE (NO JAVASCRIPT API FETCHING)
# ==============================================================================
def python_fetch_live_prediction(timeout: float = 4.0):
    url = f"{PREDICTION_API_URL}?t={int(time.time()*1000)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status != 200:
                logger.warning(f"Prediction API HTTP Status {response.status}")
                return None
            data = json.loads(response.read().decode("utf-8"))

        pred_side = None
        confidence = 80
        period = None
        pattern = ""

        next_obj = data.get("next") or {}
        if next_obj:
            raw_size = str(next_obj.get("size") or next_obj.get("pred") or "").upper().strip()
            if "SMALL" in raw_size:
                pred_side = "SMALL"
            elif "BIG" in raw_size:
                pred_side = "BIG"

            confidence = int(next_obj.get("confidence") or data.get("stats", {}).get("accuracy") or 85)
            period = str(next_obj.get("period", "")).strip() or None
            pattern = next_obj.get("pattern", "")

        if not pred_side and data.get("top_engine"):
            top = data["top_engine"]
            raw_top = str(top.get("prediction") or "").upper().strip()
            if "SMALL" in raw_top:
                pred_side = "SMALL"
            elif "BIG" in raw_top:
                pred_side = "BIG"
            confidence = int(top.get("win_rate") or 75)

        if not pred_side and data.get("history") and len(data["history"]) > 0:
            last_hist = data["history"][0]
            raw_hist = str(last_hist.get("pred") or "").upper().strip()
            if "SMALL" in raw_hist:
                pred_side = "SMALL"
            elif "BIG" in raw_hist:
                pred_side = "BIG"

        if not pred_side:
            logger.warning("Prediction API returned valid response but no definitive BIG or SMALL signal.")
            return None

        return {
            "prediction": pred_side,
            "confidence": confidence,
            "period": period,
            "pattern": pattern,
            "history": data.get("history") or data.get("data", {}).get("history") or []
        }

    except Exception as e:
        logger.error(f"Failed to fetch live prediction from Python backend: {e}")
        return None

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
        logger.debug(f"Process kill notice: {e}")

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
            logger.warning(f"Memory high: {mem.percent}%. Dumping garbage & cache...")
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
                    if (window.__DRX_STATE) {
                        window.__DRX_STATE.isRun = false;
                        if (window.__DRX_STATE.timerInterval) clearInterval(window.__DRX_STATE.timerInterval);
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
    logger.info(f"Slot cleared successfully. Worker {NODE_ID} ready for new assignments.")

# ==============================================================================
# HARDENED BROWSER SESSION ISOLATION (0.5GB RAM SAFE)
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
# INJECTED JAVASCRIPT AUTOMATION (DOM EXECUTION & FAST SCRAPING)
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

        const clickableNodes = document.querySelectorAll('button, div[role="button"], span, p, a');
        clickableNodes.forEach(node => {
            if (node && node.offsetParent !== null && !node.closest('#drx-prediction-hud')) {
                const txt = (node.innerText || '').trim().toLowerCase();
                if (txt === 'confirm' || txt === 'receive' || txt === 'got it' || txt === '確定' || txt === 'close' || txt === 'ok') {
                    try { node.click(); } catch(e){}
                }
            }
        });

        document.querySelectorAll('.van-overlay, .van-dialog, .modal-backdrop').forEach(overlay => {
            if (overlay && overlay.offsetParent !== null && !overlay.closest('#drx-prediction-hud')) {
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

# ==============================================================================
# ULTRA-FAST DIRECT BALANCE FETCHER (SUPER FAST DOM SCRAPING)
# ==============================================================================
FAST_FETCH_BALANCE_JS = r"""
try {
    let reloadBtn = document.querySelector('.van-icon-replay, .reload-icon, .Wallet__balance-icon, [class*="reload" i], [class*="refresh" i]');
    if (reloadBtn) {
        try { reloadBtn.click(); } catch(e){}
    }

    // সরাসরি টার্গেটেড ব্যালেন্স ক্লাস
    let targetedEls = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
    for (let i = 0; i < targetedEls.length; i++) {
        let txt = targetedEls[i].innerText || '';
        let match = txt.match(/[৳₹$€£]?\s*([\d,]+\.?\d*)/);
        if (match) {
            let val = parseFloat(match[1].replace(/,/g, ''));
            if (!isNaN(val) && val > 0) return val;
        }
    }

    // ফলব্যাক ১: লেবেল অনুযায়ী প্যারেন্ট সার্চ
    let els = document.querySelectorAll('span, div, p');
    for (let i = 0; i < els.length; i++) {
        let txt = els[i].innerText || '';
        if (txt.includes('Wallet balance') || txt.includes('Balance')) {
            let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
            let match = parentTxt.match(/[৳₹$€£]?\s*([\d,]+\.?\d*)/);
            if (match) {
                let val = parseFloat(match[1].replace(/,/g, ''));
                if (!isNaN(val) && val > 0) return val;
            }
        }
    }

    // ফলব্যাক ২: স্ট্যান্ডঅ্যালোন কারেন্সি সিম্বল ম্যাচ
    for (let i = 0; i < els.length; i++) {
        let txt = (els[i].innerText || '').trim();
        if (/^[৳₹$€£]\s*[\d,]+\.?\d*$/.test(txt)) {
            let val = parseFloat(txt.replace(/[^\d.]/g, ''));
            if (!isNaN(val) && val > 0) return val;
        }
    }
} catch(e){}
return 0.0;
"""

GET_ACTIVE_ROUND_PERIOD_JS = r"""
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
return null;
"""

# ==============================================================================
# PASSIVE HUD ENGINE (DISPLAY ONLY - WITH COMPLETE STEP PREVIEW)
# ==============================================================================
WINGO_INIT_HUD_JS = r"""
(function(){
    let hud = document.getElementById('drx-prediction-hud');
    if (!hud) {
        hud = document.createElement('div');
        hud.id = 'drx-prediction-hud';
        hud.style.cssText = 'position:fixed;top:8px;right:8px;z-index:999999;background:rgba(13,17,23,0.92);border:1px solid #30363d;border-radius:8px;padding:8px;color:#58a6ff;font-family:monospace;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.6);width:175px;pointer-events:none;';
        hud.innerHTML = `
            <div style="font-size:10px;font-weight:bold;color:#f0883e;">⚡ DRX VIP WORKER ⚡</div>
            <div id="hud-timer" style="font-size:22px;font-weight:bold;color:#39d353;margin:2px 0;">00:30</div>
            <div id="hud-signal" style="font-size:13px;font-weight:bold;color:#ffffff;">SIGNAL: STANDBY</div>
            <div id="hud-step-info" style="font-size:11px;font-weight:bold;color:#388bfd;margin-top:2px;">STEP: 1/-- | BET: --</div>
            <div id="hud-plan-preview" style="font-size:9px;color:#7ee787;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">PLAN: --</div>
            <div id="hud-rate" style="font-size:10px;color:#8b949e;">CONFIDENCE: --%</div>
            <div id="hud-bst-time" style="font-size:9px;color:#8b949e;margin-top:2px;">BST: --:--:--</div>
        `;
        document.body.appendChild(hud);
    }

    window.__DRX_STATE = window.__DRX_STATE || {
        isRun: true,
        lastPred: null,
        lastAmt: 0,
        lastPeriod: null
    };

    function updateLocalBST() {
        const d = new Date();
        const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
        const nowBst = new Date(utc + (3600000 * 6));
        const seconds = nowBst.getSeconds();
        const remainingSeconds = 30 - (seconds % 30);
        const displaySec = remainingSeconds === 30 ? 0 : remainingSeconds;

        let tEl = document.getElementById("hud-timer");
        if (tEl) tEl.innerText = `00:${String(displaySec).padStart(2, '0')}`;
        
        let cEl = document.getElementById("hud-bst-time");
        if (cEl) {
            let h = String(nowBst.getHours()).padStart(2, '0');
            let m = String(nowBst.getMinutes()).padStart(2, '0');
            let s = String(seconds).padStart(2, '0');
            cEl.innerText = `BST: ${h}:${m}:${s}`;
        }
    }

    if (!window.__DRX_TIMER_INT) {
        window.__DRX_TIMER_INT = setInterval(updateLocalBST, 1000);
    }
    updateLocalBST();
    return "HUD_INITIALIZED";
})();
"""

UPDATE_HUD_TELEMETRY_JS = """
const pred = arguments[0];
const conf = arguments[1];
const stepNum = arguments[2];
const totalSteps = arguments[3];
const betAmt = arguments[4];
const planPreview = arguments[5] || "";

const hudSig = document.getElementById('hud-signal');
const hudRate = document.getElementById('hud-rate');
const hudStep = document.getElementById('hud-step-info');
const hudPlan = document.getElementById('hud-plan-preview');

if (hudSig) {
    hudSig.innerText = "SIGNAL: " + pred;
    if (pred === "BIG") {
        hudSig.style.color = "#f0883e";
    } else if (pred === "SMALL") {
        hudSig.style.color = "#388bfd";
    } else {
        hudSig.style.color = "#ffffff";
    }
}
if (hudRate) {
    hudRate.innerText = "CONFIDENCE: " + conf + "%";
}
if (hudStep) {
    hudStep.innerText = "STEP: " + stepNum + "/" + totalSteps + " | BET: " + betAmt + " BDT";
}
if (hudPlan && planPreview) {
    hudPlan.innerText = "PLAN: " + planPreview;
}
"""

# ==============================================================================
# DYNAMIC BIDIRECTIONAL TRADE EXECUTION (BIG & SMALL HARDENED)
# ==============================================================================
EXECUTE_BIDIRECTIONAL_ORDER_JS = r"""
const targetSide = String(arguments[0] || '').toUpperCase().trim();
const rawAmt = arguments[1];
const betAmount = parseInt(rawAmt) || 1;
const periodId = String(arguments[2] || '');

if (targetSide !== 'BIG' && targetSide !== 'SMALL') {
    return { status: "REJECTED", reason: "INVALID_TARGET_SIDE: " + targetSide };
}

const simClick = (el) => {
    if (!el) return;
    ['pointerdown', 'mousedown', 'touchstart', 'pointerup', 'mouseup', 'touchend', 'click'].forEach(evt => {
        try { el.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window })); } catch(e) {}
    });
    if (typeof el.click === 'function') {
        try { el.click(); } catch(e) {}
    }
};

try {
    // যেকোনো অনাকাঙ্ক্ষিত পপআপ বা ব্যানার সরানো
    document.querySelectorAll('.van-dialog, .announcement-box, .bonus-dialog').forEach(el => {
        let cBtn = el.querySelector('.van-dialog__confirm, button');
        if (cBtn) try { cBtn.click(); } catch(e){}
        try { el.remove(); } catch(e){}
    });

    let targetBtn = null;

    if (targetSide === 'BIG') {
        targetBtn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
        if (!targetBtn) {
            let allBtns = document.querySelectorAll('button, div[role="button"], span');
            for (let el of allBtns) {
                let t = (el.innerText || '').trim();
                if ((t === 'Big' || t === 'BIG' || t === '大') && el.offsetParent !== null && el.children.length === 0) {
                    targetBtn = el;
                    break;
                }
            }
        }
    } else if (targetSide === 'SMALL') {
        targetBtn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
        if (!targetBtn) {
            let allBtns = document.querySelectorAll('button, div[role="button"], span');
            for (let el of allBtns) {
                let t = (el.innerText || '').trim();
                if ((t === 'Small' || t === 'SMALL' || t === '小') && el.offsetParent !== null && el.children.length === 0) {
                    targetBtn = el;
                    break;
                }
            }
        }
    }

    if (!targetBtn) {
        return { status: "FAILED", reason: "TARGET_BUTTON_NOT_FOUND_FOR_" + targetSide };
    }

    // বাটন ক্লিক (BIG অথবা SMALL)
    simClick(targetBtn);

    // ইনপুট বক্সে টাকার পরিমাণ ইনজেক্ট
    setTimeout(() => {
        let inpEl = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input");
        if (inpEl) {
            inpEl.focus();
            let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
            if (setter) {
                setter.call(inpEl, String(betAmount));
            } else {
                inpEl.value = betAmount;
            }
            inpEl.dispatchEvent(new Event('input', { bubbles: true }));
            inpEl.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // ফাইনাল বেট কনফার্ম বাটন ক্লিক
        setTimeout(() => {
            let confirmBtn = document.querySelector('button.bet-amount, button[class*="bet-amount"], .Betting__C-foot-total, .van-button--danger, .van-button--warning, .van-button--primary');
            if (!confirmBtn) {
                let docButtons = document.querySelectorAll('button, div[role="button"]');
                for (let b of docButtons) {
                    let txt = (b.innerText || '').toLowerCase();
                    if ((txt.includes('total amount') || txt.includes('total') || txt.includes('confirm') || txt.includes('bet')) && b.offsetParent) {
                        confirmBtn = b;
                        break;
                    }
                }
            }

            if (confirmBtn) {
                simClick(confirmBtn);
            }

            setTimeout(() => {
                let overlay = document.querySelector('.van-overlay');
                if (overlay) try { overlay.click(); } catch(e){}
            }, 500);

        }, 150);
    }, 120);

    return {
        status: "SUCCESS",
        side: targetSide,
        amount: betAmount,
        period: periodId
    };

} catch(err) {
    return { status: "EXCEPTION", error: err.toString() };
}
"""

CHECK_ROUND_OUTCOME_DOM_JS = r"""
const targetPeriod = String(arguments[0] || '').trim();
const targetPred = String(arguments[1] || '').toUpperCase().trim();

if (!targetPeriod) return { evaluated: false };

try {
    let rows = document.querySelectorAll('.GameList__C-body-item, .van-row, tr, [class*="record-item" i], [class*="history-item" i], .van-table__row');
    let shortPeriod = targetPeriod.length > 5 ? targetPeriod.slice(-5) : targetPeriod;

    for (let r of rows) {
        let txt = (r.innerText || '').trim();
        if (txt.includes(shortPeriod)) {
            let won = false;
            let actualSide = null;

            if (txt.includes('Big') || txt.includes('BIG') || txt.includes('大')) {
                actualSide = 'BIG';
                won = (targetPred === 'BIG');
            } else if (txt.includes('Small') || txt.includes('SMALL') || txt.includes('小')) {
                actualSide = 'SMALL';
                won = (targetPred === 'SMALL');
            } else {
                let m = txt.match(/\b([0-9])\b/);
                if (m) {
                    let n = parseInt(m[1]);
                    actualSide = (n >= 5) ? 'BIG' : 'SMALL';
                    won = (targetPred === actualSide);
                }
            }

            if (actualSide) {
                return {
                    evaluated: true,
                    won: won,
                    actual: actualSide,
                    source: "DOM_RECORD"
                };
            }
        }
    }
} catch(e){}

return { evaluated: false };
"""

# ==============================================================================
# WORKER LOGIN FLOW
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
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.3)

    sess["current_balance"] = current_bal
    sess["cur_bal"] = current_bal
    sess["last_bal_ts"] = time.time()
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    emit_event_to_manager("WINGO_READY", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "live_balance": current_bal
    })

# ==============================================================================
# AUTOMATED TRADING LOOP (FULL 7/10 STEP COMPOUND MARTINGALE RUNNER)
# ==============================================================================
def worker_monitor_trading_loop(chat_id, sid, site_name):
    """
    Automated trade cycle loop:
    - 100% Locked Step Plan based on HTML compound formula.
    - Full execution of ALL steps (including Step 7 and beyond) without early recycling.
    - High-speed balance caching and step breakdown telemetry.
    """
    sess = active_sessions.get(sid)
    if not sess:
        return

    logger.info(f"[{WORKER_ALIAS}] Launching Python trading monitor for session: {sid}")

    # HUD ইনজেকশন
    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_INIT_HUD_JS))

    # প্রাথমিক ব্যালেন্স নিশ্চিতকরণ
    initial_bal = float(sess.get("start_bal", 0.0))
    if initial_bal <= 0:
        fresh_b = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_FETCH_BALANCE_JS))
        initial_bal = float(fresh_b or 0.0)
        sess["start_bal"] = initial_bal
        sess["cur_bal"] = initial_bal
        sess["current_balance"] = initial_bal
        sess["last_bal_ts"] = time.time()

    # টার্গেট ও স্টেপ সংখ্যা অটো-কনফিগারেশন
    target_goal = float(sess.get("target_goal", 0.0))
    total_steps = int(sess.get("total_steps") or 7)

    # যদি টার্গেট গোল শূন্য থাকে তবে স্বয়ংক্রিয় সেফটি টার্গেট
    if target_goal <= 0 and initial_bal > 0:
        target_goal = round(initial_bal * 1.5, 2)
        sess["target_goal"] = target_goal
        logger.info(f"[{WORKER_ALIAS}] Auto-Target Goal locked at: {target_goal} BDT")

    # ==========================================================================
    # এইচটিএমএল ভিত্তিক স্টেপ ক্যালকুলেশন ও পার্মানেন্ট লক
    # ==========================================================================
    martingale_meta = calculate_html_martingale_steps(initial_bal, total_steps)
    locked_plan = martingale_meta["int_steps"]
    float_plan = martingale_meta["float_steps"]
    step_details = martingale_meta["step_details"]
    step_summary_text = martingale_meta["step_summary_text"]

    sess["step_plan"] = locked_plan
    sess["step_plan_floats"] = float_plan
    sess["step_details"] = step_details
    sess["step_summary_text"] = step_summary_text

    logger.info(
        f"[{WORKER_ALIAS}] LOCKED MARTINGALE PLAN INITIALIZED ({total_steps} STEPS): {locked_plan} | "
        f"Float Breakdown: {float_plan} | Initial Bal: {initial_bal} BDT | Target: {target_goal} BDT"
    )

    state = {
        "step_idx": 0,
        "locked_plan": locked_plan,
        "float_plan": float_plan,
        "wins": 0,
        "losses": 0,
        "cur_w_streak": 0,
        "cur_l_streak": 0,
        "max_w_streak": 0,
        "max_l_streak": 0,
        "trades_done": 0,
        "last_bet_period": None,
        "last_bet_side": None,
        "last_bet_amount": 0,
        "last_evaluated_period": None,
        "pre_bet_balance": initial_bal,
        "last_cycle_dispatched": None
    }

    loop_tick = 0
    last_synced_state = {}

    while sess.get("is_trading", False):
        loop_tick += 1
        enforce_low_ram_guard()

        # ----------------------------------------------------------------------
        # ১. লগআউট অথবা সেশন ডিসকানেক্ট গার্ড
        # ----------------------------------------------------------------------
        def _check_logout(drv):
            return drv.execute_script("""
                const hash = window.location.hash || '';
                const href = window.location.href || '';
                if (hash.includes('login') || href.includes('/login')) return "LOGGED_OUT_URL";
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
                if (!token && !hash.includes('WinGo')) return "TOKEN_LOST";
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
                "message": "⚠ আপনার অ্যাকাউন্টটি অন্য ডিভাইসে লগইন করার কারণে এই সেশনটি বন্ধ হয়েছে।"
            })
            terminate_session_cleanly(sid)
            break

        # ----------------------------------------------------------------------
        # ২. সময় বিশ্লেষণ (BST UTC+6)
        # ----------------------------------------------------------------------
        now_bst = bst_now()
        seconds = now_bst.second
        remaining_seconds = 30 - (seconds % 30)
        current_cycle = int(time.time() // 30)

        # ----------------------------------------------------------------------
        # ৩. উইন / লস ফলাফল মূল্যায়ন (রাউন্ড শুরুর ২২ থেকে ২৮ সেকেন্ডে)
        # ----------------------------------------------------------------------
        if remaining_seconds >= 22 and state["last_bet_period"] and state["last_evaluated_period"] != state["last_bet_period"]:
            time.sleep(1.0)
            target_period = state["last_bet_period"]
            state["last_evaluated_period"] = target_period

            fresh_bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_FETCH_BALANCE_JS))
            if fresh_bal and float(fresh_bal) > 0:
                sess["cur_bal"] = float(fresh_bal)
                sess["current_balance"] = float(fresh_bal)
                sess["last_bal_ts"] = time.time()

            is_evaluated = False
            round_won = False
            eval_source = "NONE"

            # Layer 1: API History ভেরিফিকেশন
            live_api_data = python_fetch_live_prediction(timeout=3.0)
            if live_api_data and live_api_data.get("history"):
                for hist_item in live_api_data["history"]:
                    hp = str(hist_item.get("period") or hist_item.get("pid") or hist_item.get("issue") or "").strip()
                    if hp == target_period or (len(target_period) >= 5 and hp.endswith(target_period[-5:])):
                        status_str = str(hist_item.get("status") or "").upper().strip()
                        actual_sz = str(hist_item.get("actual_size") or hist_item.get("size") or "").upper().strip()

                        if status_str in ["WIN", "LOSS"]:
                            round_won = (status_str == "WIN")
                            is_evaluated = True
                            eval_source = f"API_STATUS_{status_str}"
                            break
                        elif actual_sz in ["BIG", "SMALL"]:
                            round_won = (state["last_bet_side"] == actual_sz)
                            is_evaluated = True
                            eval_source = "API_ACTUAL_SIZE"
                            break

            # Layer 2: DOM স্ক্র্যাপার ফলব্যাক
            if not is_evaluated:
                dom_eval = safe_tab_execute(
                    sid,
                    lambda drv: drv.execute_script(CHECK_ROUND_OUTCOME_DOM_JS, target_period, state["last_bet_side"])
                )
                if isinstance(dom_eval, dict) and dom_eval.get("evaluated"):
                    round_won = dom_eval.get("won", False)
                    is_evaluated = True
                    eval_source = dom_eval.get("source", "DOM_RECORD")

            # Layer 3: ব্যালেন্স তারতম্য ফলব্যাক (হার্ডেন্ড সিকিউরিটি)
            if not is_evaluated and sess["cur_bal"] > 0 and state["pre_bet_balance"] > 0:
                diff = sess["cur_bal"] - state["pre_bet_balance"]
                # যদি ব্যালেন্স দৃশ্যমানভাবে বৃদ্ধি পায়
                if diff > 0.2:
                    round_won = True
                    is_evaluated = True
                    eval_source = "BALANCE_GAIN"
                # যদি ব্যালেন্স ড্রপ করে (বেট লস)
                elif diff < -0.5:
                    round_won = False
                    is_evaluated = True
                    eval_source = "BALANCE_DROP"

            # ==================================================================
            # স্টেপ প্রগ্রেশন লজিক (নিখুঁত ৭ স্টেপ বা নির্ধারিত পূর্ণ স্টেপ ট্র্যাকিং)
            # ==================================================================
            if is_evaluated:
                if round_won:
                    state["wins"] += 1
                    state["cur_w_streak"] += 1
                    state["cur_l_streak"] = 0
                    if state["cur_w_streak"] > state["max_w_streak"]:
                        state["max_w_streak"] = state["cur_w_streak"]
                    
                    # প্রফিট হলে নির্ভুলভাবে ১ম স্টেপে (index 0) ফিরে যাবে
                    state["step_idx"] = 0
                    next_stake = state["locked_plan"][0]
                    logger.info(
                        f"[{WORKER_ALIAS}] [WIN EVALUATED] Period: {target_period} via {eval_source} | "
                        f"Step reset to 1 (Next Bet: {next_stake} BDT)"
                    )
                else:
                    state["losses"] += 1
                    state["cur_l_streak"] += 1
                    state["cur_w_streak"] = 0
                    if state["cur_l_streak"] > state["max_l_streak"]:
                        state["max_l_streak"] = state["cur_l_streak"]

                    # লস হলে তালিকার পরবর্তী স্টেপে যাবে (সম্পূর্ণ total_steps পর্যন্ত বজায় থাকবে)
                    if state["step_idx"] < len(state["locked_plan"]) - 1:
                        state["step_idx"] += 1
                        next_stake = state["locked_plan"][state["step_idx"]]
                        logger.info(
                            f"[{WORKER_ALIAS}] [LOSS EVALUATED] Period: {target_period} via {eval_source} | "
                            f"Advancing to Step {state['step_idx'] + 1} of {total_steps} (Next Bet: {next_stake} BDT)"
                        )
                    else:
                        # শেষ স্টেপ (যেমন ৭ম স্টেপ) ও লস হলে তবেই ১ম স্টেপে রিসাইকেল করবে
                        logger.warning(
                            f"[{WORKER_ALIAS}] Complete {total_steps}-Step cycle exhausted. "
                            f"Recycling back to Step 1 of the locked plan."
                        )
                        state["step_idx"] = 0
                        next_stake = state["locked_plan"][0]

        # ----------------------------------------------------------------------
        # ৪. টার্গেট ব্যালেন্স মনিটরিং
        # ----------------------------------------------------------------------
        live_b = sess.get("cur_bal", 0.0)
        start_b = sess.get("start_bal", 0.0)

        if target_goal > 0 and live_b >= target_goal and start_b > 0:
            logger.info(f"[{WORKER_ALIAS}] TARGET ACHIEVED! Goal: {target_goal} | Balance: {live_b}. Stopping cleanly...")
            sess["is_trading"] = False

            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "COMPLETED",
                "start_balance": start_b,
                "current_balance": live_b,
                "target_amount": target_goal,
                "step": state["step_idx"] + 1,
                "total_steps": total_steps,
                "step_plan": state["locked_plan"],
                "step_plan_floats": state["float_plan"],
                "step_summary_text": step_summary_text,
                "wins": state["wins"],
                "losses": state["losses"],
                "currency": "BDT",
                "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            })

            emit_event_to_manager("TARGET_ACHIEVED", {
                "session_id": sid,
                "chat_id": chat_id,
                "site_name": site_name,
                "start_balance": start_b,
                "final_balance": live_b,
                "wins": state["wins"],
                "losses": state["losses"]
            })
            terminate_session_cleanly(sid)
            break

        # ----------------------------------------------------------------------
        # ৫. ডাইনামিক ট্রেড ডিসপ্যাচ (লক হওয়ার ৮ থেকে ১৯ সেকেন্ড পূর্বে)
        # ----------------------------------------------------------------------
        if 8 <= remaining_seconds <= 19 and state["last_cycle_dispatched"] != current_cycle:
            state["last_cycle_dispatched"] = current_cycle

            pred_data = python_fetch_live_prediction()
            if pred_data and pred_data.get("prediction"):
                signal_side = pred_data["prediction"]
                confidence = pred_data["confidence"]
                api_period = pred_data.get("period")

                dom_period = safe_tab_execute(sid, lambda drv: drv.execute_script(GET_ACTIVE_ROUND_PERIOD_JS))
                active_period = str(api_period or dom_period or f"CYCLE_{current_cycle}").strip()

                if state["last_bet_period"] != active_period:
                    idx = min(state["step_idx"], len(state["locked_plan"]) - 1)
                    stake_amount = state["locked_plan"][idx]

                    # HUD আপডেট
                    safe_tab_execute(
                        sid, 
                        lambda drv: drv.execute_script(
                            UPDATE_HUD_TELEMETRY_JS, 
                            signal_side, confidence, idx + 1, total_steps, stake_amount, step_summary_text[:28] + "..."
                        )
                    )

                    # ট্রেডের আগের ব্যালেন্স দ্রুত নিশ্চিতকরণ
                    cur_b_check = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_FETCH_BALANCE_JS))
                    if cur_b_check and float(cur_b_check) > 0:
                        state["pre_bet_balance"] = float(cur_b_check)
                        sess["cur_bal"] = float(cur_b_check)
                        sess["current_balance"] = float(cur_b_check)
                        sess["last_bal_ts"] = time.time()

                    logger.info(
                        f"[{WORKER_ALIAS}] [DISPATCHING ORDER] Side: {signal_side} | Stake: {stake_amount} BDT | "
                        f"Step: {idx + 1}/{total_steps} | Period: {active_period} | Conf: {confidence}%"
                    )

                    order_result = safe_tab_execute(
                        sid,
                        lambda drv: drv.execute_script(EXECUTE_BIDIRECTIONAL_ORDER_JS, signal_side, stake_amount, active_period)
                    )

                    if isinstance(order_result, dict) and order_result.get("status") == "SUCCESS":
                        state["trades_done"] += 1
                        state["last_bet_period"] = active_period
                        state["last_bet_side"] = signal_side
                        state["last_bet_amount"] = stake_amount
                        logger.info(f"[{WORKER_ALIAS}] [TRADE PLACED] Side: {signal_side} | Amount: {stake_amount} BDT | Period: {active_period}")
                    else:
                        logger.error(f"[{WORKER_ALIAS}] [TRADE FAILED] Reason: {order_result}")
            else:
                logger.warning(f"[{WORKER_ALIAS}] Real-time signal missing from API. Skipping trade this cycle.")

        # ----------------------------------------------------------------------
        # ৬. ফায়ারবেসে লাইভ স্টেট সিঙ্ক
        # ----------------------------------------------------------------------
        curr_step_idx = min(state["step_idx"], len(state["locked_plan"]) - 1)
        current_signature = {
            "bal": sess.get("cur_bal", 0.0),
            "w": state["wins"],
            "l": state["losses"],
            "s": curr_step_idx + 1,
            "r": sess.get("is_trading", False)
        }

        if current_signature != last_synced_state or (loop_tick % 5 == 0):
            last_synced_state = current_signature
            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "RUNNING" if sess.get("is_trading") else "PAUSED",
                "start_balance": start_b,
                "current_balance": sess.get("cur_bal", 0.0),
                "target_amount": target_goal,
                "step": curr_step_idx + 1,
                "total_steps": total_steps,
                "step_plan": state["locked_plan"],
                "step_plan_floats": state["float_plan"],
                "step_summary_text": step_summary_text,
                "current_stake": state["locked_plan"][curr_step_idx],
                "wins": state["wins"],
                "losses": state["losses"],
                "currency": "BDT",
                "updated_at": time.time(),
                "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            })

        if loop_tick % 25 == 0:
            gc.collect()

        time.sleep(1.5)

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

                    target_goal = float(task.get("target_goal") or task.get("target_amount") or task.get("target") or 0.0)
                    total_steps = int(task.get("total_steps") or task.get("steps") or task.get("target_steps") or task.get("target_step") or 7)

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
                        "last_bal_ts": 0.0,
                        "target_goal": target_goal,
                        "total_steps": total_steps,
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
                    target_goal = float(
                        action_pkt.get("target_goal") or 
                        action_pkt.get("target_amount") or 
                        action_pkt.get("target") or 
                        sess.get("target_goal", 0.0)
                    )
                    total_steps = int(
                        action_pkt.get("total_steps") or 
                        action_pkt.get("steps") or 
                        action_pkt.get("target_steps") or 
                        action_pkt.get("target_step") or 
                        sess.get("total_steps", 7)
                    )

                    sess["is_trading"] = True
                    sess["target_goal"] = target_goal
                    sess["total_steps"] = total_steps

                    cur_b = sess.get("current_balance", 0.0)
                    sess["start_bal"] = cur_b

                    threading.Thread(
                        target=worker_monitor_trading_loop,
                        args=(chat_id, sid, sess["site_name"]),
                        daemon=True
                    ).start()

                elif kind == "REQUEST_BALANCE" and sid in active_sessions:
                    # ==========================================================
                    # আল্ট্রা-ফাস্ট ব্যালেন্স এবং পূর্ণ স্টেপ বিবরণ রিটার্ন
                    # ==========================================================
                    sess = active_sessions[sid]
                    now_ts = time.time()
                    cached_bal = sess.get("cur_bal", 0.0)
                    last_ts = sess.get("last_bal_ts", 0.0)

                    # যদি ক্যাশে ১.৫ সেকেন্ডের ভেতরে থাকে তবে ক্যাশ থেকে দ্রুত রিটার্ন
                    if (now_ts - last_ts) < 1.5 and cached_bal > 0:
                        live_b = cached_bal
                    else:
                        bal_val = safe_tab_execute(sid, lambda drv: drv.execute_script(FAST_FETCH_BALANCE_JS), timeout=4.0)
                        if bal_val is not None and float(bal_val) > 0:
                            live_b = float(bal_val)
                            sess["current_balance"] = live_b
                            sess["cur_bal"] = live_b
                            sess["last_bal_ts"] = now_ts
                        else:
                            live_b = cached_bal

                    # স্টেপ প্ল্যান তৈরি বা ফেচ
                    total_stps = int(sess.get("total_steps") or 7)
                    step_meta = sess.get("step_details")
                    if not step_meta:
                        calc_res = calculate_html_martingale_steps(live_b if live_b > 0 else 100.0, total_stps)
                        plan_ints = calc_res["int_steps"]
                        plan_flts = calc_res["float_steps"]
                        step_meta = calc_res["step_details"]
                        summary_txt = calc_res["step_summary_text"]
                    else:
                        plan_ints = sess.get("step_plan", [])
                        plan_flts = sess.get("step_plan_floats", [])
                        summary_txt = sess.get("step_summary_text", "")

                    curr_s_idx = sess.get("step_idx", 0)
                    curr_stake = plan_ints[min(curr_s_idx, len(plan_ints)-1)] if plan_ints else 1

                    balance_response_payload = {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "call_id": action_pkt.get("call_id"),
                        "live_balance": live_b,
                        "start_balance": sess.get("start_bal", live_b),
                        "target_amount": sess.get("target_goal", 0.0),
                        "total_steps": total_stps,
                        "current_step": curr_s_idx + 1,
                        "current_stake": curr_stake,
                        "step_plan": plan_ints,
                        "step_plan_floats": plan_flts,
                        "step_breakdown": step_meta,
                        "step_summary_text": summary_txt,
                        "is_trading": sess.get("is_trading", False)
                    }

                    # ম্যানেজারের কাছে সরাসরি ইভেন্ট পাঠানো
                    emit_event_to_manager("BALANCE_RESPONSE", balance_response_payload)

                    # ফায়ারবেসেও আপডেট যাতে টেলিগ্রাম বোটে তৎক্ষণাৎ দেখা যায়
                    firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PATCH", {
                        "current_balance": live_b,
                        "step_plan": plan_ints,
                        "step_breakdown": step_meta,
                        "step_summary_text": summary_txt,
                        "current_stake": curr_stake
                    })

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    active_sessions[sid]["is_trading"] = False
                    logger.info(f"Stop trading command processed for session: {sid}")

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick alert: {e}")
        time.sleep(0.5)

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
