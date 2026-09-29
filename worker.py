import os
import sys
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

# ==============================================================================
# AUTOMATIC DEPENDENCY BOOTSTRAP
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [WORKER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WORKER_NODE")

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
            logger.warning(f"Installing missing dependency: {pkg_name}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "--upgrade", "--no-cache-dir", pkg_name
                ])
                logger.info(f"Successfully installed dependency: {pkg_name}")
            except Exception as e:
                logger.error(f"Failed to auto-install {pkg_name}: {e}")

ensure_dependencies()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil

# ==============================================================================
# CENTRALIZED UNICODE STYLING & TYPOGRAPHY SYSTEM
# ==============================================================================
VIP_ALPHA_MAP = {
    c: v for c, v in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")
}
BOLD_DIGIT_MAP = {d: v for d, v in zip("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")}
SUBSCRIPT_DIGIT_MAP = {d: v for d, v in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉")}

def to_vip_text(text: str) -> str:
    """Converts standard A-Z characters to VIP bold font."""
    return "".join(VIP_ALPHA_MAP.get(c.upper(), c) if c.isalpha() else c for c in str(text))

def to_bold_digits(val) -> str:
    """Converts integers/numbers to bold VIP digits."""
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

def to_subscript_digits(val) -> str:
    """Converts integers/numbers to subscript digits (ideal for % progress)."""
    return "".join(SUBSCRIPT_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# WORKER CONFIGURATION & CLUSTER REGISTRY
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json")
HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() == "true"

# Support custom terminal numbering (e.g. python3 worker.py 1 -> W-01)
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

cached_latency = 50.0

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
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
    },
    "site_tigroclub": {
        "name": "Tigro Club",
        "login": "https://tigroclub.vip/#/login",
        "wingo": "https://tigroclub.vip/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_hgnice": {
        "name": "HG Nice",
        "login": "https://hgnice.org/#/login",
        "wingo": "https://hgnice.org/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_kanpur91": {
        "name": "Kanpur 91",
        "login": "https://kanpur91.com/#/login",
        "wingo": "https://kanpur91.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    },
    "site_bdgwinsvip": {
        "name": "BDG Wins VIP",
        "login": "https://bdgwinsvip.com/#/login",
        "wingo": "https://bdgwinsvip.com/#/saasLottery/WinGo?gameCode=WinGo_30S&lottery=WinGo"
    }
}

# ==============================================================================
# FIREBASE RESILIENT SYNCHRONIZER
# ==============================================================================
def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 4.0):
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

def measure_network_latency(url: str, timeout: float = 3.5) -> float:
    try:
        start_ts = time.time()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            response.read(256)
        return round((time.time() - start_ts) * 1000, 2)
    except Exception:
        return 9999.0

def emit_event_to_manager(event_type: str, data: dict):
    payload = {
        "type": event_type,
        "worker_id": NODE_ID,
        "timestamp": time.time(),
        **data
    }
    firebase_sync_http(f"manager_events/{uuid.uuid4().hex[:10]}", "PUT", payload)

# ==============================================================================
# GUARANTEED PROCESS TEARDOWN & ZOMBIE PREVENTION
# ==============================================================================
def kill_process_tree(pid):
    """Guaranteed termination of process and all its spawned children."""
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except Exception:
                pass
        _, still_alive = psutil.wait_procs(children, timeout=1.5)
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
        parent.terminate()
        parent.wait(timeout=1.5)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    except Exception as e:
        logger.debug(f"Process tree termination: {e}")

def cleanup_zombie_browsers():
    """Scans for and cleans any abandoned firefox or geckodriver processes."""
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

def terminate_session_cleanly(session_id):
    """
    Guaranteed, strict session teardown:
    1. Stops in-browser intervals.
    2. Calls driver.quit().
    3. Force kills geckodriver and firefox processes by PID.
    4. Deletes temporary browser profile directory.
    5. Frees terminal state in Firebase so slot is instantly available.
    """
    logger.info(f"Initiating guaranteed teardown for session: {session_id}")
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

    # Reset worker node status to FREE in Firebase
    firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
        "status": "FREE",
        "assigned_user_id": None,
        "session_id": None,
        "task": None,
        "load": len(active_sessions)
    })
    logger.info(f"Teardown complete. Worker {NODE_ID} slot is now 100% FREE.")

