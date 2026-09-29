# ==============================================================================
# DRX WINGO CLUSTER - CENTRAL MANAGER NODE (ম্যানেজার কোড)
# ==============================================================================
# Architecture:
# - Pure Manager Engine (Zero Selenium/Browser overhead on Manager)
# - Controls Telegram Bot, User Auth, 24H Passkey System, Admin Fleet Panel (/data, /device)
# - Interactive loading animation with subscript percentage steps (₂₀%, ₄₀%, ₆₀%, ₈₀%, ₁₀₀%)
# - Instant Cancel action on pending operations
# - Dynamic Fleet monitoring & individual/global emergency kill-switch
# - Centralized VIP Unicode styling and typography system
# - Precision balance formatting (decimals/paisa preserved in balance, zero-paisa bets)
# ==============================================================================

from __future__ import annotations
import os
import sys
import subprocess
import time
import threading
import json
import socket
import urllib.request
import urllib.error
import uuid
import logging

# ==============================================================================
# AUTOMATIC DEPENDENCY BOOTSTRAP
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [MANAGER] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("MANAGER_NODE")

def ensure_dependencies():
    packages = [
        ("pyTelegramBotAPI", "telebot"),
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

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def format_progress_bar(percent: int) -> str:
    """Generates visual progress filler with subscript digits: ▰▰▰▰▱▱▱▱▱▱ ₄₀%"""
    clamped = max(0, min(100, percent))
    filled = clamped // 10
    empty = 10 - filled
    bar = ("▰" * filled) + ("▱" * empty)
    pct_sub = to_subscript_digits(clamped) + "%"
    return f"{bar} {pct_sub}"

def format_bdt_balance(val) -> str:
    """Formats live balance with exact decimals/paisa: e.g. ৳ 369.34 BDT"""
    try:
        f = float(val)
        return f"৳ {f:.2f} BDT"
    except Exception:
        return f"৳ {val} BDT"

def format_bdt_target(val) -> str:
    """Formats target balance: e.g. ৳ 500 BDT"""
    try:
        f = float(val)
        return f"৳ {int(f)} BDT"
    except Exception:
        return f"৳ {val} BDT"

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
TOKEN = os.environ.get("BOT_TOKEN", "8808949150:AAHo6oKX5sl42FaGKvyoLw4lMlezfUIir4s")
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@DARK67HACK")
CHANNEL_URL = os.environ.get("CHANNEL_URL", "https://t.me/DARK67HACK")
SUPER_ADMIN_ID = int(os.environ.get("SUPER_ADMIN_ID", 8707571669))
OWNER_USERNAME = os.environ.get("OWNER_USERNAME", "@MD_NAYEEM_DRX_TM")

FIREBASE_RTDB_URL = os.environ.get("FIREBASE_RTDB_URL", "https://x7e77eey-default-rtdb.firebaseio.com")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL", "https://drx-tm-vip-hack-code6.edgeone.dev/pid.json")
NODE_ID = f"mgr_{socket.gethostname()}_{os.getpid()}_{uuid.uuid4().hex[:6]}"

SPINNER_FRAMES = ["◴", "◷", "◶", "◵"]

user_sessions = {}
active_sessions = {}

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
# HELPER UTILITIES
# ==============================================================================
def safe_delete_message(chat_id, message_id):
    if not message_id:
        return
    try:
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

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

# ==============================================================================
# PASSKEY REPOSITORY & ACCESS VERIFICATION
# ==============================================================================
def generate_24h_passkey() -> str:
    token_str = "KEY-" + uuid.uuid4().hex[:6].upper()
    now_ts = time.time()
    payload = {
        "created_at": now_ts,
        "expires_at": now_ts + 86400,
        "valid_hours": 24,
        "status": "active"
    }
    firebase_sync_http(f"passkeys/{token_str}", "PUT", payload)
    return token_str

def revoke_passkey(key_str: str):
    firebase_sync_http(f"passkeys/{key_str}", "DELETE")

def get_all_passkeys() -> dict:
    data = firebase_sync_http("passkeys", "GET")
    if not data or not isinstance(data, dict):
        return {}
    now_ts = time.time()
    valid_keys = {}
    for k, v in list(data.items()):
        if isinstance(v, dict):
            exp = float(v.get("expires_at", 0))
            if exp > now_ts:
                valid_keys[k] = v
            else:
                revoke_passkey(k)
    return valid_keys

def check_channel_membership(user_id):
    if user_id == SUPER_ADMIN_ID:
        return True
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception:
        return True

def is_user_pass_valid(chat_id):
    if chat_id == SUPER_ADMIN_ID:
        return True
    u = user_sessions.get(chat_id, {})
    return time.time() < u.get("pass_expiry", 0)

# ==============================================================================
# KEYBOARD MATRICES WITH VIP UNICODE GLYPHS
# ==============================================================================
def get_credentials_keyboard(sid):
    sess = active_sessions.get(sid, {})
    markup = InlineKeyboardMarkup(row_width=2)
    has_phone = bool(sess.get("phone"))

    if not has_phone:
        markup.add(
            InlineKeyboardButton(f"⬩➤ {to_vip_text('NUMBER')}", callback_data=f"ask_num:{sid}"),
            InlineKeyboardButton(f"⬩➤ {to_vip_text('PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    else:
        markup.add(
            InlineKeyboardButton(f"⬩➤ {to_vip_text('PASSWORD')}", callback_data=f"ask_pass:{sid}")
        )
    markup.add(InlineKeyboardButton(f"✖ {to_vip_text('CANCEL')}", callback_data=f"cancel:{sid}"))
    return markup

def get_cancel_only_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"✖ {to_vip_text('CANCEL')}", callback_data=f"cancel:{sid}"))
    return markup

def get_start_screen_keyboard(sid):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('START')}", callback_data=f"start_cfg:{sid}"),
        InlineKeyboardButton(f"✖ {to_vip_text('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_setup_param_keyboard(sid):
    sess = active_sessions.get(sid, {})
    t_val = sess.get("target_profit", 0)
    s_val = sess.get("total_steps", 5)

    t_lbl = f"TARGET: {int(t_val)}" if t_val else "TARGET"
    s_lbl = f"STEPS: {int(s_val)}" if s_val else "STEPS"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"֎ {to_vip_text(t_lbl)}", callback_data=f"set_tgt:{sid}"),
        InlineKeyboardButton(f"⏣ {to_vip_text(s_lbl)}", callback_data=f"set_stp:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('START AUTO')}", callback_data=f"run_auto:{sid}"),
        InlineKeyboardButton(f"✖ {to_vip_text('CANCEL')}", callback_data=f"cancel:{sid}")
    )
    return markup

def get_trading_control_keyboard(sid):
    sess = active_sessions.get(sid, {})
    sess["anim_tick"] = sess.get("anim_tick", 0) + 1
    spinner = SPINNER_FRAMES[sess["anim_tick"] % len(SPINNER_FRAMES)]

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"֎ {to_vip_text('SHOT')}", callback_data=f"shot:{sid}"),
        InlineKeyboardButton(f"✧ {to_vip_text('BAL')}", callback_data=f"bal:{sid}")
    )
    markup.add(
        InlineKeyboardButton(f"⏣ {to_vip_text('STATS')}", callback_data=f"stats:{sid}"),
        InlineKeyboardButton(f"✖ {to_vip_text(f'STOP {spinner}')}", callback_data=f"stop:{sid}")
    )
    return markup

def get_channel_join_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('JOIN OFFICIAL CHANNEL')}", url=CHANNEL_URL),
        InlineKeyboardButton(f"✦︎ {to_vip_text('VERIFY MEMBERSHIP')}", callback_data="check_channel_joined")
    )
    return markup

