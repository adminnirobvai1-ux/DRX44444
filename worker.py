# ==============================================================================
# DRX WINGO CLUSTER - 24/7 CONTINUOUS EXECUTION WORKER NODE
# ==============================================================================
# Responsibilities:
# - Continuous 24/7 Non-Stop Automated Trading (Zero Unexpected Shutdowns)
# - Bulletproof DOM + API Multi-Layer Win/Loss Evaluation
# - Exact Step-Maker Martingale Mathematics (JavaScript 2^N - 1 Scaling)
# - Anti-Double Trade Guard (Strict Single Trade per Period Lock)
# - Ultra-Low RAM (0.5GB) & Low CPU Utilization Profile
# - Automatic Milestone Profit Rollover & Sequence Reset
# ==============================================================================

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
    return "".join(VIP_ALPHA_MAP.get(c.upper(), c) if c.isalpha() else c for c in str(text))

def to_bold_digits(val) -> str:
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

def to_subscript_digits(val) -> str:
    return "".join(SUBSCRIPT_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# WORKER CONFIGURATION & CLUSTER REGISTRY
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://drx-tm-vip-hack-code6.edgeone.dev/pid.json")
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
    logger.info(f"Initiating teardown for session: {session_id}")
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
    logger.info(f"Session {session_id} freed.")

# ==============================================================================
# HARDENED BROWSER SESSION ISOLATION (0.5GB RAM TUNED)
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

    # 0.5GB Low Memory & Ultra-Low CPU Configuration
    options.set_preference("dom.ipc.processCount", 1)
    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 512)
    options.set_preference("javascript.options.mem.max", 16384)
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

def safe_tab_execute(sid, task_fn, timeout=20.0):
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

    if not result_container["completed"] or result_container["error"]:
        return None

    return result_container["res"]

# ==============================================================================
# INJECTED JAVASCRIPT AUTOMATION & MODAL CLEANER
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

        document.querySelectorAll('.van-overlay, .van-dialog, .modal-backdrop').forEach(overlay => {
            if (overlay && overlay.offsetParent !== null && !overlay.closest('#sys-core-fin') && !overlay.closest('#drx-prediction-hud')) {
                try { overlay.remove(); } catch(e){}
            }
        });
    };

    sweepModals();
    if (!window.__SWEEPER_INTERVAL) {
        window.__SWEEPER_INTERVAL = setInterval(sweepModals, 1200);
    }
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

if (!window.location.hash.includes('login')) {
    window.location.hash = '#/login';
}

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input');

let elP = document.querySelector('input[type="password"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input');

let elL = document.querySelector('button[type="submit"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');

if (!elN || !elP || !elL) return "NOT_READY";

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

const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const dText = dialog.innerText || '';
    if (dText.includes('already logged in') || dText.includes('somewhere else') || 
        dText.includes('logged in') || dText.includes('22') || dText.includes('other device') ||
        dText.includes('Confirm') || dText.includes('continue')) {
        const confirmBtn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm" i], .van-button--danger, .van-button--primary, button');
        if (confirmBtn) {
            try { confirmBtn.click(); } catch(e){}
            return { status: "CONFIRM_CLICKED", message: "Auto-confirmed device prompt" };
        }
    }
}

try {
    const t1 = localStorage.getItem('token') || localStorage.getItem('token_str') || localStorage.getItem('auth');
    const t2 = sessionStorage.getItem('token') || sessionStorage.getItem('auth');
    if (t1 || t2) return { status: "SUCCESS" };
} catch(e){}

if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) {
    return { status: "SUCCESS" };
}

return { status: "PENDING" };
"""

WINGO_PERSISTENT_NAV_JS = """
const targetUrl = arguments[0];
(function(){
    const currentHash = window.location.hash || '';
    const currentHref = window.location.href || '';
    const bodyTxt = document.body ? document.body.innerText : '';

    if (currentHash.includes('WinGo') || currentHref.includes('WinGo') || bodyTxt.includes('Time remaining') || bodyTxt.includes('30S')) {
        return "ALREADY_VERIFIED";
    }

    try {
        if (!window.location.href.includes('WinGo')) {
            window.location.href = targetUrl;
        }
    } catch(e){}
    return "NAV_INJECTED";
})();
"""

CHECK_WINGO_READY_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';
const bodyText = document.body ? document.body.innerText : '';
return (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Time remaining') || bodyText.includes('30S'));
"""

