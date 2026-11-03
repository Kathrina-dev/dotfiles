#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import time

graph_id = sys.argv[1] if len(sys.argv) > 1 else "default"
raw_val = sys.argv[2] if len(sys.argv) > 2 else "0"
raw_max = sys.argv[3] if len(sys.argv) > 3 else "100"
accent_color = sys.argv[4] if len(sys.argv) > 4 else "#c44582"

HIST_FILE = f"/tmp/conky_graph_{graph_id}.txt"
MAX_SAMPLES = 30  # Fixed character width

BRAILLE_BARS = ["⡀", "⣀", "⣄", "⣤", "⣦", "⣶", "⣷", "⣿"]


def parse_float(val_str):
    try:
        clean = "".join(c for c in str(val_str) if c.isdigit() or c == ".")
        return float(clean) if clean else 0.0
    except ValueError:
        return 0.0


def get_default_iface():
    try:
        with open("/proc/net/route") as f:
            for line in f:
                fields = line.strip().split()
                if len(fields) >= 2 and fields[1] == "00000000":
                    return fields[0]
    except Exception:
        pass
    try:
        for dev in os.listdir("/sys/class/net"):
            if dev != "lo":
                return dev
    except Exception:
        pass
    return None


def get_net_kibs():
    iface = get_default_iface()
    if not iface:
        return 0.0, 0.0

    state_file = "/tmp/conky_net_raw_state.json"
    now = time.time()
    rx, tx = 0, 0

    try:
        with open(f"/sys/class/net/{iface}/statistics/rx_bytes") as f:
            rx = int(f.read().strip())
        with open(f"/sys/class/net/{iface}/statistics/tx_bytes") as f:
            tx = int(f.read().strip())
    except Exception:
        return 0.0, 0.0

    state = {}
    if os.path.exists(state_file):
        try:
            with open(state_file) as f:
                state = json.load(f)
        except Exception:
            pass

    prev_time = state.get("time", now - 1)
    dt = max(now - prev_time, 0.2)

    rx_kibs = max(0.0, (rx - state.get("rx", rx)) / dt / 1024.0)
    tx_kibs = max(0.0, (tx - state.get("tx", tx)) / dt / 1024.0)

    try:
        with open(state_file, "w") as f:
            json.dump({"time": now, "rx": rx, "tx": tx}, f)
    except Exception:
        pass

    return rx_kibs, tx_kibs


def get_cpu_proc_stat():
    state_file = "/tmp/conky_cpu_stat.json"
    try:
        with open("/proc/stat") as f:
            fields = [float(x) for x in f.readline().split()[1:]]
        idle = fields[3] + fields[4]
        total = sum(fields)

        state = {}
        if os.path.exists(state_file):
            try:
                with open(state_file) as f:
                    state = json.load(f)
            except Exception:
                pass

        prev_idle = state.get("idle", idle)
        prev_total = state.get("total", total)

        try:
            with open(state_file, "w") as f:
                json.dump({"idle": idle, "total": total}, f)
        except Exception:
            pass

        diff_total = total - prev_total
        diff_idle = idle - prev_idle

        if diff_total > 0:
            return max(0.0, min(100.0, ((diff_total - diff_idle) / diff_total) * 100.0))
    except Exception:
        pass
    return None


def get_gpu_usage():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
        )
        return float(out.decode().strip())
    except Exception:
        return 0.0


def get_bat_watts():
    for bat in ["BAT0", "BAT1"]:
        p_path = f"/sys/class/power_supply/{bat}/power_now"
        if os.path.exists(p_path):
            try:
                with open(p_path) as f:
                    return float(f.read().strip()) / 1e6
            except Exception:
                pass
        c_path = f"/sys/class/power_supply/{bat}/current_now"
        v_path = f"/sys/class/power_supply/{bat}/voltage_now"
        if os.path.exists(c_path) and os.path.exists(v_path):
            try:
                with open(c_path) as fc, open(v_path) as fv:
                    return (float(fc.read().strip()) * float(fv.read().strip())) / 1e12
            except Exception:
                pass
    return 0.0


def main():
    if graph_id == "cpu":
        val = get_cpu_proc_stat()
        if val is None:
            val = parse_float(raw_val)
        max_val = 100.0
    elif graph_id == "gpu":
        val = parse_float(raw_val)
        if val == 0.0:
            val = get_gpu_usage()
        max_val = 100.0
    elif graph_id == "bat":
        val = get_bat_watts()
        max_val = 30.0
    elif graph_id in ["net_down", "net_up"]:
        rx_kibs, tx_kibs = get_net_kibs()
        val = rx_kibs if graph_id == "net_down" else tx_kibs
        max_val = "auto"
    else:
        val = parse_float(raw_val)
        max_val = parse_float(raw_max) if raw_max != "auto" else "auto"

    history = []
    if os.path.exists(HIST_FILE):
        try:
            with open(HIST_FILE, "r") as f:
                history = [float(x) for x in f.read().strip().split(",") if x]
        except ValueError:
            history = []

    if len(history) < MAX_SAMPLES:
        history = [0.0] * (MAX_SAMPLES - len(history)) + history

    history.append(val)
    history = history[-MAX_SAMPLES:]

    try:
        with open(HIST_FILE, "w") as f:
            f.write(",".join(map(str, history)))
    except Exception:
        pass

    if max_val == "auto":
        ceiling = max(max(history), 10.0)
    else:
        ceiling = float(max_val) if float(max_val) > 0 else 100.0

    out = []
    for v in history:
        pct = min(max(v / ceiling, 0.0), 1.0)
        idx = int(pct * (len(BRAILLE_BARS) - 1))
        out.append(BRAILLE_BARS[idx])

    graph_str = "".join(out)
    print(f"${{color {accent_color}}}{graph_str}${{color}}")


if __name__ == "__main__":
    main()