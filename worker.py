
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
                logger.error(f"Failed installing dependency {pkg_name}: {e}")

ensure_dependencies()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.by import By
import psutil

# VIP Unicode Typography Maps
VIP_ALPHA_MAP = {c: v for c, v in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")}
VIP_LOWER_MAP = {c: v for c, v in zip("abcdefghijklmnopqrstuvwxyz", "𝐚𝐛𝐜𝐝𝐞𝐟𝐠𝐡𝐢𝐣𝐤𝐥𝐦𝐧𝐨𝐩𝐪𝐫𝐬𝐭𝐮𝐯𝐰𝐱𝐲𝐳")}
BOLD_DIGIT_MAP = {d: v for d, v in zip("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")}
SUBSCRIPT_DIGIT_MAP = {d: v for d, v in zip("0123456789", "₀₁₂₃₄₅₆₇₈₉")}

def to_vip_text(text: str) -> str:
    res = []
    for c in str(text):
        if c in VIP_ALPHA_MAP:
            res.append(VIP_ALPHA_MAP[c])
        elif c in VIP_LOWER_MAP:
            res.append(VIP_LOWER_MAP[c])
        elif c in BOLD_DIGIT_MAP:
            res.append(BOLD_DIGIT_MAP[c])
        else:
            res.append(c)
    return "".join(res)

def to_bold_digits(val) -> str:
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

def to_subscript_digits(val) -> str:
    return "".join(SUBSCRIPT_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
FIREBASE_RTDB_URL = "https://x7e77eey-default-rtdb.firebaseio.com"
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://medieval-pink-yqnjxslo-dpjebg2ugq2r.edgeone.dev/apipid.json")
HEADLESS_MODE = os.environ.get("HEADLESS", "true").lower() in ["true", "1", "yes"]

custom_arg = sys.argv[1].strip() if len(sys.argv) > 1 else ""
if custom_arg.isdigit():
    WORKER_ALIAS = f"W-{int(custom_arg):02d}"
elif custom_arg:
    WORKER_ALIAS = custom_arg.upper()
else:
    WORKER_ALIAS = f"W-{uuid.uuid4().hex[:4].upper()}"

NODE_ID = f"worker_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:4]}"
cached_latency = 50.0

PROFILES_BASE_DIR = os.path.expanduser("~/.ff_bot_profiles")
os.makedirs(PROFILES_BASE_DIR, exist_ok=True)

active_sessions: dict[str, dict] = {}
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
    ev_id = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
    payload = {
        "type": event_type,
        "worker_id": NODE_ID,
        "timestamp": time.time(),
        **data
    }
    firebase_sync_http(f"manager_events/{ev_id}", "PUT", payload)

def kill_process_tree(pid: int):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            try:
                child.terminate()
            except Exception:
                pass
        parent.terminate()
    except Exception:
        pass

def cleanup_zombie_browsers():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = proc.info.get('name', '').lower()
            if 'geckodriver' in pname or 'firefox' in pname:
                proc.terminate()
        except Exception:
            pass

def terminate_session_cleanly(session_id: str):
    sess = active_sessions.pop(session_id, None)
    if sess:
        sess["is_trading"] = False
        drv = sess.get("driver")
        if drv:
            try:
                drv.quit()
            except Exception:
                pass
        p_dir = sess.get("profile_dir")
        if p_dir and os.path.exists(p_dir):
            try:
                shutil.rmtree(p_dir, ignore_errors=True)
            except Exception:
                pass
        gc.collect()

def allocate_session_tab(session_id: str, target_url: str):
    sess = active_sessions.setdefault(session_id, {})
    sess["lock"] = threading.RLock()

    p_dir = os.path.join(PROFILES_BASE_DIR, f"p_{session_id}")
    sess["profile_dir"] = p_dir

    options = Options()
    if HEADLESS_MODE:
        options.add_argument("-headless")
    options.add_argument("--window-size=412,915")
    options.add_argument("--no-remote")

    # Mobile User Agent
    options.set_preference("general.useragent.override",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36")

    # RAM and Performance optimizations
    options.set_preference("browser.sessionhistory.max_entries", 2)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("image.mem.surfacecache.max_size_kb", 2048)
    options.set_preference("javascript.options.mem.max", 65536)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("network.http.use-cache", False)

    # CRITICAL: Keep WebGL & Canvas enabled so WinGo HTML5 game loaders pass 100% without freezing!
    options.set_preference("webgl.disabled", False)
    options.set_preference("dom.disable_open_during_load", False)

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)
    driver.set_page_load_timeout(35)
    driver.set_script_timeout(20)
    driver.implicitly_wait(2)
    driver.set_window_size(412, 915)

    try:
        driver.get(target_url)
    except Exception as e:
        logger.warning(f"Initial navigation warning for {session_id}: {e}")

    sess["driver"] = driver
    sess["handle"] = driver.current_window_handle
    return driver, sess["handle"]

def safe_tab_execute(session_id: str, task_fn):
    sess = active_sessions.get(session_id)
    if not sess or not sess.get("driver"):
        return None
    with sess.get("lock", threading.RLock()):
        try:
            return task_fn(sess["driver"])
        except Exception as e:
            logger.debug(f"Tab execution transient error on {session_id}: {e}")
            return None

# ==============================================================================
# JAVASCRIPT INJECTION SCRIPTS
# ==============================================================================

MODAL_AUTO_DISMISSER_JS = """
(function(){
    // Universal auto-dismisser for login splash, notices, daily bonuses, and Star/Cancel rating dialogs
    const dismissSelectors = [
        '.announcement-box', '.bonus-dialog', '.van-overlay', '.van-dialog',
        '.popup-notice', '.notice-dialog', '.winning-tip', '.van-popup--center',
        '[class*="star" i]', '[class*="rating" i]', '[class*="notice" i]',
        '[class*="activity" i]', '[class*="daily" i]', '[class*="announcement" i]'
    ];
    dismissSelectors.forEach(sel => {
        document.querySelectorAll(sel).forEach(el => {
            try {
                // Try clicking Cancel, Close, or Confirm buttons inside the dialog
                const btn = el.querySelector('button, .van-button--primary, .van-button--default, .van-dialog__cancel, .van-dialog__confirm, .close-btn, .van-icon-cross, .icon-close, [class*="close" i], [class*="cancel" i]');
                if (btn) btn.click();
                el.remove();
            } catch(e){}
        });
    });

    // Dismiss 100% frozen loading masks
    document.querySelectorAll('[class*="loading" i], [class*="progress" i], .splash').forEach(ldr => {
        if (ldr.innerText && ldr.innerText.includes('100%')) {
            try { ldr.style.display = 'none'; ldr.remove(); } catch(e){}
        }
    });

    return true;
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const password = arguments[1];

let phoneInput = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="mobile" i], input[placeholder*="number" i], input[placeholder*="手机" i], .phone-input input');
let passInput = document.querySelector('input[type="password"], input[placeholder*="password" i], input[placeholder*="密码" i]');

if (!phoneInput) {
    let allInputs = document.querySelectorAll('input:not([type="hidden"])');
    if (allInputs.length >= 2) {
        phoneInput = allInputs[0];
        passInput = allInputs[1];
    }
}

if (phoneInput && passInput) {
    phoneInput.focus();
    let setVal = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
    if (setVal) {
        setVal.call(phoneInput, phone);
        setVal.call(passInput, password);
    } else {
        phoneInput.value = phone;
        passInput.value = password;
    }

    ['input', 'change', 'blur'].forEach(evt => {
        phoneInput.dispatchEvent(new Event(evt, { bubbles: true }));
        passInput.dispatchEvent(new Event(evt, { bubbles: true }));
    });

    // Find and click Login button
    setTimeout(() => {
        let loginBtn = document.querySelector('button.login-btn, button[class*="login" i], .van-button--primary, .van-button--danger');
        if (!loginBtn) {
            let btns = document.querySelectorAll('button, div[role="button"], span');
            for (let b of btns) {
                let txt = (b.innerText || '').trim().toLowerCase();
                if (txt === 'login' || txt === 'log in' || txt === 'sign in' || txt === '登录' || txt === 'লগইন') {
                    loginBtn = b;
                    break;
                }
            }
        }
        if (loginBtn) {
            ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(evt => {
                try { loginBtn.dispatchEvent(new MouseEvent(evt, { bubbles: true, cancelable: true, view: window })); } catch(e){}
            });
            try { loginBtn.click(); } catch(e){}
        }
    }, 200);

    return "SUCCESS";
}
return "NOT_FOUND";
"""

CHECK_LOGIN_STATUS_JS = """
const currentUrl = window.location.href;
const bodyText = document.body ? document.body.innerText : '';

// Error 22 auto-takeover resolution (Account currently logged in elsewhere)
if (bodyText.includes('Error 22') || bodyText.includes('logged in another') || bodyText.includes('already logged')) {
    let confirmBtn = document.querySelector('.van-dialog__confirm, button[class*="confirm" i]');
    if (confirmBtn) {
        try { confirmBtn.click(); } catch(e){}
    }
}

// Bypasses login screen when authenticated
if (currentUrl.includes('#/main') || currentUrl.includes('#/home') || currentUrl.includes('#/saasLottery') || currentUrl.includes('#/wallet')) {
    return "LOGGED_IN";
}

if (bodyText.includes('Wallet') || bodyText.includes('Balance') || bodyText.includes('Deposit') || bodyText.includes('Withdraw') || bodyText.includes('Win Go') || bodyText.includes('SaasLottery')) {
    return "LOGGED_IN";
}

let loginFailedMsg = document.querySelector('.van-toast, .error-tip, .van-field__error-message');
if (loginFailedMsg && loginFailedMsg.innerText) {
    return "FAILED:" + loginFailedMsg.innerText;
}

return "PENDING";
"""

WINGO_PERSISTENT_NAV_JS = """
const targetUrl = arguments[0];
(function(){
    document.querySelectorAll('.announcement-box, .bonus-dialog, .van-overlay, .van-dialog, [class*="star" i]').forEach(el => {
        try {
            const btn = el.querySelector('button, .van-button--primary, .van-dialog__cancel, .close-btn');
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

// Dismiss Star / Cancel / Notice popups
document.querySelectorAll('.van-dialog__confirm, .dialog-close, .van-popup__close-icon, button[class*="close" i], button[class*="cancel" i], .van-dialog button').forEach(btn => {
    try { btn.click(); } catch(e){}
});

// Dismiss / unfreeze 100% loaders
document.querySelectorAll('[class*="loading" i], [class*="progress" i], .splash').forEach(ldr => {
    if (ldr.innerText && ldr.innerText.includes('100%')) {
        try { ldr.style.display = 'none'; } catch(e){}
    }
});

if (hash.includes('WinGo') || href.includes('WinGo') || bodyText.includes('Win Go') || bodyText.includes('30S') || bodyText.includes('Time remaining')) {
    return true;
}
return false;
"""

FETCH_BALANCE_JS = """
let targetedEls = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
for (let i = 0; i < targetedEls.length; i++) {
    let txt = targetedEls[i].innerText || '';
    let match = txt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
    if (match) return parseFloat(match[1].replace(/,/g, ''));
}

let els = document.querySelectorAll('span, div, p');
for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.includes('Wallet balance') || txt.includes('Balance')) {
        let parentTxt = (els[i].parentNode && els[i].parentNode.innerText) ? els[i].parentNode.innerText : '';
        let match = parentTxt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
        if (match) return parseFloat(match[1].replace(/,/g, ''));
    }
}

for (let i = 0; i < els.length; i++) {
    let txt = els[i].innerText || '';
    if (txt.trim().match(/^[৳₹$€£]\\s*[\\d,]+\\.?\\d*$/)) {
        return parseFloat(txt.replace(/[^\\d.]/g, ''));
    }
}

try {
    let b = localStorage.getItem('user_balance') || sessionStorage.getItem('user_balance');
    if (b && parseFloat(b) > 0) return parseFloat(b);
} catch(e){}

return 0.0;
"""

# ==============================================================================
# 24/7 CONSECUTIVE ROUND EXECUTION & HIGH-FREQUENCY BETTING CORE
# ==============================================================================

WINGO_CORE_JS = """
const autoTargetGoal = parseFloat(arguments[0]) || 0;
const autoTotalSteps = parseInt(arguments[1]) || 5;
const targetApiUrl = arguments[2] || "https://medieval-pink-yqnjxslo-dpjebg2ugq2r.edgeone.dev/apipid.json";
const workerIdentifier = arguments[3] || "";

(function(){
    // Setup state container
    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, parseInt(autoTotalSteps) || 5);
        if (autoTargetGoal && autoTargetGoal > 0) {
            let liveBal = (typeof chkBal === 'function') ? chkBal() : window.__WINGO_ST.curBal;
            window.__WINGO_ST.tgtAmt = (autoTargetGoal <= liveBal && liveBal > 0) ? (liveBal + autoTargetGoal) : autoTargetGoal;
        }
        return "ALREADY_RUNNING_UPDATED";
    }

    if (window.__WINGO_ST && window.__WINGO_ST.autoInt) {
        clearInterval(window.__WINGO_ST.autoInt);
    }

    // Dynamic 12-Slot Stagger Offset (evenly distributes calls within 1000ms: 0ms, 83ms, 166ms... 916ms)
    // Ensures multiple worker nodes poll smoothly every 1000ms without hammering or lagging server
    let instSlot = 0;
    if (typeof workerIdentifier === 'number') {
        instSlot = Math.abs(workerIdentifier) % 12;
    } else if (typeof workerIdentifier === 'string' && workerIdentifier.length > 0) {
        let hash = 0;
        for (let i = 0; i < workerIdentifier.length; i++) {
            hash = ((hash << 5) - hash) + workerIdentifier.charCodeAt(i);
            hash |= 0;
        }
        instSlot = Math.abs(hash) % 12;
    } else {
        instSlot = Math.floor(Math.random() * 12);
    }
    const staggerOffsetMs = instSlot * 83;

    const st = {
        isRun: true,
        tgtAmt: 0,
        startBal: 0,
        curBal: 0,
        autoInt: null,
        isTrd: false,
        stpIdx: 0,
        steps: Math.max(1, parseInt(autoTotalSteps) || 5),
        dynSeq: [],
        tradesDone: 0,
        activePeriod: null,
        placedPeriod: null,
        lastTradedPeriod: null,
        lastTradedPred: null,
        evaluatedPeriod: null,
        circuitBreakerTriggered: false,
        w: 0,
        l: 0,
        cur_w_streak: 0,
        cur_l_streak: 0,
        max_w_streak: 0,
        max_l_streak: 0,
        externalPrediction: null,
        _trdLockTs: 0
    };
    window.__WINGO_ST = st;

    // External injection hook from Python thread (guarantees real-time sync even if CSP blocks window.fetch)
    window.__WINGO_FEED_PRED = function(data) {
        if (data && typeof data === 'object') {
            st.externalPrediction = data;
        }
    };

    function chkBal() {
        try {
            let targeted = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i], [class*="wallet" i]');
            for (let i = 0; i < targeted.length; i++) {
                let txt = targeted[i].innerText || '';
                let match = txt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
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
                    let match = parentTxt.match(/[৳₹$€£]\\s*([\\d,]+\\.?\\d*)/);
                    if (match) {
                        st.curBal = parseFloat(match[1].replace(/,/g, ''));
                        return st.curBal;
                    }
                }
            }
        } catch(e) {}
        return st.curBal || 0;
    }

    // WinGo 30s Countdown Inspector
    function getRemainingSeconds() {
        try {
            let timeEls = document.querySelectorAll('.time-box, .Time, .van-count-down');
            for (let el of timeEls) {
                let txt = (el.innerText || '').trim();
                let m = txt.match(/(\\d+)\\s*[:：]\\s*(\\d+)/);
                if (m) {
                    return (parseInt(m[1], 10) * 60) + parseInt(m[2], 10);
                }
                let cleanDigits = txt.replace(/\\D/g, '');
                if (cleanDigits.length > 0 && cleanDigits.length <= 2) {
                    let s = parseInt(cleanDigits, 10);
                    if (s >= 0 && s <= 35) return s;
                }
            }
        } catch(e){}
        return 30; // Default safe: allow trade if custom countdown
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

    // Precision Button Selector for Big / Small / Smok
    function findBetButton(predType) {
        let isBig = (predType === 'BIG');
        let isSmall = (predType === 'SMALL');

        // 1. Direct platform class selectors
        if (isBig) {
            let b = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button.bign, div.bign, .bign');
            if (b && b.offsetParent !== null) return b;
        } else if (isSmall) {
            let s = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button.smalln, div.smalln, .smalln');
            if (s && s.offsetParent !== null) return s;
        }

        // 2. Elements inside betting panel footer
        let footBtns = document.querySelectorAll('.Betting__C-foot button, .Betting__C-foot div, .Betting__C button');
        for (let btn of footBtns) {
            let t = (btn.innerText || '').trim().toLowerCase();
            if (isBig && (t === 'big' || t.startsWith('big'))) return btn;
            if (isSmall && (t === 'small' || t === 'smok' || t.startsWith('small') || t.startsWith('smok'))) return btn;
        }

        // 3. Document-wide scan with visible button dimensions
        let allCandidates = document.querySelectorAll('button, div[role="button"], span');
        for (let c of allCandidates) {
            if (c.offsetParent === null || c.clientHeight < 18 || c.clientWidth < 30) continue;
            let t = (c.innerText || '').trim().toLowerCase();
            if (isBig && (t === 'big' || t === '大')) return c;
            if (isSmall && (t === 'small' || t === 'smok' || t === '小')) return c;
        }
        return null;
    }

    // Ultra-Fast Trade Executor with 3.5s failsafe
    const exeTrd = (pred, amt, cb) => {
        let finished = false;
        const done = (status) => {
            if (!finished) {
                finished = true;
                if (cb) cb(status);
            }
        };

        setTimeout(() => done(false), 3500);

        try {
            // Check countdown lock: WinGo 30S locks only in the last 4 seconds
            let remSec = getRemainingSeconds();
            if (remSec <= 4 && remSec >= 0) {
                return done(false);
            }

            // Dismiss lingering alerts or dialogs
            document.querySelectorAll('.van-dialog, .announcement-box, .winning-tip, .bonus-dialog').forEach(l => {
                let cBtn = l.querySelector('.van-dialog__confirm, .van-icon-cross, button, .close-btn');
                if (cBtn) try { cBtn.click(); } catch(e){}
            });

            let normPred = String(pred).toUpperCase().trim();
            if (normPred.includes('SMOK') || normPred.includes('SMALL') || normPred === 'S') {
                normPred = 'SMALL';
            } else {
                normPred = 'BIG';
            }

            let betBtn = findBetButton(normPred);
            if (!betBtn) {
                return done(false);
            }

            drx_simClick(betBtn);

            // Wait for Vant UI bottom sheet popup and input field to mount
            let attempts = 0;
            let checkInterval = setInterval(() => {
                attempts++;
                let inpEl = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input, input[type='tel'], input[inputmode='numeric']");
                let popupEl = document.querySelector(".van-popup--bottom, .van-popup, .Betting__C-popup");

                if (inpEl || popupEl || attempts > 20) {
                    clearInterval(checkInterval);

                    if (inpEl) {
                        inpEl.focus();
                        let setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                        if (setter) setter.call(inpEl, String(amt));
                        else inpEl.value = String(amt);
                        drx_triggerEvent(inpEl, 'input');
                        drx_triggerEvent(inpEl, 'change');
                        drx_triggerEvent(inpEl, 'blur');
                    }

                    setTimeout(() => {
                        let confirmBtn = document.querySelector('button.bet-amount, .Betting__C-foot-total, .van-button--danger, .van-button--primary, button[class*="confirm" i]');
                        if (!confirmBtn) {
                            let docBtns = document.querySelectorAll('button, div[role="button"]');
                            for (let b of docBtns) {
                                let txt = (b.innerText || '').toLowerCase();
                                if ((txt.includes('total') || txt.includes('confirm') || txt.includes('bet') || txt.includes('立即下注') || txt.includes('৳') || txt.includes('₹') || txt.includes('presale')) && b.offsetParent) {
                                    confirmBtn = b;
                                    break;
                                }
                            }
                        }
                        if (confirmBtn) {
                            drx_simClick(confirmBtn);
                            setTimeout(() => done(true), 300);
                        } else {
                            done(false);
                        }
                    }, 120);
                }
            }, 40);
        } catch(e) {
            done(false);
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

    // 24/7 Consecutive Poller & Real-Time Trade Engine (Runs every 1000ms on staggered schedule)
    const apiLoopTask = async () => {
        if (!st.isRun) return;
        if (st.isTrd) return;
        if (isFetchingApi) return;

        isFetchingApi = true;
        try {
            chkBal();
            if (st.tgtAmt > 0 && st.curBal >= st.tgtAmt && st.startBal > 0) {
                st.isRun = false;
                st.isTrd = false;
                if (st.autoInt) clearInterval(st.autoInt);
                isFetchingApi = false;
                return;
            }

            let ts = Date.now();
            let sep = targetApiUrl.includes('?') ? '&' : '?';
            let fetchUrl = targetApiUrl + sep + "ts=" + ts + "&_r=" + Math.random().toString(36).substring(2, 6);

            let dataObj = null;
            // 1. Check if Python background thread fed a newer prediction
            if (st.externalPrediction && st.externalPrediction.next) {
                dataObj = st.externalPrediction;
            }

            // 2. Fetch directly from EdgeOne API
            if (!dataObj || (dataObj.next && dataObj.next.period === st.lastTradedPeriod)) {
                let controller = new AbortController();
                let fTimeout = setTimeout(() => controller.abort(), 2000);
                try {
                    let res = await fetch(fetchUrl, {
                        signal: controller.signal,
                        headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' }
                    });
                    clearTimeout(fTimeout);
                    if (res.ok) {
                        dataObj = await res.json();
                    }
                } catch(fetchErr) {
                    clearTimeout(fTimeout);
                    // Use external prediction if fetch failed
                    if (st.externalPrediction) dataObj = st.externalPrediction;
                }
            }

            if (dataObj) {
                let activeLogic = Array.isArray(dataObj) ? dataObj[0] : (dataObj.data ? dataObj.data[0] : dataObj);
                if (activeLogic) {
                    let targetNext = activeLogic.next || (activeLogic.data && activeLogic.data.next) || activeLogic;
                    let incomingPeriod = '';
                    if (targetNext && (targetNext.period || targetNext.pid || targetNext.pld)) {
                        incomingPeriod = String(targetNext.period || targetNext.pid || targetNext.pld).trim();
                    } else if (activeLogic.period || activeLogic.pid) {
                        incomingPeriod = String(activeLogic.period || activeLogic.pid).trim();
                    }

                    // Normalize prediction (BIG / SMALL / SMOK)
                    let rawPred = (targetNext && (targetNext.size || targetNext.pred)) || (activeLogic.pred || activeLogic.prediction || activeLogic.size) || 'BIG';
                    let predText = String(rawPred).toUpperCase().trim();
                    let prediction = 'BIG';
                    if (predText.includes('SMOK') || predText.includes('SMALL') || predText === 'S') {
                        prediction = 'SMALL';
                    } else {
                        prediction = 'BIG';
                    }

                    st.activePeriod = incomingPeriod;

                    // A. Evaluate Previous Round Result when period transitions
                    if (st.lastTradedPeriod && incomingPeriod && st.evaluatedPeriod !== incomingPeriod && st.lastTradedPeriod !== incomingPeriod) {
                        let tempHist = activeLogic.history || (activeLogic.data && activeLogic.data.history) || [];
                        let finishedItem = tempHist.find(h => String(h.period || h.pid || '') === String(st.lastTradedPeriod)) || tempHist[0];
                        let actualSize = '';
                        if (finishedItem) {
                            if (finishedItem.actual_size) {
                                actualSize = String(finishedItem.actual_size).toUpperCase().trim();
                            } else if (finishedItem.actual === 'BIG' || finishedItem.actual === 1 || (typeof finishedItem.actual === 'number' && finishedItem.actual >= 5)) {
                                actualSize = 'BIG';
                            } else if (finishedItem.actual === 'SMALL' || finishedItem.actual === 0 || (typeof finishedItem.actual === 'number' && finishedItem.actual < 5)) {
                                actualSize = 'SMALL';
                            }
                        }

                        let won = false;
                        if (actualSize) {
                            won = (st.lastTradedPred === actualSize);
                        } else {
                            let pBal = parseFloat(sessionStorage.getItem('drx_p_bal') || '0');
                            if (pBal > 0 && st.curBal > pBal) won = true;
                        }

                        if (won) {
                            st.w++;
                            st.cur_w_streak++;
                            st.cur_l_streak = 0;
                            if (st.cur_w_streak > st.max_w_streak) st.max_w_streak = st.cur_w_streak;
                            st.stpIdx = 0; // Win: reset to Step 1
                        } else {
                            st.l++;
                            st.cur_l_streak++;
                            st.cur_w_streak = 0;
                            if (st.cur_l_streak > st.max_l_streak) st.max_l_streak = st.cur_l_streak;

                            // Loss: advance step. If max step reached, wrap around to Step 1 so 24/7 continuous trading NEVER stops!
                            if (st.stpIdx >= st.steps - 1) {
                                st.stpIdx = 0;
                            } else {
                                st.stpIdx = st.stpIdx + 1;
                            }
                        }
                        st.evaluatedPeriod = incomingPeriod;
                    }

                    // B. Consecutive Trade Placement (Zero-Skip 24/7 Engine)
                    let sSig = sessionStorage.getItem('drx_sig');
                    let alreadyPlaced = (st.placedPeriod === incomingPeriod) || (sSig === incomingPeriod);

                    if (incomingPeriod && !alreadyPlaced) {
                        let remSec = getRemainingSeconds();
                        if (remSec > 4 || remSec < 0) {
                            let nBal = chkBal();
                            if (st.tgtAmt > 0 && nBal >= st.tgtAmt && st.startBal > 0) {
                                st.isRun = false;
                                st.isTrd = false;
                                isFetchingApi = false;
                                return;
                            }

                            st.dynSeq = calcSeq(nBal > 0 ? nBal : st.tgtAmt, st.steps);
                            if (st.stpIdx >= st.dynSeq.length) st.stpIdx = st.dynSeq.length - 1;
                            let tAmt = Math.floor(st.dynSeq[st.stpIdx]) || 1;
                            if (nBal > 0 && nBal < tAmt) {
                                st.stpIdx = 0;
                                tAmt = Math.floor(st.dynSeq[0]) || 1;
                            }

                            st.isTrd = true;
                            exeTrd(prediction, tAmt, (suc) => {
                                if (suc) {
                                    st.placedPeriod = incomingPeriod;
                                    st.lastTradedPeriod = incomingPeriod;
                                    st.lastTradedPred = prediction;
                                    sessionStorage.setItem('drx_sig', incomingPeriod);
                                    sessionStorage.setItem('drx_p_bal', String(st.curBal));
                                    st.tradesDone++;
                                }
                                st.isTrd = false;
                            });
                        }
                    }
                }
            }
        } catch(e) {
            st.isTrd = false;
        }
        isFetchingApi = false;
    };

    // 8-second watchdog to release trade-lock if page freezes
    setInterval(() => {
        if (st.isTrd) {
            if (!st._trdLockTs) st._trdLockTs = Date.now();
            else if (Date.now() - st._trdLockTs > 8000) {
                st.isTrd = false;
                isFetchingApi = false;
                st._trdLockTs = 0;
            }
        } else {
            st._trdLockTs = 0;
        }
    }, 1500);

    // Staggered boot across 12 slots, repeating every 1000ms
    setTimeout(() => {
        apiLoopTask();
        st.autoInt = setInterval(apiLoopTask, 1000);
    }, staggerOffsetMs);

    return "GHOST_TRADING_INITIATED_24_7";
})();
"""

# ==============================================================================
# WORKER EXECUTION SEQUENCES
# ==============================================================================

def execute_worker_login(chat_id: int, sid: str, phone: str, password: str, login_url: str, site_name: str, anim_msg_id: int | None):
    # Step 1: Initialize browser
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 20,
        "text": "Initializing dedicated browser container...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    driver, handle = allocate_session_tab(sid, login_url)
    if not driver:
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": f"Failed to allocate session for {site_name}",
            "anim_msg_id": anim_msg_id
        })
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    # Step 2: Navigating & form check
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 40,
        "text": "Navigating to platform portal & bypassing guards...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    form_ready = False
    for _ in range(12):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))
        if res == "SUCCESS":
            form_ready = True
            break
        time.sleep(0.6)

    if not form_ready:
        safe_tab_execute(sid, lambda drv: drv.get(login_url))
        time.sleep(1.5)
        safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
        safe_tab_execute(sid, lambda drv: drv.execute_script(AUTO_FILL_AND_CLICK_JS, phone, password))

    # Step 3: Authenticating credentials
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 60,
        "text": "Submitting credentials & establishing token...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })
    time.sleep(1.5)

    # Step 4: Verification & Error 22 auto-resolution
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 80,
        "text": "Resolving session security & validating session...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    logged_in = False
    fail_reason = ""
    for _ in range(15):
        status = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if status == "LOGGED_IN":
            logged_in = True
            break
        elif status and status.startswith("FAILED:"):
            fail_reason = status.split(":", 1)[1]
            break
        time.sleep(0.6)

    if not logged_in and not fail_reason:
        curr_url = safe_tab_execute(sid, lambda drv: drv.current_url) or ""
        if "#/login" not in curr_url:
            logged_in = True

    if not logged_in:
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "site_name": site_name,
            "reason": fail_reason or "Invalid phone or password",
            "anim_msg_id": anim_msg_id
        })
        terminate_session_cleanly(sid)
        return

    # Dismiss any post-login modals
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    emit_event_to_manager("LOGIN_SUCCESS", {
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "phone": phone,
        "worker_id": NODE_ID,
        "anim_msg_id": anim_msg_id
    })

