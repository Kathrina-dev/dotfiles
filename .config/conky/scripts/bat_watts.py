#!/usr/bin/env python3
import os

for bat in ["BAT0", "BAT1"]:
    p_path = f"/sys/class/power_supply/{bat}/power_now"
    if os.path.exists(p_path):
        try:
            with open(p_path) as f:
                w = float(f.read().strip()) / 1e6
                print(f"{w:.1f} W")
                exit()
        except Exception:
            pass
    c_path = f"/sys/class/power_supply/{bat}/current_now"
    v_path = f"/sys/class/power_supply/{bat}/voltage_now"
    if os.path.exists(c_path) and os.path.exists(v_path):
        try:
            with open(c_path) as fc, open(v_path) as fv:
                w = (float(fc.read().strip()) * float(fv.read().strip())) / 1e12
                print(f"{w:.1f} W")
                exit()
        except Exception:
            pass

print("0.0 W")