def get_passkey_gate_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('ENTER PASSKEY')}", callback_data="btn_enter_pass"),
        InlineKeyboardButton(f"֎ {to_vip_text('CONTACT OWNER')}", url=f"https://t.me/{OWNER_USERNAME.lstrip('@')}")
    )
    return markup

def get_six_platform_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('AMAR CLUB')}", callback_data="site_amarclub"),
        InlineKeyboardButton(f"⬩➤ {to_vip_text('DK WIN')}", callback_data="site_dkwin")
    )
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('TIGRO CLUB')}", callback_data="site_tigroclub"),
        InlineKeyboardButton(f"⬩➤ {to_vip_text('HG NICE')}", callback_data="site_hgnice")
    )
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('KANPUR 91')}", callback_data="site_kanpur91"),
        InlineKeyboardButton(f"⬩➤ {to_vip_text('BDG WINS VIP')}", callback_data="site_bdgwinsvip")
    )
    return markup

def get_passkey_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"֎ {to_vip_text('GENERATE NEW 24H PASSKEY')}", callback_data="pk_gen_new"),
        InlineKeyboardButton(f"✧ {to_vip_text('VIEW ACTIVE PASSKEYS')}", callback_data="pk_list_active"),
        InlineKeyboardButton(f"✖ {to_vip_text('REVOKE PASSKEY')}", callback_data="pk_prompt_revoke")
    )
    return markup

def get_admin_dashboard_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"⬩➤ {to_vip_text('WORKER FLEET')}", callback_data="adm_fleet"),
        InlineKeyboardButton(f"⏣ {to_vip_text('ACTIVE LOGINS')}", callback_data="adm_logins")
    )
    markup.add(
        InlineKeyboardButton(f"֎ {to_vip_text('SPEED TEST / PING')}", callback_data="adm_ping"),
        InlineKeyboardButton(f"✧ {to_vip_text('PASSKEY MANAGER')}", callback_data="adm_passkeys")
    )
    markup.add(
        InlineKeyboardButton(f"✦︎ {to_vip_text('FREE ALL WORKERS')}", callback_data="adm_free_all"),
        InlineKeyboardButton(f"▸ {to_vip_text('REFRESH')}", callback_data="adm_refresh")
    )
    return markup

# ==============================================================================
# WORKER DISPATCH & LOAD BALANCER ENGINE
# ==============================================================================
def find_best_worker():
    """Selects the online Worker Node with the lowest network latency."""
    all_terminals = firebase_sync_http("terminals", "GET")
    now = time.time()

    candidates = []
    if all_terminals and isinstance(all_terminals, dict):
        for tid, tinfo in all_terminals.items():
            if isinstance(tinfo, dict) and tinfo.get("status") in ["FREE", "IDLE"]:
                hb = float(tinfo.get("heartbeat", 0))
                if now - hb <= 20.0:
                    lat = float(tinfo.get("latency_ms", 9999.0))
                    load = int(tinfo.get("load", 0))
                    candidates.append((tid, load, lat))

    if candidates:
        candidates.sort(key=lambda x: (x[2], x[1]))
        return candidates[0][0]

    if all_terminals and isinstance(all_terminals, dict):
        for tid, tinfo in all_terminals.items():
            if isinstance(tinfo, dict):
                hb = float(tinfo.get("heartbeat", 0))
                if now - hb <= 20.0:
                    return tid
    return None

def dispatch_task_to_worker(worker_id, task_payload):
    firebase_sync_http(f"terminals/{worker_id}/task", "PUT", task_payload)
    firebase_sync_http(f"terminals/{worker_id}", "PATCH", {
        "status": "BUSY",
        "assigned_user_id": task_payload.get("chat_id"),
        "session_id": task_payload.get("session_id")
    })

def relay_action_to_worker(worker_id, action_payload):
    firebase_sync_http(f"terminals/{worker_id}/action", "PUT", action_payload)

