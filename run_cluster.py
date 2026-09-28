#!/usr/bin/env python3
"""
✦︎ WINGO 30S CLUSTER LAUNCHER (run_cluster.py) ✦︎
Starts both manager.py (Telegram Bot Node) and worker.py (Selenium Execution Node) concurrently.
Maintains continuous lifecycle, auto-restarts on crash, and streams unified logs.
"""

import sys
import subprocess
import time
import os
import signal

print("=" * 65)
print("✦︎ WINGO 30S 2-NODE CLUSTER CONCURRENT RUNNER ✦︎")
print("Node 1: manager.py (Telegram Bot & Task Dispatcher)")
print("Node 2: worker.py  (Headless Browser & 512MB RAM Execution Core)")
print("=" * 65)

procs = []

def cleanup(sig=None, frame=None):
    print("\n✦︎ Shutting down cluster nodes...")
    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def start_process(script_name):
    print(f"⬩➤ Launching {script_name}...")
    return subprocess.Popen([sys.executable, script_name])

# Start Worker Node first so it registers in Firebase
worker_proc = start_process("worker.py")
procs.append(worker_proc)
time.sleep(2.0)

# Start Manager Node
manager_proc = start_process("manager.py")
procs.append(manager_proc)

print("\n✔ Both cluster nodes are ACTIVE.")
print("Press Ctrl+C to terminate both nodes cleanly.\n")

while True:
    try:
        # Check if worker died
        if worker_proc.poll() is not None:
            print("⚠ worker.py stopped! Auto-restarting in 3 seconds...")
            time.sleep(3)
            worker_proc = start_process("worker.py")
            procs[0] = worker_proc

        # Check if manager died
        if manager_proc.poll() is not None:
            print("⚠ manager.py stopped! Auto-restarting in 3 seconds...")
            time.sleep(3)
            manager_proc = start_process("manager.py")
            procs[1] = manager_proc

        time.sleep(5)
    except KeyboardInterrupt:
        cleanup()