def execute_worker_prepare_wingo(chat_id: int, sid: str, wingo_url: str, site_name: str):
    sess = active_sessions.get(sid)
    if not sess:
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_PERSISTENT_NAV_JS, wingo_url))
    time.sleep(1.5)

    verified = False
    for _ in range(15):
        is_ready = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_WINGO_READY_JS))
        if is_ready:
            verified = True
            break
        time.sleep(0.5)

    if not verified:
        safe_tab_execute(sid, lambda drv: drv.get(wingo_url))
        time.sleep(2.0)
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

# Python Background Direct API Poller Thread (Dual Layer)
def python_prediction_poller(session_id: str, pred_api_url: str):
    logger.info(f"Python direct prediction poller started for session {session_id} on: {pred_api_url}")
    # Compute slot offset across 12 instances
    slot_num = abs(hash(NODE_ID)) % 12
    stagger_sec = (slot_num * 83) / 1000.0
    time.sleep(stagger_sec)

    sess = active_sessions.get(session_id)
    while sess and sess.get("is_trading") and WORKER_ACTIVE:
        try:
            req = urllib.request.Request(
                pred_api_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Cache-Control": "no-cache"}
            )
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                raw_data = resp.read()
                if raw_data:
                    data = json.loads(raw_data.decode("utf-8"))
                    safe_tab_execute(session_id, lambda drv: drv.execute_script(
                        "if (window.__WINGO_FEED_PRED) window.__WINGO_FEED_PRED(arguments[0]);", data
                    ))
        except Exception as e:
            logger.debug(f"Direct API poller tick: {e}")
        time.sleep(1.0)

