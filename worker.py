#!/usr/bin/env python3
# ==============================================================================
# DRX WINGO CLUSTER - EXECUTION WORKER NODE (ওয়ার্কার কোড)
# ==============================================================================
# Responsibilities:
# - Connects to Firebase RTDB and registers as an active worker terminal
# - Handles browser sessions (Headless Firefox, GeckoDriver, Container isolation)
# - Performs auto-login across 6 platforms, resolves Error 22 auto-takeover
# - Dismisses modals & USDT bonus announcements continuously
# - Executes 24/7 invisible ghost Step Maker trading engine (WinGo 30S)
# - Robust 24/7 execution: never shrinks steps on losses, no decimals/fractions
# - Monochrome aesthetic: ֎ ✧ ⏣ 𖤓 ﴾ ﴿ ⪼ ⟡ ▸ ▰▰▰▱ ⬩➤ ❯❯❯❯ ✦︎
# - Mathematical bold numbers: 𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗 & subscripts: ₀₁₂₃₄₅₆₇₈₉
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

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [WORKER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WORKER_NODE")

def install_and_import(package_name, import_name=None):
    if import_name is None:
        import_name = package_name
    try:
        __import__(import_name)
    except ImportError:
        logger.warning(f"Installing missing package: {package_name}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--upgrade", "--no-cache-dir", package_name
            ])
            logger.info(f"Successfully installed: {package_name}")
        except Exception as e:
            logger.error(f"Pip installation failed for {package_name}: {e}")

install_and_import("selenium")
install_and_import("psutil")

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil

# ==============================================================================
# WORKER CONFIGURATION & CLUSTER REGISTRY
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://medieval-pink-yqnjxslo-dp376cefm0gv.edgeone.dev/apipid.json")
HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() == "true"
NODE_ID = f"worker_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"

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
# MATHEMATICAL BOLD UNICODE & FORMATTERS
# ==============================================================================
BOLD_DIGITS = {
    '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
    '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗'
}

SUB_DIGITS = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
}

def to_bold_num(val) -> str:
    s = str(val)
    return "".join(BOLD_DIGITS.get(c, c) for c in s)

def to_sub_num(val) -> str:
    s = str(val)
    return "".join(SUB_DIGITS.get(c, c) for c in s)

def to_bold(text: str) -> str:
    res = []
    for c in str(text):
        n = ord(c)
        if 65 <= n <= 90:
            res.append(chr(n + 119743))
        elif 97 <= n <= 122:
            res.append(chr(n + 119737))
        elif 48 <= n <= 57:
            res.append(BOLD_DIGITS.get(c, c))
        else:
            res.append(c)
    return "".join(res)

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
# AGGRESSIVE ZOMBIE PROCESS & MEMORY HYGIENE
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
        gone, still_alive = psutil.wait_procs(children, timeout=2.0)
        for p in still_alive:
            try:
                p.kill()
            except Exception:
                pass
        parent.terminate()
        parent.wait(timeout=2.0)
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