# ==============================================================================
# HARDENED BROWSER SESSION ISOLATION
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    cleanup_zombie_browsers()

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
    options.add_argument("--width=412")
    options.add_argument("--height=915")
    options.page_load_strategy = 'eager'
    options.add_argument("-profile")
    options.add_argument(profile_dir)

    # Low RAM & Anti-Freeze Tuning
    options.set_preference("dom.ipc.processCount", 1)
    options.set_preference("browser.sessionhistory.max_entries", 2)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 1024)
    options.set_preference("javascript.options.mem.max", 32768)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
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

    driver.set_page_load_timeout(35)
    driver.set_script_timeout(20)
    driver.implicitly_wait(2)
    driver.set_window_size(412, 915)

    try:
        driver.get(target_url)
    except Exception as e:
        logger.warning(f"Initial navigation warning for {target_url}: {e}")

    sess["driver"] = driver
    sess["window_handle"] = driver.current_window_handle
    sess["last_activity"] = time.time()
    return driver, sess["window_handle"]

def safe_tab_execute(sid, task_fn, timeout=25.0):
    sess = active_sessions.get(sid)
    if not sess:
        return None

    lock = sess.get("lock")
    driver = sess.get("driver")

    if not driver or not lock:
        return None

    acquired = lock.acquire(timeout=5.0)
    if not acquired:
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
        logger.warning(f"Tab execution took longer than {timeout}s on sid: {sid}")
        return None

    if result_container["error"]:
        err_msg = str(result_container["error"])
        if "unexpectedly closed" in err_msg or "connection" in err_msg:
            logger.error(f"Driver connection lost: {err_msg}")
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
                if (el && el.offsetParent !== null && !el.closest('#sys-core-fin')) {
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
            if (node && node.offsetParent !== null && !node.closest('#sys-core-fin')) {
                const txt = (node.innerText || '').trim().toLowerCase();
                if (txt === 'confirm' || txt === 'receive' || txt === 'got it' || txt === '確定' || txt === 'close' || txt === 'ok') {
                    try { node.click(); } catch(e){}
                }
            }
        });

        document.querySelectorAll('.van-overlay, .van-dialog, .modal-backdrop').forEach(overlay => {
            if (overlay && overlay.offsetParent !== null && !overlay.closest('#sys-core-fin')) {
                try { overlay.remove(); } catch(e){}
            }
        });
    };

    sweepModals();
    if (!window.__SWEEPER_INTERVAL) {
        window.__SWEEPER_INTERVAL = setInterval(sweepModals, 600);
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
    }, 400);
}, 400);

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
# 9. INTEGRATED TIMER-BASED EXECUTION ENGINE (WITH GUARDRAILS & EXPIRATION TRIGGER)
# ==============================================================================
WINGO_CORE_JS = r"""
const autoTargetGoal = parseFloat(arguments[0]) || 0;
const autoTotalSteps = parseInt(arguments[1]) || 5;
const targetApiUrl = arguments[2] || "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json";

(function(){
    let ghostContainer = document.getElementById('sys-core-fin');
    if (!ghostContainer) {
        ghostContainer = document.createElement('div');
        ghostContainer.id = 'sys-core-fin';
        ghostContainer.setAttribute('style', 'display: none !important; opacity: 0 !important; pointer-events: none !important; position: fixed !important; top: -9999px !important; left: -9999px !important; width: 0 !important; height: 0 !important; z-index: -9999 !important; overflow: hidden !important;');
        document.body.appendChild(ghostContainer);
    }

    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, parseInt(autoTotalSteps) || 5);
        if (autoTargetGoal && autoTargetGoal > 0) {
            let liveBal = (typeof chkBal === 'function') ? chkBal() : window.__WINGO_ST.curBal;
            window.__WINGO_ST.tgtAmt = (autoTargetGoal <= liveBal && liveBal > 0) ? (liveBal + autoTargetGoal) : autoTargetGoal;
        }
        return "ALREADY_RUNNING_UPDATED";
    }

    if (window.__WINGO_ST) {
        if (window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt);
        if (window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt);
    }

    const cfg = { fRt: 300, syncDly: 2500, minSf: 10 };
    const st = {
        isRun: true,
        tgtAmt: 0,
        startBal: 0,
        curBal: 0,
        autoInt: null,
        timerInt: null,
        isTrd: false,
        stpIdx: 0,
        steps: Math.max(1, parseInt(autoTotalSteps) || 5),
        dynSeq: [],
        tradesDone: 0,
        lastPred: null,
        lastPeriod: null,
        circuitBreakerTriggered: false,
        w: 0,
        l: 0,
        cur_w_streak: 0,
        cur_l_streak: 0,
        max_w_streak: 0,
        max_l_streak: 0
    };
    window.__WINGO_ST = st;

    function chkBal() {
        try {
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
            let els = document.querySelectorAll('*');
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
            for (let i = 0; i < els.length; i++) {
                let txt = els[i].innerText || '';
                if (txt.trim().match(/^[৳₹$€£]\s*[\d,]+\.?\d*$/)) {
                    st.curBal = parseFloat(txt.replace(/[^\d.]/g, ''));
                    return st.curBal;
                }
            }
        } catch(e) {}
        return st.curBal || 0;
    }

    // Target Balance Pre-Check Guardrail (strictly halts trading & eliminates race conditions)
    function isTargetReached() {
        let liveBal = chkBal();
        if (st.tgtAmt > 0 && liveBal >= st.tgtAmt && st.startBal > 0) {
            st.isRun = false;
            st.isTrd = false;
            if (st.autoInt) clearInterval(st.autoInt);
            if (st.timerInt) clearInterval(st.timerInt);
            return true;
        }
        return false;
    }

    // WinGo 30s Countdown Inspector
    function getRemainingSeconds() {
        try {
            const timeSelectors = [
                '.time-box', '.Time', '.van-count-down', '[class*="countdown" i]',
                '.Betting__C-head-r', '.clock', '[class*="TimeBox" i]', '[class*="time" i]'
            ];
            for (let sel of timeSelectors) {
                let el = document.querySelector(sel);
                if (el && el.offsetParent !== null) {
                    let txt = (el.innerText || '').trim();
                    let m = txt.match(/(\d+)\s*:\s*(\d+)/);
                    if (m) {
                        return (parseInt(m[1], 10) * 60) + parseInt(m[2], 10);
                    }
                    let spans = el.querySelectorAll('span, div, p');
                    if (spans.length >= 2) {
                        let digits = [];
                        spans.forEach(s => {
                            let t = (s.innerText || '').trim();
                            if (/^\d+$/.test(t) && t.length <= 2) digits.push(t);
                        });
                        if (digits.length >= 2) {
                            let secStr = digits.slice(-2).join('');
                            let parsed = parseInt(secStr, 10);
                            if (!isNaN(parsed) && parsed <= 60) return parsed;
                        }
                    }
                }
            }
            let allTimeEls = document.querySelectorAll('*');
            for (let i = 0; i < allTimeEls.length; i++) {
                let txt = (allTimeEls[i].innerText || '').trim();
                let m = txt.match(/^00\s*:\s*(\d{2})$/);
                if (m) {
                    return parseInt(m[1], 10);
                }
            }
        } catch(e){}
        return -1;
    }

    const calcSeq = (cBal, nSteps) => {
        let B = Math.floor(Number(cBal)) || 0;
        let n = parseInt(nSteps) || 5;
        if (n < 1) n = 1;
        let u = Math.pow(2, n) - 1;
        let s1 = Math.floor(B / u);
        if (s1 < 1) s1 = 1;
        let seq = [];
        let sum = 0;
        for (let k = 1; k < n; k++) {
            let sk = Math.floor(s1 * Math.pow(2, k - 1));
            seq.push(sk);
            sum += sk;
        }
        let sn = Math.floor(B - sum);
        seq.push(sn > 0 ? sn : Math.floor(s1 * Math.pow(2, n - 1)));
        return seq;
    };

    const getNextLivePeriod = (str) => {
        let chars = String(str).split('');
        for (let i = chars.length - 1; i >= 0; i--) {
            if (chars[i] !== '9') {
                chars[i] = String.fromCharCode(chars[i].charCodeAt(0) + 1);
                return chars.join('');
            }
            chars[i] = '0';
        }
        return '1' + chars.join('');
    };

    const drx_triggerEvent = (el, etype) => {
        let ev = new Event(etype, { bubbles: true, cancelable: true });
        el.dispatchEvent(ev);
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

    // Robust, non-skipping trade executor
    const exeTrd = (pred, amt, cb) => {
        try {
            // Guardrail Pre-Check before executing any DOM action
            if (isTargetReached()) {
                if (cb) cb(false);
                return;
            }

            // Guard: Never place bet during locked last 5 seconds of round
            let remSec = getRemainingSeconds();
            if (remSec <= 5 && remSec > 0) {
                if (cb) cb(false);
                return;
            }

            // Dismiss any lingering overlay first so buttons are 100% clickable
            let lingeringDialog = document.querySelector('.van-dialog, .announcement-box');
            if (lingeringDialog) {
                let cBtn = lingeringDialog.querySelector('.van-dialog__confirm, button');
                if (cBtn) try { cBtn.click(); } catch(e){}
                try { lingeringDialog.remove(); } catch(e){}
            }

            let btn = null;
            let targetText = String(pred).toLowerCase().trim();
            let btns = document.querySelectorAll('button, div, span');
            for (let i = 0; i < btns.length; i++) {
                let t = (btns[i].innerText || '').trim().toLowerCase();
                if (t === targetText && btns[i].offsetParent && !btns[i].children.length) {
                    btn = btns[i];
                    break;
                }
            }
            if (!btn) {
                if (targetText === 'big') btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i], div[class*="big" i]');
                else if (targetText === 'small') btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i], div[class*="small" i]');
                else if (targetText === 'green') btn = document.querySelector('button[class*="green"], div[class*="green"]');
                else if (targetText === 'red') btn = document.querySelector('button[class*="red"], div[class*="red"]');
                else if (targetText === 'violet') btn = document.querySelector('button[class*="violet"], div[class*="violet"]');
            }
            if (!btn) {
                if (cb) cb(false);
                return;
            }
            drx_simClick(btn);

            // Interval-based waiting for Vant UI modal & stepper input to fully mount
            let checkAttempts = 0;
            let valInterval = setInterval(() => {
                checkAttempts++;

                // Immediate abort if target reached while modal was opening
                if (isTargetReached()) {
                    clearInterval(valInterval);
                    let closeBtn = document.querySelector('.van-popup__close-icon, .dialog-close, button.van-dialog__cancel');
                    if (closeBtn) try { closeBtn.click(); } catch(e){}
                    if (cb) cb(false);
                    return;
                }

                let inpEl = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input, input[inputmode='numeric']");
                if (inpEl || checkAttempts > 18) {
                    clearInterval(valInterval);
                    if (inpEl) {
                        inpEl.focus();
                        let setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                        if (setV) setV.call(inpEl, String(amt));
                        else inpEl.value = amt;
                        drx_triggerEvent(inpEl, 'input');
                        drx_triggerEvent(inpEl, 'change');
                        drx_triggerEvent(inpEl, 'blur');
                    }
                    setTimeout(() => {
                        // Strict check before final confirm click
                        if (isTargetReached()) {
                            let closeBtn = document.querySelector('.van-popup__close-icon, .dialog-close, button.van-dialog__cancel');
                            if (closeBtn) try { closeBtn.click(); } catch(e){}
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
                        if (dEl) {
                            drx_simClick(dEl);
                        }
                        setTimeout(() => {
                            if (cb) cb(true);
                        }, 1800);
                    }, 700);
                }
            }, 180);
        } catch(e) {
            if (cb) cb(false);
        }
    };

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    let targetProfitVal = parseFloat(autoTargetGoal) || 0;
    st.tgtAmt = (targetProfitVal <= initialBal && initialBal > 0) ? (initialBal + targetProfitVal) : targetProfitVal;
    st.dynSeq = calcSeq(initialBal > 0 ? initialBal : st.tgtAmt, st.steps);
    st.stpIdx = 0;
    sessionStorage.removeItem('drx_sig');

    let isFetchingApi = false;
    let isExecutingCycle = false;

    // Automated Prediction Fetch & Immediate Execution Workflow
    const triggerAutomatedExecution = async () => {
        // Guardrail 1: Target Balance Pre-Check
        if (isTargetReached()) return;
        if (!st.isRun || st.isTrd || isFetchingApi || isExecutingCycle) return;

        isExecutingCycle = true;
        isFetchingApi = true;

        try {
            // Guardrail 2: Verify balance before dispatching prediction API call
            if (isTargetReached()) {
                isFetchingApi = false;
                isExecutingCycle = false;
                return;
            }

            let ts = Math.floor(Date.now() / 1000);
            let sep = targetApiUrl.includes('?') ? '&' : '?';
            let fetchUrl = targetApiUrl + sep + "page=1&ts=" + ts;
            let dataArray = null;

            try {
                let res = await fetch(fetchUrl);
                if (res.ok) {
                    dataArray = await res.json();
                }
            } catch(fetchErr) {
                // Secondary fallback attempt if primary endpoint has momentary network error
                try {
                    let fallbackUrl = "https://data-vip-247-hack.ai.studio/apipid.json?page=1&ts=" + ts;
                    let res2 = await fetch(fallbackUrl);
                    if (res2.ok) dataArray = await res2.json();
                } catch(e2){}
            }

            // Guardrail 3: Verify target balance immediately post-API response
            if (isTargetReached()) {
                isFetchingApi = false;
                isExecutingCycle = false;
                return;
            }

            if (dataArray) {
                let activeLogic = Array.isArray(dataArray) ? dataArray[0] : (dataArray.data ? dataArray.data[0] : dataArray);
                if (activeLogic) {
                    let tempHist = activeLogic.history || (activeLogic.data && activeLogic.data.history) || [];
                    let cSig = '';
                    if (tempHist[0] && (tempHist[0].pid || tempHist[0].period)) {
                        cSig = getNextLivePeriod(String(tempHist[0].pid || tempHist[0].period));
                    }
                    if (!cSig && activeLogic.next && (activeLogic.next.period || activeLogic.next.pid)) {
                        cSig = String(activeLogic.next.period || activeLogic.next.pid);
                    }
                    if (!cSig && activeLogic.period) {
                        cSig = String(activeLogic.period);
                    }
                    let sSig = sessionStorage.getItem('drx_sig');

                    if (cSig && cSig !== sSig) {
                        // A. Evaluate Previous Round Result
                        if (st.lastPred && st.lastPred !== 'SKIP' && st.lastPeriod) {
                            let actualData = tempHist[0];
                            let actualR = '';
                            if (actualData) {
                                if (actualData.actual_size) {
                                    actualR = String(actualData.actual_size).toUpperCase().trim();
                                } else if (actualData.actual === 'BIG' || actualData.actual === 1 || (typeof actualData.actual === 'number' && actualData.actual >= 5)) {
                                    actualR = 'BIG';
                                } else if (actualData.actual === 'SMALL' || actualData.actual === 0 || (typeof actualData.actual === 'number' && actualData.actual < 5)) {
                                    actualR = 'SMALL';
                                }
                            }
                            let won = false;
                            if (actualR) {
                                won = (st.lastPred === actualR);
                            } else {
                                let prevRecordedBal = parseFloat(sessionStorage.getItem('drx_p_bal') || '0');
                                if (prevRecordedBal > 0 && st.curBal > prevRecordedBal) {
                                    won = true;
                                }
                            }

                            if (won) {
                                st.w++;
                                st.cur_w_streak++;
                                st.cur_l_streak = 0;
                                if (st.cur_w_streak > st.max_w_streak) st.max_w_streak = st.cur_w_streak;
                                st.stpIdx = 0;
                            } else {
                                st.l++;
                                st.cur_l_streak++;
                                st.cur_w_streak = 0;
                                if (st.cur_l_streak > st.max_l_streak) st.max_l_streak = st.cur_l_streak;

                                // Max Step Failure (Circuit Breaker)
                                if (st.stpIdx >= st.steps - 1) {
                                    st.circuitBreakerTriggered = true;
                                    st.isRun = false;
                                    st.isTrd = false;
                                    if (st.autoInt) clearInterval(st.autoInt);
                                    if (st.timerInt) clearInterval(st.timerInt);
                                    isFetchingApi = false;
                                    isExecutingCycle = false;
                                    return;
                                } else {
                                    st.stpIdx = Math.min(st.stpIdx + 1, st.dynSeq.length - 1);
                                }
                            }
                        }

                        st.lastPred = null;
                        st.lastPeriod = cSig;
                        st.isTrd = true;

                        // Guardrail 4: Verify target balance before staking
                        let nBal = chkBal();
                        if (isTargetReached()) {
                            st.isTrd = false;
                            isFetchingApi = false;
                            isExecutingCycle = false;
                            return;
                        }

                        st.dynSeq = calcSeq(nBal > 0 ? nBal : st.tgtAmt, st.steps);
                        if (st.stpIdx >= st.dynSeq.length) st.stpIdx = st.dynSeq.length - 1;
                        let tAmt = Math.floor(st.dynSeq[st.stpIdx]) || 1;

                        if (nBal > 0 && nBal < tAmt) {
                            st.stpIdx = 0;
                            st.isTrd = false;
                            isFetchingApi = false;
                            isExecutingCycle = false;
                            return;
                        }

                        let rawPred = activeLogic.pred || activeLogic.prediction || (activeLogic.next && (activeLogic.next.size || activeLogic.next.pred)) || 'BIG';
                        let prediction = String(rawPred).toUpperCase().trim();

                        if (prediction === 'SKIP') {
                            st.lastPred = null;
                            sessionStorage.setItem('drx_sig', cSig);
                            setTimeout(() => { 
                                st.isTrd = false; 
                                isExecutingCycle = false;
                            }, 1000);
                        } else {
                            if (!['BIG', 'SMALL'].includes(prediction)) {
                                prediction = (st.tradesDone % 2 === 0) ? 'BIG' : 'SMALL';
                            }
                            st.lastPred = prediction;

                            // Guardrail 5: Final pre-trade check strictly prior to DOM dispatch
                            if (isTargetReached()) {
                                st.isTrd = false;
                                isFetchingApi = false;
                                isExecutingCycle = false;
                                return;
                            }

                            // Immediate automated execution on received prediction data
                            exeTrd(prediction, tAmt, (suc) => {
                                if (suc) {
                                    sessionStorage.setItem('drx_sig', cSig);
                                    sessionStorage.setItem('drx_p_bal', String(st.curBal));
                                    st.tradesDone++;
                                } else {
                                    st.lastPred = null;
                                }
                                setTimeout(() => { 
                                    st.isTrd = false; 
                                    isExecutingCycle = false;
                                    isTargetReached();
                                }, 1000);
                            });
                        }
                    }
                }
            }
        } catch(e) {
            st.isTrd = false;
            isExecutingCycle = false;
        }
        isFetchingApi = false;
    };

    // Close Countdown Timer Monitoring & Zero-Expiration Trigger
    let lastRemSec = -1;
    let cycleTriggered = false;

    const timerMonitorTask = () => {
        if (!st.isRun) return;
        if (isTargetReached()) return;

        let remSec = getRemainingSeconds();
        let epochSec = Math.floor(Date.now() / 1000) % 30;
        let epochRem = (30 - epochSec) % 30;

        let isExpired = false;

        if (remSec !== -1) {
            // Hit zero directly
            if (remSec === 0) {
                isExpired = true;
            }
            // Transition wrap-around: was near end (<= 3s) and wrapped back to high (>= 24s)
            else if (lastRemSec >= 0 && lastRemSec <= 3 && remSec >= 24) {
                isExpired = true;
            }

            // Reset/re-arm timer trigger for next cycle when safely mid-round (4s to 26s)
            if (remSec > 4 && remSec < 26) {
                cycleTriggered = false;
            }

            lastRemSec = remSec;
        } else {
            // High-precision epoch 30-second boundary fallback
            if (epochRem === 0 || (lastRemSec === 1 && epochRem === 0)) {
                isExpired = true;
            }
            if (epochRem > 4 && epochRem < 26) {
                cycleTriggered = false;
            }
            lastRemSec = epochRem;
        }

        // Trigger automated workflow immediately at the exact expiration moment
        if (isExpired && !cycleTriggered) {
            cycleTriggered = true;
            triggerAutomatedExecution();
        }
    };

    // 15-second trade-lock watchdog (prevents st.isTrd or isExecutingCycle from staying stuck)
    let tradeLockTs = 0;
    setInterval(() => {
        if (st.isTrd || isExecutingCycle) {
            if (!tradeLockTs) tradeLockTs = Date.now();
            else if (Date.now() - tradeLockTs > 15000) {
                st.isTrd = false;
                isFetchingApi = false;
                isExecutingCycle = false;
                tradeLockTs = 0;
            }
        } else {
            tradeLockTs = 0;
        }
    }, 3000);

    // High-frequency 200ms timer monitoring interval
    st.timerInt = setInterval(timerMonitorTask, 200);
    st.autoInt = st.timerInt;
    return "GHOST_TRADING_INITIATED_24_7";
})();
"""