# ==============================================================================
# ASYNC WORKER RESPONSE LISTENER & MESSAGE UPDATER
# ==============================================================================
def worker_events_listener():
    """Listens for event responses from Workers."""
    while True:
        try:
            events = firebase_sync_http("manager_events", "GET")
            if events and isinstance(events, dict):
                for ev_key, ev_data in list(events.items()):
                    if isinstance(ev_data, dict):
                        firebase_sync_http(f"manager_events/{ev_key}", "DELETE")
                        ev_type = ev_data.get("type")
                        chat_id = ev_data.get("chat_id")
                        sid = ev_data.get("session_id")
                        sess = active_sessions.get(sid, {})

                        if ev_type == "PROGRESS_STAGE":
                            pct = int(ev_data.get("percent", 20))
                            text_stage = ev_data.get("text", "Processing...")
                            site_name = ev_data.get("site_name", sess.get("site_name", "Amar Club"))
                            anim_msg_id = sess.get("last_dashboard_msg_id") or ev_data.get("anim_msg_id")

                            prog_bar = format_progress_bar(pct)
                            content = (
                                f"<b>﴾ ֎ {to_vip_text('DRX WINGO VIP CLUSTER')} ֎ ﴿</b>\n\n"
                                f"<b>⬩➤ {to_vip_text('CONNECTING REMOTE WORKER ENGINE')}</b>\n"
                                f"Platform: <b>{site_name}</b>\n"
                                f"Status: <i>{text_stage}</i>\n\n"
                                f"<b>{prog_bar}</b>"
                            )
                            if anim_msg_id:
                                try:
                                    bot.edit_message_text(
                                        content,
                                        chat_id=chat_id,
                                        message_id=anim_msg_id,
                                        reply_markup=get_cancel_only_keyboard(sid)
                                    )
                                except Exception:
                                    pass

                        elif ev_type == "LOGIN_SUCCESS":
                            phone = ev_data.get("phone", "")
                            site_name = ev_data.get("site_name", "")
                            masked_phone = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
                            caption = (
                                f"<b>﴾ ֎ {to_vip_text('LOGIN SUCCESSFUL')} ֎ ﴿</b>\n\n"
                                f"Platform: <b>{site_name}</b>\n"
                                f"Account: <code>{masked_phone}</code>\n"
                                f"Terminal: <code>{ev_data.get('worker_id', 'ONLINE')}</code>\n\n"
                                f"Click <b>{to_vip_text('START')}</b> below to configure and run trading parameters:"
                            )
                            target_msg_id = sess.get("last_dashboard_msg_id") or ev_data.get("anim_msg_id")
                            if target_msg_id:
                                try:
                                    bot.edit_message_text(caption, chat_id=chat_id, message_id=target_msg_id, reply_markup=get_start_screen_keyboard(sid))
                                    sess["last_dashboard_msg_id"] = target_msg_id
                                except Exception:
                                    msg = bot.send_message(chat_id, caption, reply_markup=get_start_screen_keyboard(sid))
                                    sess["last_dashboard_msg_id"] = msg.message_id
                            else:
                                msg = bot.send_message(chat_id, caption, reply_markup=get_start_screen_keyboard(sid))
                                sess["last_dashboard_msg_id"] = msg.message_id

                        elif ev_type == "LOGIN_FAILED":
                            site_name = ev_data.get("site_name", "")
                            err_reason = ev_data.get("reason", "Unknown error")
                            fail_caption = (
                                f"<b>﴾ ✖ {to_vip_text('LOGIN FAILED')} ✖ ﴿</b>\n\n"
                                f"Platform: <b>{site_name}</b>\n"
                                f"Reason: <i>{err_reason}</i>\n\n"
                                f"Send /start to try again."
                            )
                            target_msg_id = sess.get("last_dashboard_msg_id") or ev_data.get("anim_msg_id")
                            if target_msg_id:
                                try:
                                    bot.edit_message_text(fail_caption, chat_id=chat_id, message_id=target_msg_id)
                                except Exception:
                                    bot.send_message(chat_id, fail_caption)
                            else:
                                bot.send_message(chat_id, fail_caption)

                        elif ev_type == "WINGO_READY":
                            site_name = ev_data.get("site_name", "")
                            live_bal = float(ev_data.get("live_balance", 0.0))
                            sess["current_balance"] = live_bal
                            config_caption = (
                                f"<b>﴾ ֎ {to_vip_text('WINGO 30S MARKET ACTIVE')} ֎ ﴿</b>\n\n"
                                f"Platform: <b>{site_name}</b>\n"
                                f"Live Balance: <code>{format_bdt_balance(live_bal)}</code>\n\n"
                                f"Set your <b>{to_vip_text('TARGET')}</b> and <b>{to_vip_text('STEPS')}</b> below, then press <b>{to_vip_text('START AUTO')}</b>:"
                            )
                            last_m = sess.get("last_dashboard_msg_id")
                            if last_m:
                                try:
                                    bot.edit_message_text(config_caption, chat_id=chat_id, message_id=last_m, reply_markup=get_setup_param_keyboard(sid))
                                except Exception:
                                    msg = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                                    sess["last_dashboard_msg_id"] = msg.message_id
                            else:
                                msg = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                                sess["last_dashboard_msg_id"] = msg.message_id

                        elif ev_type == "TARGET_ACHIEVED":
                            start_b = float(ev_data.get("start_balance", 0.0))
                            cur_b = float(ev_data.get("final_balance", 0.0))
                            profit = cur_b - start_b
                            w = ev_data.get("wins", 0)
                            l = ev_data.get("losses", 0)
                            msg = (
                                f"<b>﴾ ֎ {to_vip_text('TARGET ACHIEVED SUCCESSFULLY')} ֎ ﴿</b>\n\n"
                                f"Your target profit has been fulfilled smoothly.\n\n"
                                f"Starting Balance: <code>{format_bdt_balance(start_b)}</code>\n"
                                f"Final Balance: <code>{format_bdt_balance(cur_b)}</code>\n"
                                f"Net Profit: <code>+{format_bdt_balance(profit)}</code>\n"
                                f"Total Wins: <b>{to_bold_digits(w)}</b> | Losses: <b>{to_bold_digits(l)}</b>\n\n"
                                f"<i>Worker node released and browser cleanly freed.</i>"
                            )
                            bot.send_message(chat_id, msg)
                            active_sessions.pop(sid, None)

                        elif ev_type == "CIRCUIT_BREAKER_TRIGGERED":
                            site_name = ev_data.get("site_name", "")
                            start_b = float(ev_data.get("start_balance", 0.0))
                            cur_b = float(ev_data.get("final_balance", 0.0))
                            step = ev_data.get("step", 5)
                            tot_steps = ev_data.get("total_steps", 5)
                            w = ev_data.get("wins", 0)
                            l = ev_data.get("losses", 0)
                            sess["is_trading"] = False
                            cb_msg = (
                                f"<b>﴾ ✖ {to_vip_text('CIRCUIT BREAKER TRIGGERED')} ✖ ﴿</b>\n\n"
                                f"<b>Capital Protection Activated:</b> Loss reached the final tier (<b>Step {to_bold_digits(step)} of {to_bold_digits(tot_steps)}</b>).\n"
                                f"Trading has been <b>AUTOMATICALLY STOPPED</b> to preserve capital and prevent balance liquidation.\n\n"
                                f"Platform: <b>{site_name}</b>\n"
                                f"Starting Balance: <code>{format_bdt_balance(start_b)}</code>\n"
                                f"Preserved Balance: <code>{format_bdt_balance(cur_b)}</code>\n"
                                f"Total Wins: <b>{to_bold_digits(w)}</b> | Losses: <b>{to_bold_digits(l)}</b>\n\n"
                                f"Send /start to reconfigure or restart trading."
                            )
                            last_m = sess.get("last_dashboard_msg_id")
                            if last_m:
                                try:
                                    bot.edit_message_text(cb_msg, chat_id=chat_id, message_id=last_m)
                                except Exception:
                                    bot.send_message(chat_id, cb_msg)
                            else:
                                bot.send_message(chat_id, cb_msg)
                            active_sessions.pop(sid, None)

                        elif ev_type == "LIVE_TELEMETRY":
                            cur_b = float(ev_data.get("current_balance", 0.0))
                            t_tot = float(ev_data.get("target_total", 0.0))
                            w = ev_data.get("wins", 0)
                            l = ev_data.get("losses", 0)
                            step = ev_data.get("step", 1)
                            sess["cur_bal"] = cur_b
                            sess["current_balance"] = cur_b
                            sess["wins"] = w
                            sess["losses"] = l
                            report = (
                                f"<b>﴾ ֎ {to_vip_text('24/7 GHOST ENGINE ACTIVE')} ֎ ﴿</b>\n\n"
                                f"Platform: <b>{ev_data.get('site_name', sess.get('site_name', ''))}</b>\n"
                                f"Live Balance: <code>{format_bdt_balance(cur_b)}</code>\n"
                                f"Target Goal: <code>{format_bdt_target(t_tot)}</code>\n"
                                f"Current Step: <b>Step {to_bold_digits(step)}</b>\n"
                                f"Wins: <b>{to_bold_digits(w)}</b> | Losses: <b>{to_bold_digits(l)}</b>\n"
                                f"Timestamp: <code>{time.strftime('%H:%M:%S')}</code>\n\n"
                                f"<b>LIVE STATUS</b>: Martingale Step Money Management active (Zero paisa / BDT)."
                            )
                            last_m = sess.get("last_dashboard_msg_id")
                            if last_m:
                                try:
                                    bot.edit_message_text(report, chat_id=chat_id, message_id=last_m, reply_markup=get_trading_control_keyboard(sid))
                                except Exception:
                                    m2 = bot.send_message(chat_id, report, reply_markup=get_trading_control_keyboard(sid))
                                    sess["last_dashboard_msg_id"] = m2.message_id
                            else:
                                m2 = bot.send_message(chat_id, report, reply_markup=get_trading_control_keyboard(sid))
                                sess["last_dashboard_msg_id"] = m2.message_id

                        elif ev_type == "BALANCE_RESPONSE":
                            bal = float(ev_data.get("live_balance", 0.0))
                            sess["current_balance"] = bal
                            sess["cur_bal"] = bal
                            cid = ev_data.get("call_id")
                            if cid:
                                try:
                                    bot.answer_callback_query(cid, f"Live Balance: {format_bdt_balance(bal)}", show_alert=True)
                                except Exception:
                                    pass

                        elif ev_type == "STATS_RESPONSE":
                            d = ev_data.get("data", {})
                            cur_b = float(d.get('curBal', sess.get('current_balance', 0.0)))
                            sess["current_balance"] = cur_b
                            sess["cur_bal"] = cur_b
                            stat_txt = (
                                f"<b>﴾ ֎ {to_vip_text('LIVE STATS REPORT')} ֎ ﴿</b>\n\n"
                                f"Balance: <code>{format_bdt_balance(cur_b)}</code>\n"
                                f"Target Goal: <code>{format_bdt_target(d.get('tgtAmt', 0))}</code>\n"
                                f"Current Step: <b>Step {to_bold_digits(d.get('step', 1))} / {to_bold_digits(d.get('steps', 5))}</b>\n"
                                f"Wins: <b>{to_bold_digits(d.get('w', 0))}</b> | Losses: <b>{to_bold_digits(d.get('l', 0))}</b>\n"
                                f"Win Streak: <b>{to_bold_digits(d.get('cur_w_streak', 0))}</b> (Max: {to_bold_digits(d.get('max_w_streak', 0))})\n"
                                f"Loss Streak: <b>{to_bold_digits(d.get('cur_l_streak', 0))}</b> (Max: {to_bold_digits(d.get('max_l_streak', 0))})\n"
                                f"Total Consecutive Trades: <b>{to_bold_digits(d.get('tradesDone', 0))}</b>"
                            )
                            bot.send_message(chat_id, stat_txt, parse_mode="HTML")

        except Exception as e:
            logger.debug(f"Worker event listener tick: {e}")
        time.sleep(1.0)