# ==============================================================================
# HARDENED BROWSER SESSION ISOLATION (ZERO CRASH & LOW RAM)
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

    # Ultra-low 0.5 GB (512 MB) RAM profile
    options.set_preference("permissions.default.image", 2)  # Disables image downloads (saves 150-200MB RAM)
    options.set_preference("permissions.default.stylesheet", 1)
    options.set_preference("browser.display.use_document_fonts", 0)  # Disables web font downloads
    options.set_preference("media.autoplay.default", 5)  # Disables audio/video autoplay
    options.set_preference("media.volume_scale", "0.0")
    options.set_preference("dom.ipc.processCount", 1)  # Strictly single content process (saves 100MB+ RAM)
    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 512)
    options.set_preference("javascript.options.mem.max", 24576)  # Limit JS heap to 24MB
    options.set_preference("javascript.options.mem.high_water_mark", 18)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("browser.cache.memory.capacity", 8192)  # 8MB memory cache
    options.set_preference("network.http.use-cache", False)
    options.set_preference("network.prefetch-next", False)
    options.set_preference("webgl.disabled", True)
    options.set_preference("accessibility.force_disabled", 1)
    options.set_preference("toolkit.telemetry.enabled", False)
    options.set_preference("dom.disable_open_during_load", True)
    options.set_preference("dom.popup_maximum", 0)
    options.set_preference("media.peerconnection.enabled", False)
    options.set_preference("media.navigator.enabled", False)
    options.set_preference("layout.frame_rate", 10)  # Limits headless render loop to 10 FPS (cuts CPU load)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(35)
    driver.set_script_timeout(20)
    driver.implicitly_wait(3)
    driver.set_window_size(412, 915)

    try:
        driver.get(target_url)
    except Exception as e:
        logger.warning(f"Initial get timeout/warning for {target_url}: {e}")

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

    acquired = lock.acquire(timeout=6.0)
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
        logger.warning(f"Tab execution tick exceeded {timeout}s on sid: {sid}, continuing...")
        return None

    gc.collect()

    if result_container["error"]:
        err_msg = str(result_container["error"])
        if "unexpectedly closed" in err_msg or "Tried to run command without establishing a connection" in err_msg:
            logger.error(f"Driver severed connection: {err_msg}")
        return None

    return result_container["res"]