# ==============================================================================
# WORKER EXECUTION FLOWS
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
    # Stage 1: 20%
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 20,
        "text": "Initializing dedicated browser container...",
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

    # Stage 2: 40%
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 40,
        "text": "Navigating to platform portal & bypassing guards...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    fill_ok = False
    for _ in range(70):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(1.5)
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

    # Stage 3: 60%
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
    for _ in range(40):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "CONFIRM_CLICKED":
                time.sleep(1.2)
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

    # Stage 4: 80%
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 80,
        "text": "Dismissing announcements & securing session token...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    time.sleep(0.8)

    # Stage 5: 100%
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 100,
        "text": "Authentication verified! Ready for trade setup.",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })
    time.sleep(0.5)

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
        time.sleep(1.8)

        is_ready = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS))
        if is_ready:
            verified = True
            break
        time.sleep(0.8)

    if not verified:
        safe_tab_execute(sid, lambda drv: drv.get(wingo_url))
        time.sleep(2.5)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    current_bal = 0.0
    for _ in range(15):
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
    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

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

            task_payload = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "CIRCUIT_BREAKER_STOPPED" if circuit_breaker else ("RUNNING" if is_run else "PAUSED"),
                "start_balance": start_b,
                "current_balance": sess["cur_bal"],
                "target_amount": tgt_amt,
                "step": step_idx,
                "total_steps": tot_steps,
                "wins": sess["wins"],
                "losses": sess["losses"],
                "currency": "BDT",
                "updated_at": time.time()
            }
            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

            # Max Step Failure Circuit Breaker check
            if circuit_breaker:
                sess["is_trading"] = False
                emit_event_to_manager("CIRCUIT_BREAKER_TRIGGERED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": start_b,
                    "final_balance": sess["cur_bal"],
                    "step": step_idx,
                    "total_steps": tot_steps,
                    "wins": sess["wins"],
                    "losses": sess["losses"]
                })
                terminate_session_cleanly(sid)
                break

            # Check if target balance is genuinely reached
            if tgt_amt > 0 and sess["cur_bal"] >= tgt_amt and start_b > 0:
                sess["is_trading"] = False
                task_payload["status"] = "COMPLETED"
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
                # Immediately teardown browser and free worker slot
                terminate_session_cleanly(sid)
                break
            elif not is_run:
                sess["is_trading"] = False
                break

        time.sleep(3.0)

# ==============================================================================
# WORKER TASK AND ACTION LISTENER LOOP
# ==============================================================================
def worker_task_listener():
    logger.info(f"Worker task polling initiated on node: {NODE_ID}...")
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
                    logger.warning(f"Emergency stop received: {kind}. Terminating all worker sessions!")
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
                    safe_tab_execute(sid, lambda drv: drv.execute_script("if(window.__WINGO_ST){ window.__WINGO_ST.isRun = false; if(window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt); if(window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt); }"))
                    active_sessions[sid]["is_trading"] = False

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick: {e}")
        time.sleep(0.8)

# ==============================================================================
# HEARTBEAT & CLUSTER REGISTRATION LOOP
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
        "registered_at": time.time()
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
                "latency_ms": cached_latency
            }
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", hb_data)
        except Exception:
            pass
        time.sleep(3.0)

def continuous_24h_watchdog():
    """24/7 Watchdog: Cleans abandoned stale sessions while preserving active trading sessions."""
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
    logger.info(f"Shutdown signal caught on {WORKER_ALIAS}. Commencing clean cluster teardown...")
    WORKER_ACTIVE = False
    try:
        # Immediately delete self from Firebase so no offline ghost is left behind
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