FETCH_BALANCE_JS = r"""
(function(){
    // Refresh icon click to fetch latest live balance
    let refBtn = document.querySelector('.van-icon-replay, .van-icon-refresh, [class*="reload" i], [class*="refresh" i]');
    if (refBtn) { try { refBtn.click(); } catch(e){} }

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
    return 0.0;
})();
"""

# ==============================================================================
# INTEGRATED 24/7 CORE TRADING ENGINE JAVASCRIPT
# ==============================================================================
WINGO_CORE_JS = r"""
const autoTargetGoal = parseFloat(arguments[0]) || 0;
const autoTotalSteps = parseInt(arguments[1]) || 5;
const predictionApiUrl = arguments[2] || "https://drx-tm-vip-hack-code6.edgeone.dev/pid.json";

(function(){
    let hud = document.getElementById('drx-prediction-hud');
    if (!hud) {
        hud = document.createElement('div');
        hud.id = 'drx-prediction-hud';
        hud.style.cssText = 'position:fixed;top:10px;right:10px;z-index:999999;background:rgba(13,17,23,0.92);border:2px solid #30363d;border-radius:10px;padding:12px;color:#58a6ff;font-family:monospace;text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.6);width:170px;pointer-events:none;';
        hud.innerHTML = `
            <div style="font-size:11px;font-weight:bold;color:#f0883e;">DRX 24/7 ENGINE</div>
            <div id="timer" style="font-size:26px;font-weight:bold;color:#39d353;margin:4px 0;">00:30</div>
            <div id="hud-signal" style="font-size:14px;font-weight:bold;color:#ffffff;">SIGNAL: --</div>
            <div id="hud-rate" style="font-size:10px;color:#8b949e;">WIN RATE: --%</div>
        `;
        document.body.appendChild(hud);
    }

    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, autoTotalSteps);
        if (autoTargetGoal > 0) window.__WINGO_ST.tgtAmt = autoTargetGoal;
        return "ALREADY_RUNNING_UPDATED";
    }

    if (window.__WINGO_ST && window.__WINGO_ST.timerInt) {
        clearInterval(window.__WINGO_ST.timerInt);
    }

    const st = {
        isRun: true,
        tgtAmt: autoTargetGoal,
        startBal: 0.0,
        curBal: 0.0,
        timerInt: null,
        isTrd: false,
        stpIdx: 0,
        steps: Math.max(1, autoTotalSteps),
        dynSeq: [],
        tradesDone: 0,
        lastPred: null,
        lastBetPeriod: null,
        lastBetAmt: 0,
        evaluatedPeriod: null,
        lastTriggeredCycle: null,
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
        } catch(e) {}
        return st.curBal || 0.0;
    }

    function refreshWallet() {
        try {
            let refBtn = document.querySelector('.van-icon-replay, .van-icon-refresh, [class*="reload" i], [class*="refresh" i]');
            if (refBtn) refBtn.click();
        } catch(e){}
    }

    function updateTimer() {
        const now = new Date();
        const seconds = now.getSeconds();
        const remainingSeconds = 30 - (seconds % 30);
        const displaySec = remainingSeconds === 30 ? 0 : remainingSeconds;

        let timerEl = document.getElementById("timer");
        if (timerEl) {
            timerEl.innerText = `00:${String(displaySec).padStart(2, '0')}`;
        }
        return displaySec;
    }

    function getLiveRoundId() {
        try {
            let allTextEls = document.querySelectorAll('div, span, p, h3');
            for (let i = 0; i < allTextEls.length; i++) {
                let t = (allTextEls[i].innerText || '').trim();
                if (/^20\d{12,18}$/.test(t) && allTextEls[i].children.length === 0) {
                    return t;
                }
            }
            let pEl = document.querySelector('.Game__C-title-sub, .Time__C-num, [class*="period" i], [class*="issue" i]');
            if (pEl) {
                let m = (pEl.innerText || '').match(/(\d{12,20})/);
                if (m) return m[1];
            }
        } catch(e){}
        return 'EPOCH_' + Math.floor(Date.now() / 30000);
    }

    // =========================================================================
    // EXACT STEP-MAKER FORMULA (2^N - 1)
    // =========================================================================
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

    // =========================================================================
    // DIRECT ACCURATE DOM GAME-HISTORY PARSER
    // =========================================================================
    function getActualPeriodOutcomeFromDom(targetPeriod) {
        if (!targetPeriod) return null;
        let tPeriod = String(targetPeriod).trim();

        let rows = document.querySelectorAll('tr, .van-table__row, [class*="history-item"], [class*="record" i], .van-row');
        for (let r of rows) {
            let txt = (r.innerText || '').trim();
            if (txt.includes(tPeriod)) {
                let uTxt = txt.toUpperCase();
                if (uTxt.includes('BIG') && !uTxt.includes('SMALL')) return 'BIG';
                if (uTxt.includes('SMALL') && !uTxt.includes('BIG')) return 'SMALL';
                
                let match = txt.replace(tPeriod, '').match(/\b([0-9])\b/);
                if (match) {
                    return parseInt(match[1]) >= 5 ? 'BIG' : 'SMALL';
                }
            }
        }

        let allEls = document.querySelectorAll('div, span, td, p');
        for (let el of allEls) {
            if (el.children.length === 0 && (el.innerText || '').trim() === tPeriod) {
                let parent = el.closest('tr') || el.closest('.van-row') || el.parentElement?.parentElement || el.parentElement;
                if (parent) {
                    let pTxt = (parent.innerText || '').toUpperCase();
                    if (pTxt.includes('BIG')) return 'BIG';
                    if (pTxt.includes('SMALL')) return 'SMALL';
                    let match = pTxt.replace(tPeriod, '').match(/\b([0-9])\b/);
                    if (match) {
                        return parseInt(match[1]) >= 5 ? 'BIG' : 'SMALL';
                    }
                }
            }
        }
        return null;
    }

    function resolvePredictionFromServers(rawJson) {
        let serverList = [];
        if (Array.isArray(rawJson.servers) && rawJson.servers.length > 0) {
            serverList = rawJson.servers;
        } else if (rawJson.data && Array.isArray(rawJson.data.servers) && rawJson.data.servers.length > 0) {
            serverList = rawJson.data.servers;
        }

        if (serverList.length === 0) {
            if (rawJson.top_engine && rawJson.top_engine.prediction) {
                let p = String(rawJson.top_engine.prediction).toUpperCase().trim();
                return { pred: p.includes('SMALL') ? 'SMALL' : 'BIG', rate: 70 };
            }
            return { pred: 'BIG', rate: 50 };
        }

        let parsed = serverList.map(s => {
            let rateRaw = String(s.win_rate || s.percentage || s.rate || '0');
            let m = rateRaw.match(/(\d+\.?\d*)/);
            let rateNum = m ? parseFloat(m[1]) : 0.0;
            let rawP = String(s.prediction || s.result || s.pred || s.size || '').toUpperCase().trim();
            let normP = rawP.includes('SMALL') ? 'SMALL' : (rawP.includes('BIG') ? 'BIG' : '');
            return { server: s.server || s.name || '', rate: rateNum, pred: normP };
        }).filter(item => item.pred === 'BIG' || item.pred === 'SMALL');

        if (parsed.length === 0) return { pred: 'BIG', rate: 50 };

        let maxRate = Math.max(...parsed.map(x => x.rate));
        let top = parsed.filter(x => Math.abs(x.rate - maxRate) < 0.01);
        let bigs = top.filter(x => x.pred === 'BIG').length;
        let smalls = top.filter(x => x.pred === 'SMALL').length;

        if (top.length === 1) return { pred: top[0].pred, rate: maxRate };
        return { pred: bigs >= smalls ? 'BIG' : 'SMALL', rate: maxRate };
    }

    const exeTrdFast = (pred, amt, cb) => {
        try {
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
                    }, 120);
                }, 160);
            }, 100);
        } catch(e) {
            if (cb) cb(false);
        }
    };

    window.__WINGO_EXECUTE_TRADE = (forcedPred) => {
        if (!st.isRun || st.isTrd) return;
        executeCycleTradeWorkflow(forcedPred);
    };

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    st.dynSeq = calcSeq(initialBal > 0 ? initialBal : 100, st.steps);
    st.stpIdx = 0;

    let isFetchingApi = false;

    const executeCycleTradeWorkflow = async (overridePred = null) => {
        if (isFetchingApi || st.isTrd) return;

        let incomingPeriod = getLiveRoundId();
        if (st.lastBetPeriod === incomingPeriod) return;

        refreshWallet();
        let liveB = chkBal();
        if (liveB > 0 && st.startBal <= 0) {
            st.startBal = liveB;
            st.dynSeq = calcSeq(liveB, st.steps);
        }

        isFetchingApi = true;

        try {
            let fetchUrl = predictionApiUrl + (predictionApiUrl.includes('?') ? '&' : '?') + "t=" + Date.now();
            let rawJson = null;
            if (!overridePred) {
                try {
                    let res = await fetch(fetchUrl);
                    if (res.ok) rawJson = await res.json();
                } catch(fetchErr) {}
            } else {
                rawJson = { top_engine: { prediction: overridePred, win_rate: '85%' } };
            }

            if (!rawJson) {
                rawJson = { top_engine: { prediction: 'BIG', win_rate: '50%' } };
            }

            let histArray = rawJson.history_preview || rawJson.history || (rawJson.data && rawJson.data.history) || [];

            // =================================================================
            // ACCURATE MULTI-LAYER WIN / LOSS EVALUATION
            // =================================================================
            if (st.lastBetPeriod && st.lastBetAmt > 0 && st.evaluatedPeriod !== st.lastBetPeriod) {
                st.evaluatedPeriod = st.lastBetPeriod;
                let won = false;
                let resolved = false;

                // 1. Direct DOM check from Game History
                let domOutcome = getActualPeriodOutcomeFromDom(st.lastBetPeriod);
                if (domOutcome) {
                    won = (st.lastPred === domOutcome);
                    resolved = true;
                }

                // 2. Backup check from API history
                if (!resolved && histArray.length > 0) {
                    let item = histArray.find(h => String(h.period || h.pid).trim() === String(st.lastBetPeriod).trim());
                    if (item) {
                        let actualSize = '';
                        if (item.size) actualSize = String(item.size).toUpperCase().trim();
                        else if (item.actual_size) actualSize = String(item.actual_size).toUpperCase().trim();
                        else if (typeof item.actual === 'number') actualSize = item.actual >= 5 ? 'BIG' : 'SMALL';

                        if (actualSize) {
                            won = (st.lastPred === actualSize);
                            resolved = true;
                        } else if (item.status) {
                            won = (String(item.status).toUpperCase() === 'WIN');
                            resolved = true;
                        }
                    }
                }

                // 3. Backup: Balance increase detection
                if (!resolved) {
                    let preBal = parseFloat(sessionStorage.getItem('drx_pre_bet_bal') || '0');
                    if (preBal > 0 && liveB > preBal) {
                        won = true;
                        resolved = true;
                    }
                }

                if (resolved) {
                    if (won) {
                        st.w++;
                        st.cur_w_streak++;
                        st.cur_l_streak = 0;
                        if (st.cur_w_streak > st.max_w_streak) st.max_w_streak = st.cur_w_streak;
                        st.stpIdx = 0;
                        // On Win: re-calculate steps with new enlarged balance
                        st.dynSeq = calcSeq(liveB > 0 ? liveB : st.curBal, st.steps);
                    } else {
                        st.l++;
                        st.cur_l_streak++;
                        st.cur_w_streak = 0;
                        if (st.cur_l_streak > st.max_l_streak) st.max_l_streak = st.cur_l_streak;

                        // 24/7 Mode: If max steps reached, reset smoothly to Step 1
                        if (st.stpIdx >= st.steps - 1) {
                            st.stpIdx = 0;
                            st.dynSeq = calcSeq(liveB > 0 ? liveB : st.curBal, st.steps);
                        } else {
                            st.stpIdx = st.stpIdx + 1;
                        }
                    }
                }
            }

            // Milestone Goal Check: Do not shut down; rollover profit & keep running 24/7
            if (st.tgtAmt > 0 && liveB >= st.tgtAmt && st.startBal > 0) {
                st.startBal = liveB;
                st.stpIdx = 0;
                st.dynSeq = calcSeq(liveB, st.steps);
                let diff = st.tgtAmt - st.startBal;
                st.tgtAmt = liveB + (diff > 0 ? diff : 100);
            }

            let outcome = resolvePredictionFromServers(rawJson);
            let incomingPred = overridePred || outcome.pred || 'BIG';

            let sEl = document.getElementById('hud-signal');
            let rEl = document.getElementById('hud-rate');
            if (sEl) sEl.innerText = "SIGNAL: " + incomingPred;
            if (rEl) rEl.innerText = "WIN RATE: " + outcome.rate + "%";

            let betAmt = Math.floor(st.dynSeq[st.stpIdx]) || 1;

            st.isTrd = true;
            st.lastPred = incomingPred;
            st.lastBetPeriod = incomingPeriod;
            st.lastBetAmt = betAmt;
            sessionStorage.setItem('drx_pre_bet_bal', String(liveB));

            exeTrdFast(incomingPred, betAmt, (success) => {
                if (success) st.tradesDone++;
                st.isTrd = false;
            });

        } catch(err) {
            st.isTrd = false;
        }
        isFetchingApi = false;
    };

    const timerTick = () => {
        if (!st.isRun) return;
        const rem = updateTimer();
        const currentCycle = Math.floor(Date.now() / 30000);

        // Optimal execution window: Between 24s and 8s remaining
        // Allows previous round outcome & balance to settle 100%
        if (st.lastTriggeredCycle !== currentCycle && rem <= 24 && rem >= 8) {
            st.lastTriggeredCycle = currentCycle;
            executeCycleTradeWorkflow();
        }
    };

    updateTimer();
    st.timerInt = setInterval(timerTick, 1000);
    return "DRX_24_7_ENGINE_INITIALIZED";
})();
"""