def worker_monitor_trading_loop(chat_id: int, sid: str, site_name: str):
    sess = active_sessions.get(sid)
    if not sess:
        return

    while sess.get("is_trading", False) and WORKER_ACTIVE:
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

        st_obj = safe_tab_execute(sid, _get_st)
        if st_obj and isinstance(st_obj, dict):
            c_bal = float(st_obj.get("curBal", 0.0))
            if c_bal > 0:
                sess["cur_bal"] = c_bal
                sess["current_balance"] = c_bal

            tgt_amt = float(st_obj.get("tgtAmt", 0.0))
            start_b = float(st_obj.get("startBal", 0.0))
            is_run = bool(st_obj.get("isRun", True))
            circuit_breaker = bool(st_obj.get("circuitBreakerTriggered", False))
            step_idx = int(st_obj.get("step", 1))
            tot_steps = int(st_obj.get("steps", 5))
            sess["wins"] = int(st_obj.get("w", 0))
            sess["losses"] = int(st_obj.get("l", 0))

            task_payload = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "RUNNING" if is_run else "PAUSED",
                "start_balance": start_b,
                "current_balance": sess.get("cur_bal", 0.0),
                "target_amount": tgt_amt,
                "step": step_idx,
                "total_steps": tot_steps,
                "wins": sess.get("wins", 0),
                "losses": sess.get("losses", 0),
                "currency": "BDT",
                "updated_at": time.time()
            }
            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

            if circuit_breaker:
                sess["is_trading"] = False
                emit_event_to_manager("CIRCUIT_BREAKER_TRIGGERED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": start_b,
                    "final_balance": sess.get("cur_bal", 0.0),
                    "step": step_idx,
                    "total_steps": tot_steps,
                    "wins": sess.get("wins", 0),
                    "losses": sess.get("losses", 0)
                })
                terminate_session_cleanly(sid)
                return

            if tgt_amt > 0 and sess.get("cur_bal", 0.0) >= tgt_amt and start_b > 0:
                sess["is_trading"] = False
                task_payload["status"] = "COMPLETED"
                firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)
                emit_event_to_manager("TARGET_ACHIEVED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": start_b,
                    "final_balance": sess.get("cur_bal", 0.0),
                    "wins": sess.get("wins", 0),
                    "losses": sess.get("losses", 0)
                })
                terminate_session_cleanly(sid)
                return

            if not is_run:
                sess["is_trading"] = False
                return

        time.sleep(2.5)

