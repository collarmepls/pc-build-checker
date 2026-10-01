# PC Build Checker

![lines of code](https://img.shields.io/badge/lines%20of%20code-87-blue?style=for-the-badge)
![py](https://img.shields.io/badge/py-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)

A small CLI tool that checks whether the parts in a PC build actually work together before you buy them. You describe your build in a JSON file, and it tells you if anything wont fit, wont mount, or wont get enough power.

## What it checks

| Check | What it looks at |
|---|---|
| CPU socket | CPU and motherboard sockets match |
| Memory type | RAM type (DDR4/DDR5) matches the board |
| Memory slots | Number of sticks fits the boards slots |
| Memory capacity | Total RAM is within the boards max |
| M.2 slots | Number of M.2 drives fits the board |
| Form factor | Case supports the motherboard size |
| Cooler socket | Cooler can mount on the CPU socket |
| GPU clearance | Graphics card fits in the case |
| Cooler clearance | Cooler height fits in the case |
| Cooling capacity | Cooler is rated for the CPUs TDP (with 10% headroom) |
| Power budget | PSU covers estimated draw (with 20% headroom) |

Each check prints as a pass ✓, warning !, or fail ✗, followed by a summary.

## Install

You need [Python 3](https://www.python.org/downloads/) installed.

```
git clone https://github.com/collarmepls/pc-build-checker.git
cd pc-build-checker
```

Or just download `pc_build_checker.py` and `example.json` into the same folder.

## Usage

```
python pc_build_checker.py example.json
```

On Windows, use `py` instead of `python` if needed.

For JSON output:

```
python pc_build_checker.py example.json --json
```

The script exits with code `1` if any check fails, so it can be used in scripts or CI.

## Example output

```
✓ CPU socket         match (AM5)
✓ Memory type        DDR5
✓ Memory slots       2 of 4 slots
✓ Memory capacity    32GB (max 192)
✓ M.2 slots          1 of 3 slots
✓ Form factor        supported (ATX)
✓ Cooler socket      supported (AM5)
✓ GPU clearance      267/365mm
✓ Cooler clearance   155mm, case fits 165mm
✓ Cooling capacity   245W cooler / 120W CPU
✓ Power budget       750W PSU, ~463W draw, 556W recommended

11 passed, 0 warnings, 0 failed
meow!
```

## Making your own build

Copy `example.json` and swap in your parts specs. These are usually listed on the manufacturers product page: socket, form factor, GPU length, cooler height, case clearances, and power draw.

## License

MIT
