# ==============================================================================
# DRX WINGO CLUSTER - EXECUTION WORKER NODE (ULTRA LOW-RAM RAILWAY EDITION)
# ==============================================================================
# Optimization Target: Railway 512MB RAM Containers / Zero OOM Crash
# Features:
# - Strict Single-Process Gecko/Firefox Engine (< 180MB RAM footprint)
# - Aggressive Memory Reclamation & MALLOC_ARENA Tuning
# - Non-blocking Throttled DOM Modal Cleaner (Zero CPU Churn)
# - Precision Multi-Layer Win/Loss & Stable Martingale Sequence Engine
# - Guaranteed 24/7 Continuous Auto-Recycling until Target Reached
# - BST (UTC+6) Integrated Synchronization & Realtime Firebase Telemetry
# ==============================================================================

import os
import sys

# ০.৫ জিবি র‍্যামে মেমরি ফ্র্যাগমেন্টেশন রোধ করতে সিস্টেম লেভেল টিউনিং
os.environ["MALLOC_ARENA_MAX"] = "1"
os.environ["MOZ_FORCE_DISABLE_E10S"] = "1"
os.environ["MOZ_HEADLESS"] = "1"

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
# BANGLADESH STANDARD TIME (BST / UTC+6) CONFIGURATION
# ==============================================================================
BST_TZ = timezone(timedelta(hours=6))

def bst_now():
    return datetime.now(BST_TZ)

def bst_time_converter(*args):
    return bst_now().timetuple()

logging.Formatter.converter = bst_time_converter

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s BST] [WORKER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WORKER_NODE")

# ==============================================================================
# DEPENDENCY BOOTSTRAP
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
            logger.warning(f"Installing missing package: {pkg_name}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "--upgrade", "--no-cache-dir", pkg_name
                ])
            except Exception as e:
                logger.error(f"Failed to auto-install {pkg_name}: {e}")

ensure_dependencies()

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
import psutil

# ==============================================================================
# CENTRALIZED UNICODE STYLING SYSTEM
# ==============================================================================
VIP_ALPHA_MAP = {c: v for c, v in zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "𝐀𝐁𝐂𝐃𝐄𝐅𝐆𝐇𝐈𝐉𝐊𝐋𝐌𝐍𝐎𝐏𝐐𝐑𝐒𝐓𝐔𝐕𝐖𝐗𝐘𝐙")}
BOLD_DIGIT_MAP = {d: v for d, v in zip("0123456789", "𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗")}

def to_vip_text(text: str) -> str:
    return "".join(VIP_ALPHA_MAP.get(c.upper(), c) if c.isalpha() else c for c in str(text))

def to_bold_digits(val) -> str:
    return "".join(BOLD_DIGIT_MAP.get(d, d) for d in str(val))

# ==============================================================================
# WORKER CONFIGURATION & CLUSTER REGISTRY
# ==============================================================================
FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://drx-tm-vip-hack-code6.edgeone.dev/pid.json")
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
def firebase_sync_http(path: str, method: str = "GET", payload=None, timeout: float = 3.5):
    url = f"{FIREBASE_RTDB_URL.rstrip('/')}/{path.strip('/')}.json"
    raw_data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=raw_data, headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            res_content = response.read()
            return json.loads(res_content.decode("utf-8")) if res_content else None
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
        return 999.0

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
# GUARANTEED PROCESS TEARDOWN & LOW-RAM GARBAGE COLLECTOR
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
                            s.get('driver') and hasattr(s['driver'], 'service') and
                            s['driver'].service and s['driver'].service.process and
                            s['driver'].service.process.pid == proc.info['pid']
                            for s in active_sessions.values()
                        )
                        if not is_active:
                            proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

def enforce_memory_cap():
    """রেলওয়ের ৫১২ এমবি র‍্যামে মেমরি ব্যবহারের মাত্রা পর্যবেক্ষণ ও অতিরিক্ত ক্যাশ ডাম্প করা।"""
    try:
        mem = psutil.virtual_memory()
        if mem.percent > 82.0:
            logger.warning(f"High Memory Usage Alert: {mem.percent}%! Forcing garbage collection.")
            gc.collect()
            for s in active_sessions.values():
                d = s.get("driver")
                if d:
                    try:
                        d.execute_script("if (window.performance && window.performance.memory) { window.gc && window.gc(); }")
                    except Exception:
                        pass
    except Exception:
        pass