def close_session_tab(session_id):
    sess = active_sessions.pop(session_id, None)
    if sess:
        sess["is_trading"] = False
        driver = sess.get("driver")
        if driver:
            try:
                driver.execute_script("if(window.__WINGO_ST && window.__WINGO_ST.autoInt) clearInterval(window.__WINGO_ST.autoInt);")
            except Exception:
                pass
            try:
                driver.quit()
            except Exception:
                pass
            try:
                if hasattr(driver, 'service') and driver.service and driver.service.process:
                    kill_process_tree(driver.service.process.pid)
            except Exception:
                pass

        profile_dir = os.path.join(PROFILES_BASE_DIR, f"profile_{session_id}")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)

    cleanup_zombie_browsers()
    gc.collect()

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
    }, 500);
}, 500);

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
return 0;
"""

# ==============================================================================
# INTEGRATED 24/7 INVISIBLE GHOST STEP MAKER TRADING ENGINE
# ==============================================================================
WINGO_DOM_HELPERS_JS = r"""
(function(){
    window.__GET_WINGO_STATE = function() {
        let bal = 0;
        try {
            let targeted = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
            for (let i = 0; i < targeted.length; i++) {
                let txt = targeted[i].innerText || '';
                let match = txt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                if (match) {
                    let n = Math.floor(parseFloat(match[1].replace(/,/g, '')));
                    if (n > 0) { bal = n; break; }
                }
            }
            if (!bal) {
                let els = document.querySelectorAll('span, div, p');
                for (let i = 0; i < els.length; i++) {
                    let txt = els[i].innerText || '';
                    if (txt.includes('Wallet balance') || txt.includes('Balance')) {
                        let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
                        let match = parentTxt.match(/[৳₹$€£]\s*([\d,]+\.?\d*)/);
                        if (match) { bal = Math.floor(parseFloat(match[1].replace(/,/g, ''))); break; }
                    }
                }
            }
        } catch(e) {}

        let remSec = 30;
        try {
            let timeEl = document.querySelector('.time-box, [class*="time" i], .Time, .countdown, [class*="countdown" i]');
            if (timeEl) {
                let txt = timeEl.innerText || '';
                let m = txt.match(/(\d+)\s*:\s*(\d+)/);
                if (m) remSec = (parseInt(m[1]) * 60) + parseInt(m[2]);
                else {
                    let digits = txt.replace(/\D/g, '');
                    if (digits.length >= 1) remSec = parseInt(digits);
                }
            }
        } catch(e) {}

        return { bal: bal, remSec: remSec };
    };

    window.__EXECUTE_WINGO_BET = function(pred, amt) {
        try {
            let targetText = String(pred).toUpperCase().trim();
            let btn = null;

            if (targetText === 'BIG') {
                btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button.big, [class*="big" i]');
            } else if (targetText === 'SMALL') {
                btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button.small, [class*="small" i]');
            }

            if (!btn || !btn.offsetParent) {
                let btns = document.querySelectorAll('button, div[role="button"], div, span');
                for (let b of btns) {
                    let t = (b.innerText || '').trim().toUpperCase();
                    if ((t === targetText || t.startsWith(targetText + ' ') || t.endsWith(' ' + targetText)) && b.offsetParent && b.offsetWidth > 15) {
                        btn = b;
                        break;
                    }
                }
            }

            if (!btn) {
                return { success: false, reason: "BTN_NOT_FOUND_" + targetText };
            }

            ['pointerdown', 'mousedown', 'pointerup', 'mouseup', 'click'].forEach(evt => {
                btn.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window }));
            });
            if (typeof btn.click === 'function') btn.click();

            return { success: true, reason: "CLICKED_" + targetText };
        } catch(e) {
            return { success: false, reason: e.toString() };
        }
    };

    window.__CONFIRM_WINGO_BET = function(amt) {
        try {
            // 1. Force base unit "1" to eliminate any 10x, 20x multiplier bug
            let unitButtons = document.querySelectorAll('.Betting__C-foot-c button, .Betting__C-foot-c div, .van-button, div[class*="balance" i] button, div[class*="unit" i] span, button');
            for (let ub of unitButtons) {
                let uTxt = (ub.innerText || '').trim();
                if (uTxt === '1' && ub.offsetParent && ub.offsetWidth > 10) {
                    ub.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    if (typeof ub.click === 'function') ub.click();
                    break;
                }
            }

            // 2. Set input amount
            let inpEl = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input, input[inputmode='numeric']");
            if (inpEl) {
                inpEl.focus();
                let setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                if (setV) setV.call(inpEl, String(amt));
                else inpEl.value = String(amt);
                inpEl.dispatchEvent(new Event('input', { bubbles: true }));
                inpEl.dispatchEvent(new Event('change', { bubbles: true }));
                inpEl.dispatchEvent(new Event('blur', { bubbles: true }));
            }

            // 3. Confirm button
            let confBtn = document.querySelector('button.bet-amount, button[class*="bet-amount"], .Betting__C-foot-total, .van-button--danger, .van-button--warning, .van-button--primary');
            if (!confBtn) {
                let docButtons = document.querySelectorAll('button, div[role="button"]');
                for (let b of docButtons) {
                    let txt = (b.innerText || '').toLowerCase();
                    if ((txt.includes('total amount') || txt.includes('total') || txt.includes('confirm') || txt.includes('bet')) && b.offsetParent && b.offsetWidth > 20) {
                        confBtn = b;
                        break;
                    }
                }
            }

            if (confBtn) {
                confBtn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                if (typeof confBtn.click === 'function') confBtn.click();
                return { success: true, reason: "CONFIRMED_AMOUNT_" + amt };
            }

            return { success: false, reason: "CONFIRM_BTN_NOT_FOUND" };
        } catch(e) {
            return { success: false, reason: e.toString() };
        }
    };

    return "HELPERS_INSTALLED";
})();
"""

def compute_step_maker(bal: float, steps_count: int) -> list:
    """Computes exact doubling martingale sequence strictly in floor integers.
    Formula: first_step = max(1, bal // (2^n - 1))
    sequence = [first_step * 2^i for i in range(n)]
    e.g. 100 BDT / 5 steps -> [3, 6, 12, 24, 48]
    e.g. 70 BDT / 5 steps -> [2, 4, 8, 16, 32]
    e.g. 200 BDT / 5 steps -> [6, 12, 24, 48, 96]
    """
    b = max(1, int(bal))
    n = max(1, int(steps_count))
    sum_powers = (2 ** n) - 1
    first_step = max(1, b // sum_powers)
    return [first_step * (2 ** i) for i in range(n)]

def fetch_prediction_api(pred_url: str):
    """Direct Python HTTP fetch - bypasses all browser CORS & CSP blocks cleanly."""
    try:
        ts = int(time.time())
        sep = "&" if "?" in pred_url else "?"
        url = f"{pred_url}{sep}page=1&ts={ts}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            data = resp.read()
            raw = json.loads(data.decode("utf-8"))
            if not raw:
                return None
            next_obj = raw.get("next") or (raw.get("data", {}).get("next") if isinstance(raw.get("data"), dict) else None)
            hist = raw.get("history") or (raw.get("data", {}).get("history") if isinstance(raw.get("data"), dict) else [])
            if not next_obj and isinstance(raw, list) and len(raw) > 0:
                first = raw[0]
                next_obj = first.get("next") or {"period": "", "size": first.get("size") or first.get("pred") or "BIG"}
                hist = first.get("history") or []
            return {"next": next_obj, "history": hist}
    except Exception as e:
        logger.debug(f"Prediction fetch error: {e}")
        return None

# ==============================================================================
# WORKER EXECUTION FLOWS
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
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
        return

    fill_ok = False
    for _ in range(70):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            fill_ok = True
            time.sleep(2.0)
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
        close_session_tab(sid)
        return

    login_status = "PENDING"
    err_detail = ""
    for _ in range(40):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "CONFIRM_CLICKED":
                time.sleep(1.5)
                continue
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "Invalid credentials")
                break
        time.sleep(0.5)

    if safe_tab_execute(sid, lambda drv: drv.execute_script("return !!(localStorage.getItem('token') || sessionStorage.getItem('token'));")):
        login_status = "SUCCESS"

    if login_status == "ERROR":
        close_session_tab(sid)
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": err_detail,
            "anim_msg_id": anim_msg_id
        })
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    time.sleep(1.0)

    emit_event_to_manager("LOGIN_SUCCESS", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "phone": phone,
        "anim_msg_id": anim_msg_id
    })

def execute_worker_prepare_wingo(chat_id, sid, wingo_url, site_name):
    sess = active_sessions.get(sid)
    if not sess:
        return

    # Direct native navigation to WinGo 30S SaasLottery URL immediately (fast 2s execution)
    try:
        safe_tab_execute(sid, lambda drv: drv.get(wingo_url), timeout=15.0)
    except Exception as e:
        logger.warning(f"Direct nav exception for {wingo_url}: {e}")

    time.sleep(1.5)
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS), timeout=4.0)

    # Fast balance check
    current_bal = 0.0
    for _ in range(8):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS), timeout=3.0)
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.4)

    sess["current_balance"] = current_bal
    sess["cur_bal"] = current_bal
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS), timeout=3.0)

    emit_event_to_manager("WINGO_READY", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "live_balance": current_bal
    })

def worker_monitor_trading_loop(chat_id, sid, site_name, target_profit, total_steps, pred_url):
    """24/7 Python-driven trading loop. Direct HTTP prediction fetch (zero CORS issues).
    Implements exact doubling Step Maker martingale with zero fractional points."""
    sess = active_sessions.get(sid)
    if not sess:
        return

    logger.info(f"[*] [AUTO TRADE ACTIVE] Node: {NODE_ID} | Session: {sid} | Site: {site_name}")

    # Inject DOM helpers into browser page
    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_DOM_HELPERS_JS), timeout=6.0)

    # Initial Balance Read
    init_data = safe_tab_execute(sid, lambda drv: drv.execute_script("return window.__GET_WINGO_STATE ? window.__GET_WINGO_STATE() : null;"), timeout=5.0) or {}
    init_bal = float(init_data.get("bal") or sess.get("current_balance") or 100.0)
    if init_bal <= 0:
        init_bal = 100.0

    sess["start_bal"] = init_bal
    sess["base_bal"] = init_bal
    sess["cur_bal"] = init_bal
    sess["target_total"] = (init_bal + target_profit) if target_profit > 0 else 0.0

    step_sequence = compute_step_maker(init_bal, total_steps)
    step_idx = 0
    last_bet_period = None
    last_bet_pred = None
    last_bet_amt = 0
    last_processed_pid = None
    wins = 0
    losses = 0
    trades_done = 0
    cur_w_streak = 0
    cur_l_streak = 0
    max_w_streak = 0
    max_l_streak = 0
    last_telemetry_ts = 0

    sess["wins"] = wins
    sess["losses"] = losses
    sess["step"] = step_idx + 1

    logger.info(f"[*] Base Bal: {init_bal} ৳ | Step Maker Sequence ({total_steps} steps): {step_sequence} | Target Goal: {sess['target_total']} ৳")

    while sess.get("is_trading") and WORKER_ACTIVE:
        try:
            # 1. Read live browser state (balance & countdown)
            st_data = safe_tab_execute(sid, lambda drv: drv.execute_script("return window.__GET_WINGO_STATE ? window.__GET_WINGO_STATE() : null;"), timeout=4.0) or {}
            live_b = float(st_data.get("bal") or 0.0)
            rem_sec = int(st_data.get("remSec", 30))
            if live_b > 0:
                sess["cur_bal"] = live_b
                sess["current_balance"] = live_b

            # 2. Check if Target Profit is Reached
            if sess["target_total"] > 0 and sess["cur_bal"] >= sess["target_total"] and sess["cur_bal"] > sess["start_bal"]:
                logger.info(f"[!] Target Profit Fulfilled! Current Balance: {sess['cur_bal']} >= Target: {sess['target_total']}")
                sess["is_trading"] = False
                emit_event_to_manager("TARGET_ACHIEVED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": sess["start_bal"],
                    "final_balance": sess["cur_bal"],
                    "wins": wins,
                    "losses": losses
                })
                break

            # 3. Direct HTTP Prediction Signal (Zero CORS, 100% Reliable)
            pred_data = fetch_prediction_api(pred_url)
            if pred_data:
                next_info = pred_data.get("next") or {}
                hist_list = pred_data.get("history") or []

                # A. Evaluate outcome of previously placed bet
                if last_bet_period:
                    finished = None
                    for h in hist_list:
                        if str(h.get("period") or h.get("pid")) == str(last_bet_period):
                            finished = h
                            break
                    if not finished and hist_list:
                        first_pid = str(hist_list[0].get("period") or hist_list[0].get("pid"))
                        if first_pid == str(last_bet_period):
                            finished = hist_list[0]

                    if finished:
                        won = False
                        act_sz = str(finished.get("actual_size") or finished.get("actual") or "").upper().strip()
                        if act_sz in ["0", "1", "2", "3", "4"]: act_sz = "SMALL"
                        elif act_sz in ["5", "6", "7", "8", "9"]: act_sz = "BIG"

                        st_str = str(finished.get("status") or "").upper()
                        if st_str == "WIN" and finished.get("pred") and str(finished.get("pred")).upper() == last_bet_pred:
                            won = True
                        elif st_str == "LOSS" and finished.get("pred") and str(finished.get("pred")).upper() == last_bet_pred:
                            won = False
                        else:
                            won = (last_bet_pred == act_sz)

                        if won:
                            wins += 1
                            cur_w_streak += 1
                            cur_l_streak = 0
                            if cur_w_streak > max_w_streak: max_w_streak = cur_w_streak
                            step_idx = 0  # WIN: Reset to Step 1
                            logger.info(f"[*] [ROUND WON] Period: {last_bet_period} | Bet: {last_bet_pred} ({last_bet_amt} ৳) | Reset Step 1")
                            if sess["cur_bal"] > sess["base_bal"]:
                                sess["base_bal"] = sess["cur_bal"]
                                step_sequence = compute_step_maker(sess["base_bal"], total_steps)
                                logger.info(f"[*] Balance Grew! Updated Sequence: {step_sequence}")
                        else:
                            losses += 1
                            cur_l_streak += 1
                            cur_w_streak = 0
                            if cur_l_streak > max_l_streak: max_l_streak = cur_l_streak
                            step_idx = min(step_idx + 1, len(step_sequence) - 1)  # LOSS: Advance Step
                            logger.info(f"[*] [ROUND LOST] Period: {last_bet_period} | Bet: {last_bet_pred} ({last_bet_amt} ৳) | Next: Step {step_idx + 1} ({step_sequence[step_idx]} ৳)")

                        last_bet_period = None
                        last_bet_pred = None
                        sess["wins"] = wins
                        sess["losses"] = losses
                        sess["step"] = step_idx + 1

                # B. Place Bet for Upcoming Period
                curr_pid = str(next_info.get("period") or "").strip()
                curr_sz = str(next_info.get("size") or next_info.get("pred") or "BIG").upper().strip()

                if curr_pid and curr_pid != last_processed_pid and rem_sec > 6:
                    if curr_sz in ["BIG", "SMALL", "GREEN", "RED", "VIOLET"]:
                        bet_amt = step_sequence[step_idx]
                        logger.info(f"[*] [AUTO BET] Period: {curr_pid} | Size: {curr_sz} | Amount: {bet_amt} ৳ | Step: {step_idx + 1} of {len(step_sequence)}")

                        # 1. Click selection (BIG/SMALL)
                        safe_tab_execute(sid, lambda drv: drv.execute_script("return window.__EXECUTE_WINGO_BET(arguments[0], arguments[1]);", curr_sz, bet_amt), timeout=3.5)
                        time.sleep(0.4)
                        # 2. Confirm amount
                        safe_tab_execute(sid, lambda drv: drv.execute_script("return window.__CONFIRM_WINGO_BET(arguments[0]);", bet_amt), timeout=3.5)
                        time.sleep(0.5)

                        last_processed_pid = curr_pid
                        last_bet_period = curr_pid
                        last_bet_pred = curr_sz
                        last_bet_amt = bet_amt
                        trades_done += 1
                        sess["tradesDone"] = trades_done

            # 4. Periodic Live Telemetry (every 3 seconds)
            now_ts = time.time()
            if now_ts - last_telemetry_ts >= 3.0:
                last_telemetry_ts = now_ts
                sess["step"] = step_idx + 1
                sess["cur_w_streak"] = cur_w_streak
                sess["cur_l_streak"] = cur_l_streak
                sess["max_w_streak"] = max_w_streak
                sess["max_l_streak"] = max_l_streak
                emit_event_to_manager("LIVE_TELEMETRY", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "current_balance": sess["cur_bal"],
                    "target_total": sess["target_total"],
                    "wins": wins,
                    "losses": losses,
                    "step": step_idx + 1
                })

            time.sleep(1.2)
        except Exception as e:
            logger.error(f"Trading loop error on {sid}: {e}")
            time.sleep(2.0)

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

                if kind == "PREPARE_WINGO" and sid in active_sessions:
                    sess = active_sessions[sid]
                    threading.Thread(
                        target=execute_worker_prepare_wingo,
                        args=(chat_id, sid, sess["wingo_url"], sess["site_name"]),
                        daemon=True
                    ).start()

                elif kind == "START_TRADING" and sid in active_sessions:
                    sess = active_sessions[sid]
                    target_profit = float(action_pkt.get("target_profit", 0))
                    total_steps = int(action_pkt.get("total_steps", 5))
                    pred_url = action_pkt.get("prediction_api_url") or PREDICTION_API_URL
                    sess["is_trading"] = True
                    sess["target_profit"] = target_profit
                    sess["total_steps"] = total_steps

                    # Start 24/7 Python auto-trade engine
                    threading.Thread(
                        target=worker_monitor_trading_loop,
                        args=(chat_id, sid, sess["site_name"], target_profit, total_steps, pred_url),
                        daemon=True
                    ).start()

                elif kind == "REQUEST_TELEMETRY" and sid in active_sessions:
                    sess = active_sessions[sid]
                    emit_event_to_manager("LIVE_TELEMETRY", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "site_name": sess.get("site_name", ""),
                        "current_balance": sess.get("cur_bal", 0.0),
                        "target_total": sess.get("target_total", 0.0),
                        "wins": sess.get("wins", 0),
                        "losses": sess.get("losses", 0),
                        "step": sess.get("step", 1)
                    })

                elif kind == "REQUEST_BALANCE" and sid in active_sessions:
                    sess = active_sessions[sid]
                    cur_b = sess.get("cur_bal", 0.0)
                    if cur_b <= 0:
                        bal_val = safe_tab_execute(sid, lambda drv: drv.execute_script("return (window.__GET_WINGO_STATE ? window.__GET_WINGO_STATE().bal : 0);"))
                        if bal_val and float(bal_val) > 0:
                            sess["cur_bal"] = float(bal_val)
                            sess["current_balance"] = float(bal_val)
                    emit_event_to_manager("BALANCE_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "call_id": action_pkt.get("call_id"),
                        "live_balance": sess.get("cur_bal", 0.0)
                    })

                elif kind == "REQUEST_STATS" and sid in active_sessions:
                    sess = active_sessions[sid]
                    emit_event_to_manager("STATS_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "data": {
                            "curBal": sess.get("cur_bal", 0.0),
                            "tgtAmt": sess.get("target_total", 0.0),
                            "step": sess.get("step", 1),
                            "steps": sess.get("total_steps", 5),
                            "w": sess.get("wins", 0),
                            "l": sess.get("losses", 0),
                            "tradesDone": sess.get("tradesDone", 0),
                            "cur_w_streak": sess.get("cur_w_streak", 0),
                            "cur_l_streak": sess.get("cur_l_streak", 0),
                            "max_w_streak": sess.get("max_w_streak", 0),
                            "max_l_streak": sess.get("max_l_streak", 0)
                        }
                    })

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    active_sessions[sid]["is_trading"] = False
                    logger.info(f"Trading stopped cleanly for session: {sid}")

                elif kind == "CANCEL_PREPARE" and sid in active_sessions:
                    logger.info(f"Market preparation cancelled by user for session: {sid}")

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    close_session_tab(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick: {e}")
        time.sleep(1.0)

# ==============================================================================
# HEARTBEAT & CLUSTER REGISTRATION LOOP
# ==============================================================================
def worker_register_node():
    node_payload = {
        "status": "FREE",
        "heartbeat": time.time(),
        "assigned_user_id": None,
        "session_id": None,
        "task": None,
        "node_id": NODE_ID,
        "load": len(active_sessions),
        "latency_ms": measure_network_latency(PLATFORMS["site_amarclub"]["login"]),
        "registered_at": time.time()
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)
    logger.info(f"Node registered in cluster as: {NODE_ID}")

def worker_heartbeat_loop():
    while WORKER_ACTIVE:
        try:
            status_val = "BUSY" if any(s.get("is_trading") for s in active_sessions.values()) else "FREE"
            lat = measure_network_latency(PLATFORMS["site_amarclub"]["login"])
            hb_data = {
                "heartbeat": time.time(),
                "status": status_val,
                "load": len(active_sessions),
                "latency_ms": lat
            }
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", hb_data)
        except Exception:
            pass
        time.sleep(4.0)

def continuous_24h_watchdog():
    while WORKER_ACTIVE:
        try:
            now = time.time()
            for sid, item in list(active_sessions.items()):
                created_at = item.get("created_at", now)
                last_act = item.get("last_activity", now)
                if now - created_at >= 86400 or (now - last_act > 900 and not item.get("is_trading")):
                    close_session_tab(sid)
        except Exception:
            pass
        time.sleep(600)

# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print(f"[*] {to_bold('DRX WINGO CLUSTER WORKER ACTIVE')} [{NODE_ID}]...")
    worker_register_node()
    threading.Thread(target=worker_heartbeat_loop, daemon=True).start()
    threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

    try:
        worker_task_listener()
    except KeyboardInterrupt:
        print("\nStopping worker gracefully...")
        WORKER_ACTIVE = False
        firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {"status": "OFFLINE", "heartbeat": 0})
        for s in list(active_sessions.keys()):
            close_session_tab(s)