# ==============================================================================
# WORKER TASK LISTENER & DISPATCHER
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
                    sid = task.get("session_id")
                    chat_id = task.get("chat_id")
                    site_name = task.get("site_name", "Amar Club")
                    login_url = task.get("login_url")
                    wingo_url = task.get("wingo_url")
                    phone = task.get("phone")
                    password = task.get("password")
                    anim_msg_id = task.get("anim_msg_id")

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
                        "last_activity": time.time()
                    }

                    threading.Thread(
                        target=execute_worker_login,
                        args=(chat_id, sid, phone, password, login_url, site_name, anim_msg_id),
                        daemon=True
                    ).start()

            action = firebase_sync_http(f"terminals/{NODE_ID}/action", "GET")
            if action and isinstance(action, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/action", "DELETE")
                kind = action.get("kind")
                sid = action.get("session_id")
                chat_id = action.get("chat_id")

                if kind in ["EMERGENCY_STOP", "EMERGENCY_STOP_ALL"]:
                    logger.warning(f"Emergency stop received: {kind}. Terminating all worker sessions!")
                    for s in list(active_sessions.keys()):
                        terminate_session_cleanly(s)
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
                    target_goal = float(action.get("target_goal", 0.0))
                    total_steps = int(action.get("total_steps", 5))
                    pred_url = action.get("prediction_api_url", PREDICTION_API_URL)

                    sess["is_trading"] = True
                    safe_tab_execute(sid, lambda drv: drv.execute_script(
                        WINGO_CORE_JS,
                        target_goal,
                        total_steps,
                        pred_url,
                        NODE_ID
                    ))
                    time.sleep(0.5)
                    cur_b = sess.get("current_balance", 0.0)
                    sess["start_bal"] = cur_b

                    # Start dual-layer Python prediction poller
                    threading.Thread(
                        target=python_prediction_poller,
                        args=(sid, pred_url),
                        daemon=True
                    ).start()

                    # Start trading state monitor loop
                    threading.Thread(
                        target=worker_monitor_trading_loop,
                        args=(chat_id, sid, sess["site_name"]),
                        daemon=True
                    ).start()

                elif kind == "REQUEST_TELEMETRY" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _tel(drv):
                        return drv.execute_script("return window.__WINGO_ST ? { curBal: window.__WINGO_ST.curBal, tgtAmt: window.__WINGO_ST.tgtAmt, w: window.__WINGO_ST.w, l: window.__WINGO_ST.l, step: (window.__WINGO_ST.stpIdx || 0) + 1 } : null;")
                    tel_data = safe_tab_execute(sid, _tel) or {}
                    emit_event_to_manager("LIVE_TELEMETRY", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "site_name": sess.get("site_name", ""),
                        "current_balance": tel_data.get("curBal", sess.get("current_balance", 0.0)),
                        "target_total": tel_data.get("tgtAmt", 0.0),
                        "wins": tel_data.get("w", 0),
                        "losses": tel_data.get("l", 0),
                        "step": tel_data.get("step", 1)
                    })

                elif kind == "REQUEST_BALANCE" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _b(drv):
                        return drv.execute_script(FETCH_BALANCE_JS)
                    b_val = safe_tab_execute(sid, _b) or sess.get("cur_bal", 0.0)
                    sess["current_balance"] = float(b_val)
                    sess["cur_bal"] = float(b_val)
                    emit_event_to_manager("BALANCE_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "live_balance": float(b_val),
                        "call_id": action.get("call_id")
                    })

                elif kind == "REQUEST_STATS" and sid in active_sessions:
                    sess = active_sessions[sid]
                    def _s(drv):
                        return drv.execute_script("""
                            if (window.__WINGO_ST) {
                                return {
                                    curBal: window.__WINGO_ST.curBal || 0.0,
                                    tgtAmt: window.__WINGO_ST.tgtAmt || 0.0,
                                    step: (window.__WINGO_ST.stpIdx || 0) + 1,
                                    steps: window.__WINGO_ST.steps || 5,
                                    w: window.__WINGO_ST.w || 0,
                                    l: window.__WINGO_ST.l || 0,
                                    cur_w_streak: window.__WINGO_ST.cur_w_streak || 0,
                                    max_w_streak: window.__WINGO_ST.max_w_streak || 0,
                                    cur_l_streak: window.__WINGO_ST.cur_l_streak || 0,
                                    max_l_streak: window.__WINGO_ST.max_l_streak || 0,
                                    tradesDone: window.__WINGO_ST.tradesDone || 0
                                };
                            }
                            return null;
                        """)
                    stat_obj = safe_tab_execute(sid, _s) or {}
                    emit_event_to_manager("STATS_RESPONSE", {
                        "session_id": sid,
                        "chat_id": chat_id,
                        "data": stat_obj
                    })

                elif kind == "STOP_TRADING" and sid in active_sessions:
                    sess = active_sessions[sid]
                    sess["is_trading"] = False
                    safe_tab_execute(sid, lambda drv: drv.execute_script("if (window.__WINGO_ST) { window.__WINGO_ST.isRun = false; }"))

                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Worker task loop tick: {e}")
        time.sleep(1.0)