# ==============================================================================
# PYTHON PARALLEL PREDICTION FETCH (ZERO-SKIP BACKEND)
# ==============================================================================
def python_fetch_best_prediction():
    try:
        req = urllib.request.Request(
            f"{PREDICTION_API_URL}?t={int(time.time()*1000)}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as res:
            data = json.loads(res.read().decode("utf-8"))

        servers = data.get("servers", [])
        if not servers:
            return data.get("top_engine", {}).get("prediction", "BIG").upper()

        parsed = []
        for s in servers:
            r_str = "".join([c for c in str(s.get("win_rate", "0")) if c.isdigit() or c == '.'])
            rate = float(r_str) if r_str else 0.0
            p = str(s.get("prediction", "")).upper().strip()
            norm = "SMALL" if "SMALL" in p else ("BIG" if "BIG" in p else "")
            if norm:
                parsed.append({"rate": rate, "pred": norm})

        if not parsed:
            return "BIG"

        max_rate = max(x["rate"] for x in parsed)
        top = [x for x in parsed if abs(x["rate"] - max_rate) < 0.01]
        bigs = sum(1 for x in top if x["pred"] == "BIG")
        smalls = sum(1 for x in top if x["pred"] == "SMALL")

        if len(top) == 1:
            return top[0]["pred"]
        return "BIG" if bigs >= smalls else "SMALL"
    except Exception:
        return "BIG"

# ==============================================================================
# WORKER EXECUTION FLOWS
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
    try:
        driver, handle = allocate_session_tab(sid, login_url)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    except Exception as e:
        logger.error(f"Allocation error for {sid}: {e}")
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid, "chat_id": chat_id, "site_name": site_name, "reason": str(e)
        })
        terminate_session_cleanly(sid)
        return

    fill_ok = False
    for _ in range(70):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(1.5)
            break
        time.sleep(0.4)

    if not fill_ok:
        terminate_session_cleanly(sid)
        return

    login_status = "PENDING"
    for _ in range(40):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict) and res.get("status") == "SUCCESS":
            login_status = "SUCCESS"
            break
        time.sleep(0.4)

    if safe_tab_execute(sid, lambda drv: drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")):
        login_status = "SUCCESS"

    if login_status != "SUCCESS":
        terminate_session_cleanly(sid)
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
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

    for _ in range(15):
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
        safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_PERSISTENT_NAV_JS, wingo_url))
        time.sleep(1.5)
        if safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS)):
            break

    current_bal = 0.0
    for _ in range(15):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.4)

    sess["current_balance"] = current_bal
    sess["cur_bal"] = current_bal

    emit_event_to_manager("WINGO_READY", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "live_balance": current_bal
    })

