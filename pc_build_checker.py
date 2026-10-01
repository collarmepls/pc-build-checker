import json, sys
import argparse

colors = {"pass": "\033[32m", 'warn': "\033[33m", "fail": "\033[31m"}
icons = dict(pass_="✓", warn="!", fail="✗")


def show(out, use_json=False):
    if use_json:
        print(json.dumps([dict(rule=r, status=s, message=m) for s, r, m in out], indent=2))
        return

    for s, rule, msg in out:
        icon = icons.get(s) or icons["pass_"]
        print(colors[s] + icon + "\033[0m", rule.ljust(18), msg)

    tally = {}
    for s, _, _ in out:
        tally[s] = tally.get(s, 0) + 1
    print("\n%d passed, %d warnings, %d failed" % (tally.get("pass", 0), tally.get("warn", 0), tally.get("fail", 0)))
    print("meow!")


p = argparse.ArgumentParser(description="Check a PC build for part compatibility and power headroom.")
p.add_argument("build_file")
p.add_argument("--json", action="store_true", help="print results as JSON")
args = p.parse_args()

build = json.load(open(args.build_file, encoding="utf-8"))
cpu, mobo = build["processor"], build["motherboard"]
sticks = build['memory']
case = build["case"]

res = []

sock = cpu["socket"]
res.append(("pass", "CPU socket", "match (" + sock + ")") if sock == mobo["socket"]
           else ("fail", "CPU socket", "{} CPU on a {} board".format(sock, mobo["socket"])))

if sticks["memory_type"] != mobo["memory_type"]:
    res.append(("fail", "Memory type", f"board wants {mobo['memory_type']}, got {sticks['memory_type']}"))
else:
    res += [("pass", "Memory type", sticks["memory_type"])]

n = sticks["module_count"]
res.append(("pass" if n <= mobo["memory_slots"] else "fail", "Memory slots", f"{n} of {mobo['memory_slots']} slots"))

gb = n * sticks["module_size_gb"]
ok = gb <= mobo["max_memory_gb"]
res.append((ok and "pass" or "fail", "Memory capacity", "%sGB (max %s)" % (gb, mobo["max_memory_gb"])))

drives = build["storage"]
m2 = len([x for x in drives if x["interface"] == "m2"])
if m2 > mobo["m2_slots"]:
    res.append(("fail", "M.2 slots", f"{m2} drives, only {mobo['m2_slots']} slots"))
else:
    res.append(("pass", "M.2 slots", str(m2) + " of " + str(mobo["m2_slots"]) + " slots"))

for label, thing, allowed in (("Form factor", mobo["form_factor"], case["supported_form_factors"]),
                              ("Cooler socket", sock, build["cooler"]["supported_sockets"])):
    res.append(("pass", label, f"supported ({thing})") if thing in allowed else ("fail", label, thing + " not in " + ", ".join(allowed)))

gpu_len = build["graphics_card"]["length_mm"]
room = case["max_gpu_length_mm"]
res.append(("pass" if gpu_len <= room else "fail", "GPU clearance", f"{gpu_len}/{room}mm"))

cooler = build["cooler"]
if cooler["height_mm"] <= case["max_cooler_height_mm"]:
    res.append(("pass", "Cooler clearance", "{}mm, case fits {}mm".format(cooler["height_mm"], case["max_cooler_height_mm"])))
else:
    res.append(("fail", "Cooler clearance", "too tall by %dmm" % (cooler["height_mm"] - case["max_cooler_height_mm"])))

tdp, rated = cpu["thermal_design_power"], cooler["rated_tdp"]
verdict = "fail" if rated < tdp else ("warn" if rated < tdp * 1.1 else "pass")
res.append((verdict, "Cooling capacity", f"{rated}W cooler / {tdp}W CPU"))

watts = 50 + sum(part.get("power_draw", 0) for part in [cpu, mobo, sticks, build["graphics_card"], case, cooler, *drives])
psu = build["power_supply"]["wattage"]
want = round(watts * 1.2)

status = "pass"
if psu < want: status = "warn"
if psu < watts: status = "fail"
res.append((status, "Power budget", f"{psu}W PSU, ~{watts}W draw, {want}W recommended"))

show(res, args.json)
sys.exit(1 if any(r[0] == "fail" for r in res) else 0)