# ==============================================================================
# HEARTBEAT & LATENCY MONITOR
# ==============================================================================

def latency_monitor_loop():
    global cached_latency
    while WORKER_ACTIVE:
        try:
            cached_latency = measure_network_latency(FIREBASE_RTDB_URL)
        except Exception:
            cached_latency = 99.0
        time.sleep(20)

def worker_register_node():
    node_data = {
        "node_id": NODE_ID,
        "alias": WORKER_ALIAS,
        "status": "IDLE",
        "registered_at": time.time(),
        "heartbeat": time.time(),
        "latency": cached_latency,
        "os": sys.platform,
        "headless": HEADLESS_MODE
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_data)
    logger.info(f"Worker registered to Firebase: {NODE_ID} (Alias: {WORKER_ALIAS})")

def worker_heartbeat_loop():
    while WORKER_ACTIVE:
        try:
            firebase_sync_http(f"terminals/{NODE_ID}", "PATCH", {
                "heartbeat": time.time(),
                "latency": cached_latency,
                "status": "BUSY" if len(active_sessions) > 0 else "IDLE"
            })
        except Exception as e:
            logger.debug(f"Heartbeat tick error: {e}")
        time.sleep(10)

def continuous_24h_watchdog():
    while WORKER_ACTIVE:
        now = time.time()
        for sid, sess in list(active_sessions.items()):
            last_act = sess.get("last_activity", now)
            if now - last_act > 7200 and not sess.get("is_trading"):
                logger.warning(f"Session {sid} idle timeout (>2h). Auto-terminating.")
                terminate_session_cleanly(sid)
        time.sleep(60)

def handle_shutdown_signals(sig=None, frame=None):
    global WORKER_ACTIVE
    logger.info("Shutdown signal caught. Cleaning up worker node...")
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

    cleanup_zombie_browsers()
    worker_register_node()

    threading.Thread(target=latency_monitor_loop, daemon=True).start()
    threading.Thread(target=worker_heartbeat_loop, daemon=True).start()
    threading.Thread(target=continuous_24h_watchdog, daemon=True).start()

    print(f"[*] {to_vip_text('DRX WINGO CLUSTER WORKER ACTIVE')} [{WORKER_ALIAS}] ({NODE_ID})...")
    worker_task_listener()