def worker_monitor_trading_loop(chat_id, sid, site_name):
    last_py_cycle = None
    loop_tick = 0

    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        loop_tick += 1

        # Check logout condition every 6 seconds
        if loop_tick % 2 == 0:
            def _check_logout(drv):
                return drv.execute_script("""
                    const hash = window.location.hash || '';
                    const href = window.location.href || '';
                    if (hash.includes('login') || href.includes('/login')) return "LOGGED_OUT_URL";
                    const bodyText = document.body ? document.body.innerText : '';
                    if (bodyText.includes('Token has expired') || bodyText.includes('please login again')) return "LOGGED_OUT_MSG";
                    return null;
                """)

            logout_reason = safe_tab_execute(sid, _check_logout)
            if logout_reason:
                logger.warning(f"Session {sid} logged out! Slot freeing...")
                emit_event_to_manager("ACCOUNT_LOGGED_OUT", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "reason": logout_reason,
                    "message": "⚠️️ অ্যাকাউন্ট অন্য ডিভাইসে লগইন হওয়ার কারণে সেশন সমাপ্ত করা হলো।"
                })
                terminate_session_cleanly(sid)
                break

        # Continuous Fallback execution (Triggered within the safe 24s-8s window)
        now_sec = time.localtime().tm_sec
        rem_sec = 30 - (now_sec % 30)
        cur_cycle = int(time.time() // 30)

        if 8 <= rem_sec <= 24 and last_py_cycle != cur_cycle:
            last_py_cycle = cur_cycle
            best_pred = python_fetch_best_prediction()
            safe_tab_execute(sid, lambda drv: drv.execute_script(f"""
                if (window.__WINGO_EXECUTE_TRADE && window.__WINGO_ST && !window.__WINGO_ST.isTrd) {{
                    window.__WINGO_EXECUTE_TRADE('{best_pred}');
                }}
            """))

        def _get_st(drv):
            return drv.execute_script("""
                if (window.__WINGO_ST) {
                    return {
                        isRun: window.__WINGO_ST.isRun,
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
            is_run = js_data.get("isRun", True)
            step_idx = js_data.get("step", 1)
            tot_steps = js_data.get("steps", sess.get("total_steps", 5))

            task_payload = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "RUNNING",
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

            if not is_run:
                sess["is_trading"] = False
                break

        # Periodic Garbage Collection (0.5GB Low-RAM Protection)
        if loop_tick % 10 == 0:
            gc.collect()

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
                    logger.warning(f"Emergency stop: {kind}. Terminating worker sessions!")
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

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    safe_tab_execute(sid, lambda drv: drv.execute_script("""
                        if(window.__WINGO_ST){ 
                            window.__WINGO_ST.isRun = false; 
                            if(window.__WINGO_ST.timerInt) clearInterval(window.__WINGO_ST.timerInt);
                        }
                    """))
                    active_sessions[sid]["is_trading"] = False

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick: {e}")
        time.sleep(1.0)

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
    logger.info(f"Shutdown signal caught on {WORKER_ALIAS}. Commencing clean teardown...")
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