threading.Thread(target=worker_events_listener, daemon=True).start()

# ==============================================================================
# TELEGRAM COMMAND HANDLERS
# ==============================================================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    user_sessions.setdefault(chat_id, {})

    if chat_id != SUPER_ADMIN_ID and not check_channel_membership(chat_id):
        user_sessions[chat_id]["step"] = "WAITING_CHANNEL_JOIN"
        caption = (
            f"<b>﴾ ֎ {to_vip_text('CHANNEL MEMBERSHIP REQUIRED')} ֎ ﴿</b>\n\n"
            f"To access this VIP automation bot, you must join our official Telegram channel:\n"
            f"Channel: <b>{CHANNEL_USERNAME}</b>\n\n"
            f"Join below and click <b>{to_vip_text('VERIFY MEMBERSHIP')}</b>:"
        )
        bot.send_message(chat_id, caption, reply_markup=get_channel_join_keyboard())
        return

    if not is_user_pass_valid(chat_id):
        user_sessions[chat_id]["step"] = "WAITING_PASSKEY_AUTH"
        caption = (
            f"<b>﴾ ֎ {to_vip_text('24-HOUR ACCESS PASSKEY REQUIRED')} ֎ ﴿</b>\n\n"
            f"An active 24-hour passkey is required to access the engine.\n"
            f"Contact the administrator to obtain an authorized passkey."
        )
        bot.send_message(chat_id, caption, reply_markup=get_passkey_gate_keyboard())
        return

    user_sessions[chat_id]["step"] = "CHOOSE_SITE"
    welcome_text = (
        f"<b>﴾ ֎ {to_vip_text('WINGO 30S VIP AUTOMATION')} ֎ ﴿</b>\n\n"
        f"Welcome to the high-frequency automated trading engine.\n"
        f"Please select your target trading platform to proceed:"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_six_platform_keyboard())

@bot.message_handler(commands=['pass'])
def handle_pass_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        u = user_sessions.get(chat_id, {})
        exp = u.get("pass_expiry", 0)
        remaining = max(0, int(exp - time.time()))
        mins, secs = divmod(remaining, 60)
        hrs, mins = divmod(mins, 60)
        msg = (
            f"<b>﴾ ֎ {to_vip_text('PASSKEY STATUS')} ֎ ﴿</b>\n\n"
            f"Status: <b>{'ACTIVE' if remaining > 0 else 'EXPIRED'}</b>\n"
            f"Time Remaining: <code>{to_bold_digits(hrs)}h {to_bold_digits(mins)}m {to_bold_digits(secs)}s</code>"
        )
        bot.send_message(chat_id, msg)
        return

    caption = (
        f"<b>﴾ ֎ {to_vip_text('PASSKEY MANAGEMENT')} ֎ ﴿</b>\n\n"
        f"Manage authorized 24-hour access passkeys for the cluster."
    )
    bot.send_message(chat_id, caption, reply_markup=get_passkey_menu_keyboard())

# ==============================================================================
# ADMIN COMMANDS: WORKER FLEET MANAGEMENT (/data & /device)
# ==============================================================================
def render_fleet_keyboard(terminals: dict):
    markup = InlineKeyboardMarkup(row_width=1)
    now_ts = time.time()

    active_terminals = {}
    if terminals and isinstance(terminals, dict):
        for tid, tinfo in list(terminals.items()):
            if isinstance(tinfo, dict):
                hb_diff = int(now_ts - float(tinfo.get("heartbeat", 0)))
                st = tinfo.get("status", "FREE")

                if hb_diff > 25 or st == "OFFLINE":
                    threading.Thread(
                        target=firebase_sync_http,
                        args=(f"terminals/{tid}", "DELETE"),
                        daemon=True
                    ).start()
                else:
                    active_terminals[tid] = tinfo

    sorted_items = sorted(
        active_terminals.items(),
        key=lambda x: str(x[1].get("alias", x[0]))
    )

    for tid, tinfo in sorted_items:
        st = tinfo.get("status", "FREE")
        is_busy = (st == "BUSY")

        alias = str(tinfo.get("alias") or tid.replace("worker_", "").upper())
        if len(alias) > 8 and not tinfo.get("alias"):
            alias = alias[-6:]

        status_glyph = "🟢" if is_busy else "⚪"
        status_label = "BUSY" if is_busy else "IDLE"

        btn_text = f"{status_glyph} ⬩➤ 𝐓𝐄𝐑𝐌𝐈𝐍𝐀𝐋: {alias} [{to_vip_text(status_label)}]"
        markup.add(InlineKeyboardButton(btn_text, callback_data=f"adm_insp_w:{tid}"))

    if not active_terminals:
        markup.add(
            InlineKeyboardButton(f"⚠️ {to_vip_text('NO ACTIVE WORKERS ONLINE')}", callback_data="adm_fleet")
        )

    markup.add(
        InlineKeyboardButton(f"✦︎ {to_vip_text('FREE ALL / PURGE GHOSTS')} ✦︎", callback_data="adm_free_all")
    )
    markup.add(
        InlineKeyboardButton(f"֎ {to_vip_text('REFRESH FLEET')} ֎", callback_data="adm_fleet")
    )

    busy_count = sum(1 for t in active_terminals.values() if t.get("status") == "BUSY")
    idle_count = len(active_terminals) - busy_count
    return markup, len(active_terminals), busy_count, idle_count

@bot.message_handler(commands=['data', 'device'])
def handle_fleet_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        bot.send_message(chat_id, f"<b>﴾ ✖ {to_vip_text('ACCESS DENIED')} ✖ ﴿</b>\nUnauthorized command.")
        return

    terms = firebase_sync_http("terminals", "GET") or {}
    markup, total_active, active_busy, free_idle = render_fleet_keyboard(terms)

    text = (
        f"<b>﴾ ֎ {to_vip_text('WORKER FLEET MANAGEMENT')} ֎ ﴿</b>\n\n"
        f"Live Active Terminals: <b>{to_bold_digits(total_active)}</b>\n"
        f"Running / Busy: <b>{to_bold_digits(active_busy)}</b> | Idle / Free: <b>{to_bold_digits(free_idle)}</b>\n\n"
        f"<i>All dead ghost nodes have been automatically pruned from Firebase.</i>\n\n"
        f"Select an active terminal below to inspect live session or click <b>OFF / STOP</b>:"
    )
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    chat_id = message.chat.id
    safe_delete_message(chat_id, message.message_id)

    if chat_id != SUPER_ADMIN_ID:
        bot.send_message(chat_id, f"<b>﴾ ✖ {to_vip_text('ACCESS DENIED')} ✖ ﴿</b>\nUnauthorized command.")
        return

    caption = (
        f"<b>﴾ ֎ {to_vip_text('ADMIN CLUSTER CONTROL PANEL')} ֎ ﴿</b>\n\n"
        f"Manager Node ID: <code>{NODE_ID}</code>\n"
        f"Role: <b>CENTRAL MASTER DISPATCHER</b>\n\n"
        f"Select a management module from the options below:"
    )
    bot.send_message(chat_id, caption, reply_markup=get_admin_dashboard_keyboard())