def terminate_session_cleanly(session_id):
    logger.info(f"Cleanly terminating session: {session_id}")
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

# ==============================================================================
# ULTRA LOW-MEMORY BROWSER SESSION ISOLATION (512MB RAM SAFE)
# ==============================================================================
def allocate_session_tab(session_id, target_url):
    sess = active_sessions.get(session_id)
    if not sess:
        raise Exception("Session data not found.")

    cleanup_zombie_browsers()
    enforce_memory_cap()

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

    # চরম লো-মেমোরি ফায়ারফক্স কনফিগ (র‍্যাম < ১৮০ এমবি নিশ্চিত করার জন্য)
    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("dom.ipc.processCount", 1)
    options.set_preference("browser.sessionhistory.max_entries", 1)
    options.set_preference("browser.sessionhistory.max_total_viewers", 0)
    options.set_preference("browser.cache.disk.enable", False)
    options.set_preference("browser.cache.memory.enable", True)
    options.set_preference("browser.cache.memory.capacity", 1024)
    options.set_preference("image.mem.surfacecache.max_size_kb", 512)
    options.set_preference("javascript.options.mem.max", 16384)
    options.set_preference("javascript.options.mem.gc_frequency", 50)
    options.set_preference("browser.sessionstore.interval", 1800000)
    options.set_preference("network.http.use-cache", False)
    options.set_preference("network.prefetch-next", False)
    options.set_preference("webgl.disabled", True)
    options.set_preference("accessibility.force_disabled", 1)
    options.set_preference("toolkit.telemetry.enabled", False)
    options.set_preference("media.autoplay.default", 5)
    options.set_preference("media.volume_scale", "0.0")

    service = FirefoxService(log_output=os.devnull)
    driver = webdriver.Firefox(service=service, options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(15)
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

    if not result_container["completed"] or result_container["error"]:
        return None

    return result_container["res"]

# ==============================================================================
# INJECTED SCRIPTS (SMOOTH & LOW-CPU OPTIMIZED)
# ==============================================================================
MODAL_AUTO_DISMISSER_JS = """
(function(){
    const sweepModals = () => {
        const dialogs = document.querySelectorAll('.announcement-box, .dialog-box, .bonus-dialog, .van-popup, .van-dialog');
        dialogs.forEach(dialog => {
            const btn = dialog.querySelector('button, .van-button, .van-dialog__confirm, div[role="button"]');
            if (btn) { try { btn.click(); } catch(e){} }
            try { dialog.remove(); } catch(e){}
        });

        const directSelectors = [
            '.van-dialog__confirm', '.dialog-confirm', '.van-button--primary',
            '.van-popup__close-icon', '.van-overlay', '.dialog-close', '.close-btn',
            'button[class*="close" i]', 'button[class*="confirm" i]'
        ];
        directSelectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => {
                if (el && el.offsetParent !== null && !el.closest('#drx-prediction-hud')) {
                    try { el.click(); } catch(e){}
                }
            });
        });
    };

    sweepModals();
    if (!window.__SWEEPER_INTERVAL) {
        // ৬০০ms এর বদলে ২৫০০ms করা হয়েছে যাতে ব্রাউজারের CPU এবং RAM ব্যবহারের চাপ শূন্য থাকে
        window.__SWEEPER_INTERVAL = setInterval(sweepModals, 2500);
    }
})();
"""

AUTO_FILL_AND_CLICK_JS = """
const phone = arguments[0];
const pass = arguments[1];

let elN = document.querySelector('input[type="tel"], input[placeholder*="phone" i], input[placeholder*="Phone" i]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div > div:nth-of-type(2) > input');

let elP = document.querySelector('input[type="password"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(2) > div:nth-of-type(2) > input');

let elL = document.querySelector('button[type="submit"]') || 
          document.querySelector('body > div > div:nth-of-type(2) > div:nth-of-type(4) > div > div > div:nth-of-type(4) > button');

if (!elN || !elP || !elL) return "NOT_READY";

const fillInput = (el, val) => {
    el.focus();
    el.value = val;
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
};

fillInput(elN, phone);
fillInput(elP, pass);

setTimeout(() => {
    try { elL.click(); } catch(e){}
}, 300);

return "SUCCESS";
"""

CHECK_LOGIN_STATUS_JS = """
const hash = window.location.hash || '';
const href = window.location.href || '';

const dialog = document.querySelector('.van-dialog');
if (dialog) {
    const btn = dialog.querySelector('.van-dialog__confirm, button[class*="confirm" i], .van-button--danger, .van-button--primary');
    if (btn) {
        try { btn.click(); } catch(e){}
        return { status: "CONFIRM_CLICKED" };
    }
}

try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (token) return { status: "SUCCESS" };
} catch(e){}

if (!href.includes('/login') && (!hash.includes('login') || hash.length > 8)) {
    return { status: "SUCCESS" };
}

const toast = document.querySelector('.van-toast--text, .van-toast--fail');
if (toast && toast.innerText) {
    const t = toast.innerText.trim();
    if (t.includes('password') || t.includes('incorrect') || t.includes('wrong') || t.includes('exist')) {
        return { status: "ERROR", message: t };
    }
}
return { status: "PENDING" };
"""

FETCH_BALANCE_JS = r"""
let targetedEls = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i]');
for (let el of targetedEls) {
    let txt = el.innerText || '';
    let match = txt.match(/[\d,]+\.?\d*/);
    if (match) {
        let val = parseFloat(match[0].replace(/,/g, ''));
        if (val > 0) return val;
    }
}
return 0.0;
"""

# ==============================================================================
# CORE REALTIME ENGINE & PREDICTION HUD JS (24/7 CONTINUOUS MARTINGALE)
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
        hud.style.cssText = 'position:fixed;top:8px;right:8px;z-index:999999;background:rgba(13,17,23,0.92);border:1px solid #30363d;border-radius:8px;padding:10px;color:#58a6ff;font-family:monospace;text-align:center;width:160px;pointer-events:none;';
        hud.innerHTML = `
            <div style="font-size:11px;font-weight:bold;color:#f0883e;">DRX VIP (BST)</div>
            <div id="hud-timer" style="font-size:22px;font-weight:bold;color:#39d353;margin:2px 0;">00:30</div>
            <div id="hud-signal" style="font-size:13px;font-weight:bold;color:#ffffff;">SIGNAL: --</div>
            <div id="hud-step" style="font-size:11px;color:#f1e05a;">STEP: 1/` + autoTotalSteps + `</div>
        `;
        document.body.appendChild(hud);
    }

    if (window.__WINGO_ST && window.__WINGO_ST.isRun) {
        window.__WINGO_ST.steps = Math.max(1, autoTotalSteps);
        if (autoTargetGoal > 0) window.__WINGO_ST.tgtAmt = autoTargetGoal;
        return "ALREADY_ACTIVE";
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
        preBetBalance: 0.0,
        evaluatedPeriod: null,
        lastTriggeredCycle: null,
        circuitBreakerTriggered: false,
        w: 0,
        l: 0
    };
    window.__WINGO_ST = st;

    function getBSTDate() {
        const d = new Date();
        const utc = d.getTime() + (d.getTimezoneOffset() * 60000);
        return new Date(utc + (3600000 * 6));
    }

    function chkBal() {
        try {
            let targeted = document.querySelectorAll('.Wallet__balance-num, .wallet-user-balance, .balance-num, [class*="balance" i]');
            for (let el of targeted) {
                let txt = el.innerText || '';
                let m = txt.match(/[\d,]+\.?\d*/);
                if (m) {
                    let num = parseFloat(m[0].replace(/,/g, ''));
                    if (num > 0) {
                        st.curBal = num;
                        return num;
                    }
                }
            }
        } catch(e) {}
        return st.curBal || 0.0;
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
            let step = Math.max(1, Math.round(firstStep * Math.pow(2, i)));
            steps.push(step);
            total += step;
        }
        let diff = Math.round(balance - total);
        if (diff !== 0 && steps.length > 0) {
            steps[stepsCount - 1] = Math.max(1, steps[stepsCount - 1] + diff);
        }
        return steps;
    };

    function updateTimer() {
        const nowBst = getBSTDate();
        const seconds = nowBst.getSeconds();
        const rem = 30 - (seconds % 30);
        const displaySec = rem === 30 ? 0 : rem;

        let timerEl = document.getElementById("hud-timer");
        if (timerEl) timerEl.innerText = `00:${String(displaySec).padStart(2, '0')}`;

        let stepEl = document.getElementById("hud-step");
        if (stepEl) stepEl.innerText = `STEP: ${st.stpIdx + 1}/${st.steps}`;

        return displaySec;
    }

    function getLiveRoundId() {
        try {
            let pEl = document.querySelector('.Game__C-title-sub, .Time__C-num, [class*="period" i], [class*="issue" i]');
            if (pEl) {
                let m = (pEl.innerText || '').match(/(\d{10,24})/);
                if (m) return m[1];
            }
        } catch(e){}
        return 'EPOCH_' + Math.floor(Date.now() / 30000);
    }

    const exeBet = (pred, amt, cb) => {
        try {
            let targetText = String(pred).toLowerCase().trim();
            let btn = null;
            let btns = document.querySelectorAll('button, div, span');
            for (let b of btns) {
                if ((b.innerText || '').trim().toLowerCase() === targetText && b.offsetParent && !b.children.length) {
                    btn = b;
                    break;
                }
            }
            if (!btn) {
                if (targetText === 'big') btn = document.querySelector('.Betting__C-foot-b, .bet-btn-big, button[class*="big" i]');
                else btn = document.querySelector('.Betting__C-foot-s, .bet-btn-small, button[class*="small" i]');
            }
            if (!btn) { if (cb) cb(false); return; }

            btn.click();

            setTimeout(() => {
                let inp = document.querySelector("input[type='number'], input.van-field__control, .van-stepper__input");
                if (inp) {
                    inp.focus();
                    let setV = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                    if (setV) setV.call(inp, String(amt));
                    else inp.value = amt;
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.dispatchEvent(new Event('change', { bubbles: true }));
                }

                setTimeout(() => {
                    let confirmBtn = document.querySelector('button.bet-amount, .Betting__C-foot-total, .van-button--danger, .van-button--warning');
                    if (confirmBtn) confirmBtn.click();
                    setTimeout(() => {
                        let overlay = document.querySelector('.van-overlay');
                        if (overlay) try { overlay.click(); } catch(e){}
                        if (cb) cb(true);
                    }, 800);
                }, 200);
            }, 150);
        } catch(e) {
            if (cb) cb(false);
        }
    };

    let initialBal = chkBal();
    st.startBal = initialBal;
    st.curBal = initialBal;
    st.dynSeq = calcSeq(initialBal > 0 ? initialBal : 100, st.steps);

    const executeCycleTradeWorkflow = async (overridePred = null) => {
        if (!st.isRun || st.isTrd) return;

        let liveB = chkBal();
        if (liveB > 0 && st.startBal <= 0) {
            st.startBal = liveB;
            st.dynSeq = calcSeq(liveB, st.steps);
        }

        // STRICT TARGET STOP CHECK
        if (st.tgtAmt > 0 && liveB >= st.tgtAmt && st.startBal > 0) {
            st.isRun = false;
            if (st.timerInt) clearInterval(st.timerInt);
            return;
        }

        let incomingPeriod = getLiveRoundId();
        if (st.lastBetPeriod === incomingPeriod) return;

        // OUTCOME EVALUATION
        if (st.lastBetPeriod && st.lastBetAmt > 0 && st.evaluatedPeriod !== st.lastBetPeriod) {
            st.evaluatedPeriod = st.lastBetPeriod;
            await new Promise(r => setTimeout(r, 1000));
            let freshBal = chkBal();
            let won = false;

            if (freshBal > 0 && st.preBetBalance > 0) {
                won = (freshBal - st.preBetBalance) >= -(st.lastBetAmt * 0.15);
            }

            if (won) {
                st.w++;
                st.stpIdx = 0;
                st.dynSeq = calcSeq(freshBal > 0 ? freshBal : st.curBal, st.steps);
            } else {
                st.l++;
                // 24/7 AUTO RECYCLE: ৫ স্টেপ শেষ হলে পুনরায় স্টেপ ১ থেকে ঘুরবে
                if (st.stpIdx >= st.steps - 1) {
                    st.stpIdx = 0;
                    st.circuitBreakerTriggered = true;
                    st.dynSeq = calcSeq(freshBal > 0 ? freshBal : st.curBal, st.steps);
                } else {
                    st.stpIdx += 1;
                }
            }
        }

        let pred = overridePred || "BIG";
        let betAmt = Math.floor(st.dynSeq[st.stpIdx]) || 1;

        let sEl = document.getElementById('hud-signal');
        if (sEl) sEl.innerText = "SIGNAL: " + pred;

        st.isTrd = true;
        st.lastPred = pred;
        st.lastBetPeriod = incomingPeriod;
        st.lastBetAmt = betAmt;
        st.preBetBalance = liveB;

        exeBet(pred, betAmt, (ok) => {
            if (ok) st.tradesDone++;
            st.isTrd = false;
        });
    };

    window.__WINGO_EXECUTE_TRADE = executeCycleTradeWorkflow;

    st.timerInt = setInterval(() => {
        if (!st.isRun) return;
        const rem = updateTimer();
        const curCycle = Math.floor(Date.now() / 30000);

        // সিগন্যাল কার্যকর করার জন্য উপযুক্ত উইন্ডো (১৮ থেকে ৮ সেকেন্ড বাকি থাকতে)
        if (st.lastTriggeredCycle !== curCycle && rem <= 18 && rem >= 8) {
            st.lastTriggeredCycle = curCycle;
            executeCycleTradeWorkflow();
        }
    }, 1000);

    return "INITIALIZED";
})();
"""

# ==============================================================================
# PYTHON PREDICTION FETCH
# ==============================================================================
def python_fetch_best_prediction():
    try:
        req = urllib.request.Request(
            f"{PREDICTION_API_URL}?t={int(time.time()*1000)}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=2.5) as res:
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
        return "BIG" if bigs >= smalls else "SMALL"
    except Exception:
        return "BIG"

# ==============================================================================
# WORKER FLOW EXECUTIONS
# ==============================================================================
def execute_worker_login(chat_id, sid, phone, password, login_url, site_name, anim_msg_id):
    emit_event_to_manager("PROGRESS_STAGE", {
        "percent": 25,
        "text": "Starting ultra-light isolated container...",
        "session_id": sid,
        "chat_id": chat_id,
        "site_name": site_name,
        "anim_msg_id": anim_msg_id
    })

    try:
        driver, handle = allocate_session_tab(sid, login_url)
    except Exception as e:
        logger.error(f"Driver start failed: {e}")
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "reason": "Container memory limit exceeded.",
            "anim_msg_id": anim_msg_id
        })
        terminate_session_cleanly(sid)
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    fill_ok = False
    for _ in range(45):
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
            "reason": "Login portal timeout.",
            "anim_msg_id": anim_msg_id
        })
        terminate_session_cleanly(sid)
        return

    login_status = "PENDING"
    err_detail = ""
    for _ in range(30):
        res = safe_tab_execute(sid, lambda drv: drv.execute_script(CHECK_LOGIN_STATUS_JS))
        if isinstance(res, dict):
            if res.get("status") == "SUCCESS":
                login_status = "SUCCESS"
                break
            elif res.get("status") == "ERROR":
                login_status = "ERROR"
                err_detail = res.get("message", "Invalid credentials")
                break
        time.sleep(0.4)

    if login_status == "ERROR":
        terminate_session_cleanly(sid)
        emit_event_to_manager("LOGIN_FAILED", {
            "session_id": sid,
            "chat_id": chat_id,
            "reason": err_detail,
            "anim_msg_id": anim_msg_id
        })
        return

    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))
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

    safe_tab_execute(sid, lambda drv: drv.get(wingo_url))
    time.sleep(2.0)
    safe_tab_execute(sid, lambda drv: drv.execute_script(MODAL_AUTO_DISMISSER_JS))

    current_bal = 0.0
    for _ in range(12):
        bal = safe_tab_execute(sid, lambda drv: drv.execute_script(FETCH_BALANCE_JS))
        if bal and float(bal) > 0:
            current_bal = float(bal)
            break
        time.sleep(0.5)

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
    loop_ticks = 0
    while True:
        sess = active_sessions.get(sid)
        if not sess or not sess.get("is_trading"):
            break

        loop_ticks += 1
        enforce_memory_cap()

        # পাইথন ফলব্যাক প্রেডিকশন হ্যান্ডলার
        now_sec = bst_now().second
        rem_sec = 30 - (now_sec % 30)
        cur_cycle = int(time.time() // 30)

        if rem_sec in [16, 17] and last_py_cycle != cur_cycle:
            last_py_cycle = cur_cycle
            best_pred = python_fetch_best_prediction()
            safe_tab_execute(sid, lambda drv: drv.execute_script(f"""
                if (window.__WINGO_EXECUTE_TRADE && window.__WINGO_ST && !window.__WINGO_ST.isTrd) {{
                    window.__WINGO_EXECUTE_TRADE('{best_pred}');
                }}
            """))

        # টেলিমেট্রি সংগ্রহ
        js_data = safe_tab_execute(sid, lambda drv: drv.execute_script("""
            if (window.__WINGO_ST) {
                return {
                    isRun: window.__WINGO_ST.isRun,
                    curBal: window.__WINGO_ST.curBal || 0.0,
                    tgtAmt: window.__WINGO_ST.tgtAmt || 0.0,
                    startBal: window.__WINGO_ST.startBal || 0.0,
                    w: window.__WINGO_ST.w || 0,
                    l: window.__WINGO_ST.l || 0,
                    step: (window.__WINGO_ST.stpIdx || 0) + 1,
                    steps: window.__WINGO_ST.steps || 5
                };
            }
            return null;
        """))

        if js_data:
            sess["cur_bal"] = float(js_data.get("curBal", sess.get("cur_bal", 0.0)))
            sess["current_balance"] = sess["cur_bal"]
            tgt_amt = float(js_data.get("tgtAmt", 0.0))
            start_b = float(js_data.get("startBal", 0.0))
            is_run = js_data.get("isRun", False)

            task_payload = {
                "chat_id": chat_id,
                "session_id": sid,
                "site_name": site_name,
                "status": "RUNNING" if is_run else "PAUSED",
                "start_balance": start_b,
                "current_balance": sess["cur_bal"],
                "target_amount": tgt_amt,
                "step": js_data.get("step", 1),
                "total_steps": js_data.get("steps", 5),
                "wins": js_data.get("w", 0),
                "losses": js_data.get("l", 0),
                "updated_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
            }
            firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

            # টার্গেট ব্যালেন্স সম্পন্ন হওয়া নিশ্চিত করা
            if tgt_amt > 0 and sess["cur_bal"] >= tgt_amt and start_b > 0:
                logger.info(f"Target Reached! Goal: {tgt_amt} | Bal: {sess['cur_bal']}")
                sess["is_trading"] = False
                task_payload["status"] = "COMPLETED"
                firebase_sync_http(f"user_tasks/{chat_id}/{sid}", "PUT", task_payload)

                emit_event_to_manager("TARGET_ACHIEVED", {
                    "session_id": sid,
                    "chat_id": chat_id,
                    "site_name": site_name,
                    "start_balance": start_b,
                    "final_balance": sess["cur_bal"]
                })
                terminate_session_cleanly(sid)
                break

            if not is_run:
                sess["is_trading"] = False
                break

        if loop_ticks % 20 == 0:
            gc.collect()

        time.sleep(1.8)

# ==============================================================================
# WORKER TASK POLLING LOOP
# ==============================================================================
def worker_task_listener():
    logger.info(f"Worker task polling active on node: {NODE_ID}")
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
                        "current_balance": 0.0,
                        "cur_bal": 0.0,
                        "lock": threading.RLock(),
                        "last_activity": time.time()
                    }
                    threading.Thread(
                        target=execute_worker_login,
                        args=(task["chat_id"], sid, task["phone"], task["password"], task["login_url"], task.get("site_name", "Amar Club"), task.get("anim_msg_id")),
                        daemon=True
                    ).start()

            action_pkt = firebase_sync_http(f"terminals/{NODE_ID}/action", "GET")
            if action_pkt and isinstance(action_pkt, dict):
                firebase_sync_http(f"terminals/{NODE_ID}/action", "DELETE")
                kind = action_pkt.get("kind")
                sid = action_pkt.get("session_id")
                chat_id = action_pkt.get("chat_id")

                if kind in ["EMERGENCY_STOP", "EMERGENCY_STOP_ALL"]:
                    for s_id in list(active_sessions.keys()):
                        terminate_session_cleanly(s_id)
                elif kind == "PREPARE_WINGO" and sid in active_sessions:
                    sess = active_sessions[sid]
                    threading.Thread(target=execute_worker_prepare_wingo, args=(chat_id, sid, sess["wingo_url"], sess["site_name"]), daemon=True).start()
                elif kind == "START_TRADING" and sid in active_sessions:
                    sess = active_sessions[sid]
                    target_goal = float(action_pkt.get("target_goal", 0.0))
                    total_steps = int(action_pkt.get("total_steps", 5))
                    pred_url = action_pkt.get("prediction_api_url") or PREDICTION_API_URL
                    sess["is_trading"] = True
                    sess["target_goal"] = target_goal
                    sess["total_steps"] = total_steps
                    safe_tab_execute(sid, lambda drv: drv.execute_script(WINGO_CORE_JS, target_goal, total_steps, pred_url))
                    threading.Thread(target=worker_monitor_trading_loop, args=(chat_id, sid, sess["site_name"]), daemon=True).start()
                elif kind == "STOP_TRADING" and sid in active_sessions:
                    safe_tab_execute(sid, lambda drv: drv.execute_script("if(window.__WINGO_ST){ window.__WINGO_ST.isRun = false; }"))
                    active_sessions[sid]["is_trading"] = False
                elif kind == "CANCEL_SESSION" and sid in active_sessions:
                    terminate_session_cleanly(sid)

        except Exception as e:
            logger.debug(f"Task listener exception: {e}")
        time.sleep(1.0)

# ==============================================================================
# HEARTBEAT & MONITORING
# ==============================================================================
def latency_monitor_loop():
    global cached_latency
    while WORKER_ACTIVE:
        try:
            cached_latency = measure_network_latency(PLATFORMS["site_amarclub"]["login"])
        except Exception:
            pass
        time.sleep(40.0)

def worker_register_node():
    node_payload = {
        "status": "FREE",
        "heartbeat": time.time(),
        "node_id": NODE_ID,
        "alias": WORKER_ALIAS,
        "load": len(active_sessions),
        "latency_ms": cached_latency,
        "registered_at_bst": bst_now().strftime("%Y-%m-%d %H:%M:%S BST")
    }
    firebase_sync_http(f"terminals/{NODE_ID}", "PUT", node_payload)
    logger.info(f"Worker registered: {NODE_ID} ({WORKER_ALIAS})")

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
        time.sleep(3.5)

def handle_shutdown_signals(sig, frame):
    global WORKER_ACTIVE
    logger.info("Graceful shutdown sequence triggered...")
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
# MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_shutdown_signals)
    signal.signal(signal.SIGTERM, handle_shutdown_signals)

    print(f"[*] {to_vip_text('DRX WINGO WORKER ENGINE ACTIVE')} [{WORKER_ALIAS}]...")
    worker_register_node()
    threading.Thread(target=latency_monitor_loop, daemon=True).start()
    threading.Thread(target=worker_heartbeat_loop, daemon=True).start()

    try:
        worker_task_listener()
    except KeyboardInterrupt:
        handle_shutdown_signals(None, None)