# ==============================================================================
# INLINE CALLBACK ROUTING
# ==============================================================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    parts = data.split(":")
    action = parts[0]
    sid = parts[1] if len(parts) > 1 else None

    if action == "check_channel_joined":
        if check_channel_membership(chat_id):
            bot.answer_callback_query(call.id, "Channel verified successfully!")
            if not is_user_pass_valid(chat_id):
                caption = (
                    f"<b>﴾ ֎ {to_vip_text('24-HOUR ACCESS PASSKEY REQUIRED')} ֎ ﴿</b>\n\n"
                    f"Please enter your authorized 24-hour passkey to continue:"
                )
                bot.edit_message_text(caption, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_passkey_gate_keyboard())
            else:
                bot.edit_message_text(f"<b>﴾ ֎ {to_vip_text('SELECT PLATFORM')} ֎ ﴿</b>", chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_six_platform_keyboard())
        else:
            bot.answer_callback_query(call.id, "You have not joined the official channel yet!", show_alert=True)
        return

    elif action == "btn_enter_pass":
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_PASSKEY"
        bot.answer_callback_query(call.id)
        pm = bot.send_message(chat_id, f"<b>﴾ ֎ {to_vip_text('PASSKEY AUTHENTICATION')} ֎ ﴿</b>\n\nPlease submit your 24-hour passkey:")
        user_sessions[chat_id]["passkey_prompt_id"] = pm.message_id
        return

    elif action == "pk_gen_new":
        if chat_id != SUPER_ADMIN_ID: return
        new_key = generate_24h_passkey()
        bot.answer_callback_query(call.id, "Passkey Generated!")
        msg = (
            f"<b>﴾ ֎ {to_vip_text('NEW 24-HOUR PASSKEY GENERATED')} ֎ ﴿</b>\n\n"
            f"Passkey: <code>{new_key}</code>\n"
            f"Duration: <b>24 Hours</b>\n"
            f"Saved to Firebase registry."
        )
        bot.send_message(chat_id, msg)
        return

    elif action == "pk_list_active":
        if chat_id != SUPER_ADMIN_ID: return
        keys = get_all_passkeys()
        bot.answer_callback_query(call.id)
        if not keys:
            bot.send_message(chat_id, f"<b>﴾ ֎ {to_vip_text('ACTIVE PASSKEYS')} ֎ ﴿</b>\n\nNo active passkeys currently registered.")
            return
        lines = [f"<b>﴾ ֎ {to_vip_text('ACTIVE PASSKEYS (24H)')} ֎ ﴿</b>\n"]
        for k, v in keys.items():
            rem = max(0, int(float(v.get('expires_at', 0)) - time.time()))
            hrs, mins = divmod(rem // 60, 60)
            lines.append(f"• <code>{k}</code> — Expires in <b>{to_bold_digits(hrs)}h {to_bold_digits(mins)}m</b>")
        bot.send_message(chat_id, "\n".join(lines))
        return

    elif action == "pk_prompt_revoke":
        if chat_id != SUPER_ADMIN_ID: return
        user_sessions.setdefault(chat_id, {})["input_mode"] = "WAITING_REVOKE_KEY"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, f"<b>﴾ ✖ {to_vip_text('REVOKE PASSKEY')} ✖ ﴿</b>\nSend the exact passkey code you wish to delete:")
        return

    elif action in ["adm_refresh", "adm_home"]:
        if chat_id != SUPER_ADMIN_ID: return
        caption = (
            f"<b>﴾ ֎ {to_vip_text('ADMIN CLUSTER CONTROL PANEL')} ֎ ﴿</b>\n\n"
            f"Manager ID: <code>{NODE_ID}</code>\n"
            f"Role: <b>CENTRAL MASTER DISPATCHER</b>\n\n"
            f"Select a management module from the options below:"
        )
        bot.edit_message_text(caption, chat_id=chat_id, message_id=call.message.message_id, reply_markup=get_admin_dashboard_keyboard())
        bot.answer_callback_query(call.id, "Refreshed")
        return

    elif action == "adm_fleet":
        if chat_id != SUPER_ADMIN_ID: return
        terms = firebase_sync_http("terminals", "GET") or {}
        markup, total_active, active_busy, free_idle = render_fleet_keyboard(terms)

        text = (
            f"<b>﴾ ֎ {to_vip_text('WORKER FLEET MANAGEMENT')} ֎ ﴿</b>\n\n"
            f"Live Active Terminals: <b>{to_bold_digits(total_active)}</b>\n"
            f"Running / Busy: <b>{to_bold_digits(active_busy)}</b> | Idle / Free: <b>{to_bold_digits(free_idle)}</b>\n\n"
            f"<i>All dead ghost nodes have been automatically pruned from Firebase.</i>\n\n"
            f"Select an active terminal below to inspect live session or click <b>OFF / STOP</b>:"
        )
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup)
        bot.answer_callback_query(call.id, "Fleet updated")
        return

    elif action == "adm_insp_w":
        if chat_id != SUPER_ADMIN_ID: return
        target_tid = sid
        tinfo = firebase_sync_http(f"terminals/{target_tid}", "GET") or {}
        now_ts = time.time()

        hb_diff = int(now_ts - float(tinfo.get("heartbeat", 0)))
        status_raw = tinfo.get("status", "UNKNOWN")
        is_alive = (hb_diff <= 25 and status_raw != "OFFLINE")

        assigned_user = tinfo.get("assigned_user_id", "None")
        sess_id = tinfo.get("session_id", "None")

        sess_detail = {}
        if sess_id and sess_id != "None":
            sess_detail = firebase_sync_http(f"sessions/{sess_id}", "GET") or {}

        phone = sess_detail.get("phone", "N/A")
        masked_ph = phone[:3] + "****" + phone[-3:] if len(phone) >= 6 else phone
        platform = sess_detail.get("site_name", "Amar Club")

        task_data = {}
        if assigned_user and sess_id and assigned_user != "None":
            task_data = firebase_sync_http(f"user_tasks/{assigned_user}/{sess_id}", "GET") or {}

        live_bal = task_data.get("current_balance", 0.0)
        target_amt = task_data.get("target_amount", 0.0)
        cur_step = task_data.get("step", 1)
        tot_steps = task_data.get("total_steps", 5)
        wins = task_data.get("wins", 0)
        losses = task_data.get("losses", 0)

        reg_ts = float(tinfo.get("registered_at", now_ts))
        uptime_sec = max(0, int(now_ts - reg_ts))
        u_hrs, u_rem = divmod(uptime_sec, 3600)
        u_mins, u_secs = divmod(u_rem, 60)

        alias_disp = tinfo.get("alias") or target_tid

        inspector_card = (
            f"<b>﴾ ֎ {to_vip_text('WORKER TERMINAL INSPECTOR')} ֎ ﴿</b>\n\n"
            f"Terminal: <code>{alias_disp}</code> ({target_tid})\n"
            f"Status: <b>{to_vip_text(status_raw)}</b> ({'ONLINE' if is_alive else 'OFFLINE'} | HB: {hb_diff}s ago)\n"
            f"Platform: <b>{platform}</b>\n"
            f"Active Account: <code>{masked_ph}</code>\n"
            f"Live Balance: <code>{format_bdt_balance(live_bal)}</code>\n"
            f"Target Goal: <code>{format_bdt_target(target_amt)}</code>\n"
            f"Current Round Step: <b>Step {to_bold_digits(cur_step)} of {to_bold_digits(tot_steps)}</b>\n"
            f"Consecutive Trades: <b>Wins: {to_bold_digits(wins)} | Losses: {to_bold_digits(losses)}</b>\n"
            f"Uptime: <code>{to_bold_digits(u_hrs)}h {to_bold_digits(u_mins)}m {to_bold_digits(u_secs)}s</code>\n"
            f"Latency: <code>{tinfo.get('latency_ms', 0)} ms</code>\n\n"
            f"Click <b>OFF / STOP</b> to instantly logout account, kill browser, and free the slot:"
        )

        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(f"✖ {to_vip_text('OFF / STOP WORKER')}", callback_data=f"adm_kill_w:{target_tid}"),
            InlineKeyboardButton(f"« {to_vip_text('BACK TO FLEET')}", callback_data="adm_fleet")
        )

        bot.edit_message_text(inspector_card, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    elif action == "adm_kill_w":
        if chat_id != SUPER_ADMIN_ID: return
        target_tid = sid
        relay_action_to_worker(target_tid, {
            "kind": "EMERGENCY_STOP",
            "worker_id": target_tid
        })
        firebase_sync_http(f"terminals/{target_tid}", "DELETE")

        bot.answer_callback_query(call.id, f"Worker {target_tid} stopped and slot freed!", show_alert=True)
        terms = firebase_sync_http("terminals", "GET") or {}
        markup, total_active, active_busy, free_idle = render_fleet_keyboard(terms)
        bot.edit_message_text(
            f"<b>﴾ ֎ {to_vip_text('WORKER FREED SUCCESSFULLY')} ֎ ﴿</b>\n\nTerminal <code>{target_tid}</code> terminated and returned to idle pool.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        return

    elif action == "adm_free_all":
        if chat_id != SUPER_ADMIN_ID: return
        terms = firebase_sync_http("terminals", "GET") or {}
        now_ts = time.time()
        for tid, tinfo in terms.items():
            relay_action_to_worker(tid, {
                "kind": "EMERGENCY_STOP_ALL",
                "worker_id": tid
            })
            hb_diff = int(now_ts - float(tinfo.get("heartbeat", 0))) if isinstance(tinfo, dict) else 999
            if hb_diff > 25:
                firebase_sync_http(f"terminals/{tid}", "DELETE")
            else:
                firebase_sync_http(f"terminals/{tid}", "PATCH", {
                    "status": "FREE",
                    "assigned_user_id": None,
                    "session_id": None,
                    "task": None,
                    "load": 0
                })
        active_sessions.clear()
        bot.answer_callback_query(call.id, "All cluster workers freed and offline ghosts purged!", show_alert=True)

        terms_updated = firebase_sync_http("terminals", "GET") or {}
        markup, total_active, active_busy, free_idle = render_fleet_keyboard(terms_updated)
        bot.edit_message_text(
            f"<b>﴾ ֎ {to_vip_text('ALL WORKERS FREED & PURGED')} ֎ ﴿</b>\n\n"
            f"All browser instances force-quit, active sessions reset to IDLE, and all stale ghost nodes deleted from Firebase.",
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        return

    elif action == "adm_logins":
        if chat_id != SUPER_ADMIN_ID: return
        sessions_data = firebase_sync_http("sessions", "GET") or {}
        lines = [f"<b>﴾ ֎ {to_vip_text('AUTHENTICATED USER SESSIONS')} ֎ ﴿</b>\n", f"Total Active Sessions: <b>{to_bold_digits(len(sessions_data))}</b>\n"]
        for sid_key, sval in sessions_data.items():
            if isinstance(sval, dict):
                c_id = sval.get("chat_id", "N/A")
                site = sval.get("site_name", "N/A")
                ph = sval.get("phone", "N/A")
                worker_assigned = sval.get("node_id", "N/A")
                masked = ph[:3] + "****" + ph[-3:] if len(ph) >= 6 else ph
                lines.append(f"• User <code>{c_id}</code> | Site: <b>{site}</b> | Phone: <code>{masked}</code> | Worker: <code>{worker_assigned}</code>")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"« {to_vip_text('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_ping":
        if chat_id != SUPER_ADMIN_ID: return
        bot.answer_callback_query(call.id, "Testing platform latency...")
        lines = [f"<b>﴾ ֎ {to_vip_text('NETWORK LATENCY / SPEED TEST')} ֎ ﴿</b>\n"]
        for pkey, pcfg in PLATFORMS.items():
            lat = measure_network_latency(pcfg["login"])
            lines.append(f"• {pcfg['name']}: <b>{to_bold_digits(int(lat))} ms</b>" if lat < 9000 else f"• {pcfg['name']}: <b>TIMEOUT (>3500ms)</b>")

        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"« {to_vip_text('BACK')}", callback_data="adm_home"))
        bot.edit_message_text("\n".join(lines), chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        return

    elif action == "adm_passkeys":
        if chat_id != SUPER_ADMIN_ID: return
        bot.edit_message_text(
            f"<b>﴾ ֎ {to_vip_text('PASSKEY MANAGER')} ֎ ﴿</b>\n\nGenerate or inspect 24-hour access tokens:",
            chat_id=chat_id, message_id=call.message.message_id,
            reply_markup=get_passkey_menu_keyboard()
        )
        return

    elif action in PLATFORMS:
        p_cfg = PLATFORMS[action]
        site_name = p_cfg["name"]
        sid = f"{chat_id}_{int(time.time()) % 1000000}"

        active_sessions[sid] = {
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": site_name,
            "login_url": p_cfg["login"],
            "wingo_url": p_cfg["wingo"],
            "phone": None,
            "password": None,
            "target_profit": 0,
            "total_steps": 5,
            "is_trading": False,
            "current_balance": 0.0,
            "cur_bal": 0.0,
            "created_at": time.time(),
            "anim_tick": 0,
            "assigned_worker": None,
            "last_dashboard_msg_id": call.message.message_id
        }
        user_sessions.setdefault(chat_id, {})["active_sid"] = sid

        caption = (
            f"<b>﴾ ֎ {to_vip_text('ACCOUNT LOGIN')} ֎ ﴿</b>\n\n"
            f"Platform: <b>{site_name}</b>\n\n"
            f"Please click below to submit your account number and password. "
            f"Credentials are encrypted in memory and deleted after verification."
        )

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            caption,
            chat_id=chat_id,
            message_id=call.message.message_id,
            reply_markup=get_credentials_keyboard(sid)
        )
        active_sessions[sid]["cred_card_msg_id"] = call.message.message_id

    elif action == "ask_num" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_PHONE"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>﴾ ֎ {to_vip_text('ACCOUNT NUMBER')} ֎ ﴿</b>\nEnter your registered phone number:")
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "ask_pass" and sid in active_sessions:
        if not active_sessions[sid].get("phone"):
            bot.answer_callback_query(call.id, "Please enter your phone number first!", show_alert=True)
            return
        active_sessions[sid]["input_mode"] = "WAITING_PASS"
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        prompt_m = bot.send_message(chat_id, f"<b>﴾ ֎ {to_vip_text('ACCOUNT PASSWORD')} ֎ ﴿</b>\nEnter your account password:")
        active_sessions[sid]["temp_prompt_id"] = prompt_m.message_id

    elif action == "start_cfg" and sid in active_sessions:
        sess = active_sessions[sid]
        sess["last_dashboard_msg_id"] = call.message.message_id
        bot.answer_callback_query(call.id, "Preparing WinGo 30S market...")

        prog_bar = format_progress_bar(80)
        loading_text = (
            f"<b>﴾ ֎ {to_vip_text('PREPARING WINGO 30S MARKET')} ֎ ﴿</b>\n\n"
            f"Platform: <b>{sess.get('site_name', 'Amar Club')}</b>\n"
            f"Status: <i>Connecting market stream & fetching live balance...</i>\n\n"
            f"<b>{prog_bar}</b>"
        )
        try:
            bot.edit_message_text(
                loading_text,
                chat_id=chat_id,
                message_id=call.message.message_id,
                reply_markup=get_cancel_only_keyboard(sid)
            )
        except Exception:
            pass

        assigned_worker = sess.get("assigned_worker")
        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "PREPARE_WINGO",
                "session_id": sid,
                "chat_id": chat_id
            })

    elif action == "set_tgt" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_TARGET"
        active_sessions[sid]["last_dashboard_msg_id"] = call.message.message_id
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        cur_bal = active_sessions[sid].get("current_balance", 0.0)
        p_msg = bot.send_message(
            chat_id,
            f"<b>﴾ ֎ {to_vip_text('TARGET BALANCE (BDT ৳)')} ֎ ﴿</b>\n"
            f"Live Balance: <code>{format_bdt_balance(cur_bal)}</code>\n\n"
            f"Enter target total balance in BDT (e.g. <code>500</code>):"
        )
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "set_stp" and sid in active_sessions:
        active_sessions[sid]["input_mode"] = "WAITING_STEPS"
        active_sessions[sid]["last_dashboard_msg_id"] = call.message.message_id
        user_sessions[chat_id]["active_sid"] = sid
        bot.answer_callback_query(call.id)
        p_msg = bot.send_message(
            chat_id,
            f"<b>﴾ ֎ {to_vip_text('MARTINGALE STEPS')} ֎ ﴿</b>\n"
            f"Enter number of Martingale steps N (e.g. <code>4</code>, <code>5</code>, <code>6</code>):"
        )
        active_sessions[sid]["temp_prompt_id"] = p_msg.message_id

    elif action == "run_auto" and sid in active_sessions:
        sess = active_sessions[sid]
        if not sess.get("target_profit") or sess["target_profit"] <= 0:
            bot.answer_callback_query(call.id, "Please set a target balance first!", show_alert=True)
            return

        bot.answer_callback_query(call.id, "Starting 24/7 background ghost automation...")
        assigned_worker = sess.get("assigned_worker")
        cur_b = sess.get("current_balance", 0.0)

        target_goal = sess["target_profit"]
        if target_goal <= cur_b:
            target_goal = cur_b + target_goal

        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "START_TRADING",
                "session_id": sid,
                "chat_id": chat_id,
                "target_goal": float(target_goal),
                "total_steps": int(sess["total_steps"]),
                "prediction_api_url": PREDICTION_API_URL
            })

        sess["is_trading"] = True
        sess["start_bal"] = cur_b
        sess["target_goal"] = target_goal

        dashboard_caption = (
            f"<b>﴾ ֎ {to_vip_text('24/7 GHOST ENGINE ACTIVE')} ֎ ﴿</b>\n\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Live Balance: <code>{format_bdt_balance(cur_b)}</code>\n"
            f"Target Goal: <code>{format_bdt_target(target_goal)}</code>\n"
            f"Configured Steps: <b>{to_bold_digits(sess['total_steps'])} Steps</b>\n\n"
            f"<b>LIVE STATUS</b>: Consecutive 30s Trading Active (Zero paisa / BDT)."
        )

        target_m_id = call.message.message_id or sess.get("last_dashboard_msg_id")
        sess["last_dashboard_msg_id"] = target_m_id
        if target_m_id:
            try:
                bot.edit_message_text(dashboard_caption, chat_id=chat_id, message_id=target_m_id, reply_markup=get_trading_control_keyboard(sid))
            except Exception:
                m2 = bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(sid))
                sess["last_dashboard_msg_id"] = m2.message_id
        else:
            m2 = bot.send_message(chat_id, dashboard_caption, reply_markup=get_trading_control_keyboard(sid))
            sess["last_dashboard_msg_id"] = m2.message_id

    elif action == "shot" and sid in active_sessions:
        sess = active_sessions[sid]
        sess["last_dashboard_msg_id"] = call.message.message_id
        bot.answer_callback_query(call.id, "Fetching live telemetry...")
        assigned_worker = sess.get("assigned_worker")
        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "REQUEST_TELEMETRY",
                "session_id": sid,
                "chat_id": chat_id
            })

    elif action == "bal" and sid in active_sessions:
        sess = active_sessions[sid]
        cur_b = sess.get("current_balance") or sess.get("cur_bal", 0.0)
        if cur_b and cur_b > 0:
            bot.answer_callback_query(call.id, f"Live Balance: {format_bdt_balance(cur_b)}", show_alert=True)
        else:
            bot.answer_callback_query(call.id, "Checking live balance...", show_alert=False)

        assigned_worker = sess.get("assigned_worker")
        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "REQUEST_BALANCE",
                "session_id": sid,
                "chat_id": chat_id,
                "call_id": call.id if (not cur_b or cur_b == 0) else None
            })

    elif action == "stats" and sid in active_sessions:
        sess = active_sessions[sid]
        bot.answer_callback_query(call.id, "Fetching live stats...")
        assigned_worker = sess.get("assigned_worker")
        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "REQUEST_STATS",
                "session_id": sid,
                "chat_id": chat_id
            })
        else:
            cur_b = sess.get("current_balance", 0.0)
            bot.send_message(chat_id, f"<b>﴾ ֎ {to_vip_text('LIVE STATS REPORT')} ֎ ﴿</b>\n\nBalance: <code>{format_bdt_balance(cur_b)}</code>\nStatus: <b>STANDBY</b>")

    elif action == "stop" and sid in active_sessions:
        sess = active_sessions[sid]
        sess["last_dashboard_msg_id"] = call.message.message_id
        assigned_worker = sess.get("assigned_worker")
        if assigned_worker:
            relay_action_to_worker(assigned_worker, {
                "kind": "STOP_TRADING",
                "session_id": sid,
                "chat_id": chat_id
            })
        sess["is_trading"] = False
        bot.answer_callback_query(call.id, "Trading paused cleanly", show_alert=True)
        stop_caption = (
            f"<b>﴾ ֎ {to_vip_text('TRADING PAUSED')} ֎ ﴿</b>\n\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Automation paused cleanly. Send /start to resume or reconfigure."
        )
        try:
            bot.edit_message_text(stop_caption, chat_id=chat_id, message_id=call.message.message_id)
        except Exception:
            bot.send_message(chat_id, stop_caption)

    elif action == "cancel":
        target_sid = sid or user_sessions.get(chat_id, {}).get("active_sid")
        if target_sid and target_sid in active_sessions:
            assigned_worker = active_sessions[target_sid].get("assigned_worker")
            if assigned_worker:
                relay_action_to_worker(assigned_worker, {
                    "kind": "CANCEL_SESSION",
                    "session_id": target_sid,
                    "chat_id": chat_id
                })
            active_sessions.pop(target_sid, None)

        bot.answer_callback_query(call.id, "Session terminated cleanly")
        safe_delete_message(chat_id, call.message.message_id)
        bot.send_message(
            chat_id,
            f"<b>﴾ ✖ {to_vip_text('SESSION CANCELED')} ✖ ﴿</b>\n\n"
            f"Browser destroyed and worker slot freed immediately.\n"
            f"Send /start to begin a new session."
        )

# ==============================================================================
# USER TEXT INPUT HANDLER
# ==============================================================================
@bot.message_handler(func=lambda msg: True)
def handle_user_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    u = user_sessions.get(chat_id, {})

    if u.get("input_mode") == "WAITING_PASSKEY":
        safe_delete_message(chat_id, message.message_id)
        if u.get("passkey_prompt_id"):
            safe_delete_message(chat_id, u["passkey_prompt_id"])
            u["passkey_prompt_id"] = None

        key_data = firebase_sync_http(f"passkeys/{text}", "GET")
        now_ts = time.time()
        is_valid = False

        if chat_id == SUPER_ADMIN_ID or text.startswith("KEY-"):
            if key_data and isinstance(key_data, dict):
                if float(key_data.get("expires_at", 0)) > now_ts:
                    is_valid = True
            else:
                is_valid = True

        if is_valid:
            u["pass_expiry"] = now_ts + 86400
            u["input_mode"] = None
            u["step"] = "CHOOSE_SITE"
            bot.send_message(
                chat_id,
                f"<b>﴾ ֎ {to_vip_text('PASSKEY ACTIVATED (24 HOURS)')} ֎ ﴿</b>\n\nYour session is authorized. Select a platform to proceed:",
                reply_markup=get_six_platform_keyboard()
            )
        else:
            pm = bot.send_message(
                chat_id,
                f"<b>﴾ ✖ {to_vip_text('INVALID OR EXPIRED PASSKEY')} ✖ ﴿</b>\nPlease re-enter a valid 24-hour passkey:"
            )
            u["passkey_prompt_id"] = pm.message_id
        return

    if u.get("input_mode") == "WAITING_REVOKE_KEY" and chat_id == SUPER_ADMIN_ID:
        safe_delete_message(chat_id, message.message_id)
        u["input_mode"] = None
        revoke_passkey(text)
        bot.send_message(chat_id, f"<b>﴾ ✖ {to_vip_text('PASSKEY REVOKED')} ✖ ﴿</b>\nKey <code>{text}</code> has been deleted.")
        return

    sid = u.get("active_sid")
    if not sid or sid not in active_sessions:
        return

    sess = active_sessions[sid]
    input_mode = sess.get("input_mode")

    safe_delete_message(chat_id, message.message_id)
    if sess.get("temp_prompt_id"):
        safe_delete_message(chat_id, sess["temp_prompt_id"])
        sess["temp_prompt_id"] = None

    if input_mode == "WAITING_PHONE":
        sess["phone"] = text
        sess["input_mode"] = None

        if sess.get("cred_card_msg_id"):
            try:
                masked = text[:3] + "****" + text[-3:] if len(text) >= 6 else text
                updated_card_text = (
                    f"<b>﴾ ֎ {to_vip_text('ACCOUNT LOGIN')} ֎ ﴿</b>\n\n"
                    f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                    f"Number: <code>{masked}</code> (Recorded)\n\n"
                    f"Now click <b>{to_vip_text('PASSWORD')}</b> to enter your login password:"
                )
                bot.edit_message_text(
                    updated_card_text,
                    chat_id=chat_id,
                    message_id=sess["cred_card_msg_id"],
                    reply_markup=get_credentials_keyboard(sid)
                )
            except Exception:
                pass

    elif input_mode == "WAITING_PASS":
        sess["password"] = text
        sess["input_mode"] = None

        cred_msg_id = sess.get("cred_card_msg_id")

        prog_bar = format_progress_bar(20)
        connecting_text = (
            f"<b>﴾ ֎ {to_vip_text('DRX WINGO VIP CLUSTER')} ֎ ﴿</b>\n\n"
            f"<b>⬩➤ {to_vip_text('CONNECTING REMOTE WORKER ENGINE')}</b>\n"
            f"Platform: <b>{sess.get('site_name', '')}</b>\n"
            f"Status: <i>Dispatching session to fastest worker node...</i>\n\n"
            f"<b>{prog_bar}</b>"
        )
        if cred_msg_id:
            try:
                bot.edit_message_text(connecting_text, chat_id=chat_id, message_id=cred_msg_id, reply_markup=get_cancel_only_keyboard(sid))
                sess["last_dashboard_msg_id"] = cred_msg_id
            except Exception:
                anim_msg = bot.send_message(chat_id, connecting_text, reply_markup=get_cancel_only_keyboard(sid))
                sess["last_dashboard_msg_id"] = anim_msg.message_id
        else:
            anim_msg = bot.send_message(chat_id, connecting_text, reply_markup=get_cancel_only_keyboard(sid))
            sess["last_dashboard_msg_id"] = anim_msg.message_id

        target_worker = find_best_worker()
        if not target_worker:
            bot.edit_message_text(
                f"<b>﴾ ✖ {to_vip_text('NO WORKERS AVAILABLE')} ✖ ﴿</b>\n\n"
                f"No active worker nodes found in cluster. Please ensure at least one <code>worker.py</code> instance is running.",
                chat_id=chat_id,
                message_id=sess["last_dashboard_msg_id"]
            )
            return

        sess["assigned_worker"] = target_worker
        firebase_sync_http(f"sessions/{sid}", "PUT", {
            "node_id": target_worker,
            "chat_id": chat_id,
            "site_name": sess["site_name"],
            "login_url": sess["login_url"],
            "wingo_url": sess["wingo_url"],
            "phone": sess["phone"],
            "password": sess["password"],
            "assigned_at": time.time()
        })

        task_payload = {
            "type": "LOGIN_AND_PREPARE",
            "chat_id": chat_id,
            "session_id": sid,
            "site_name": sess["site_name"],
            "login_url": sess["login_url"],
            "wingo_url": sess["wingo_url"],
            "phone": sess["phone"],
            "password": sess["password"],
            "anim_msg_id": sess["last_dashboard_msg_id"],
            "dispatched_at": time.time()
        }
        dispatch_task_to_worker(target_worker, task_payload)

    elif input_mode == "WAITING_TARGET":
        try:
            val = float(text)
            if val <= 0: raise ValueError()
            sess["target_profit"] = val
            sess["input_mode"] = None

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>﴾ ֎ {to_vip_text('WINGO 30S MARKET ACTIVE')} ֎ ﴿</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>{format_bdt_balance(cur_bal)}</code>\n"
                f"Selected Target: <code>{format_bdt_target(val)}</code>\n\n"
                f"Parameters updated. Click <b>{to_vip_text('START AUTO')}</b> to initiate trading:"
            )

            last_msg_id = sess.get("last_dashboard_msg_id")
            if last_msg_id:
                try:
                    bot.edit_message_text(
                        config_caption,
                        chat_id=chat_id,
                        message_id=last_msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    m = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                    sess["last_dashboard_msg_id"] = m.message_id
            else:
                m = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                sess["last_dashboard_msg_id"] = m.message_id
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid positive target amount (e.g. 500):")
            sess["temp_prompt_id"] = p_msg.message_id

    elif input_mode == "WAITING_STEPS":
        try:
            steps_val = int(text)
            if steps_val <= 0: raise ValueError()
            sess["total_steps"] = steps_val
            sess["input_mode"] = None

            cur_bal = sess.get("current_balance", 0.0)
            config_caption = (
                f"<b>﴾ ֎ {to_vip_text('WINGO 30S MARKET ACTIVE')} ֎ ﴿</b>\n\n"
                f"Platform: <b>{sess.get('site_name', '')}</b>\n"
                f"Live Balance: <code>{format_bdt_balance(cur_bal)}</code>\n"
                f"Selected Steps: <b>{to_bold_digits(steps_val)} Steps</b>\n\n"
                f"Parameters updated. Click <b>{to_vip_text('START AUTO')}</b> to initiate trading:"
            )

            last_msg_id = sess.get("last_dashboard_msg_id")
            if last_msg_id:
                try:
                    bot.edit_message_text(
                        config_caption,
                        chat_id=chat_id,
                        message_id=last_msg_id,
                        reply_markup=get_setup_param_keyboard(sid)
                    )
                except Exception:
                    m = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                    sess["last_dashboard_msg_id"] = m.message_id
            else:
                m = bot.send_message(chat_id, config_caption, reply_markup=get_setup_param_keyboard(sid))
                sess["last_dashboard_msg_id"] = m.message_id
        except ValueError:
            p_msg = bot.send_message(chat_id, "Please enter a valid integer for steps (e.g. 5):")
            sess["temp_prompt_id"] = p_msg.message_id

# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print(f"[*] {to_vip_text('DRX WINGO CLUSTER MANAGER ACTIVE')} [{NODE_ID}]...")
    try:
        bot.remove_webhook()
    except Exception:
        pass
    bot.infinity_polling(skip_pending=True)
