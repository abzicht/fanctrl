# Raspberry PI 3 Fan control

This script keeps your SBC healthy by regularly checking CPU temperature
and running an externally attached fan when necessary.

## Installation

```bash
$ apt install python3 python3-pip
```

Run `./install.sh`. This installs Python requirements and copies `fanctrl` to
`/usr/bin/`.

```bash
$ ./install.sh
```

### Optional
By running `./install_systemd.sh`, `fanctrl` is installed as `systemd` service
`fanctrl.service` under `lib/systemd/system/` to run after each system start.
Log is written to `/var/log/fanctrl.txt`.
```bash
$ ./install_systemd.sh
```

## Usage

When installed for running after system start, there is no need to run
`fanctrl` manually as temperature checks and fan spinning is performed
automatically.

To manually run the fan, call `fanctrl -f`:

```bash
# Run the fan, no matter the actual cpu temperature
$ fanctrl -f
```

Get more information with `fanctrl -h`:
```text
usage: fanctrl.py [-h] [-f [FORCE]] [-i [INTERVAL]] [-t [TEMPERATURE]]
                  [-p [PIN]] [-l [LOG]]

optional arguments:
  -h, --help            show this help message and exit
  -f [FORCE], --force [FORCE]
                        Force fan on for FORCE time (default: 15s), no matter
                        the temperature, and quit. Program does not enter
                        scheduling mode.
  -i [INTERVAL], --interval [INTERVAL]
                        Interval in which cpu temperature is checked. Min:
                        10s, Default: 30s
  -t [TEMPERATURE], --temperature [TEMPERATURE]
                        Temperature (in °C) at which the cooling function is
                        triggered. Default: 48°C
  -p [PIN], --pin [PIN]
                        Physical pin which triggers the fan (BCM mode).
                        Default: 17
  -l [LOG], --log [LOG]
                        The log file temperature changes are written to.
                        Called once per interval.
```

## Default values
* Default fan pin: 17 (BCM mode)
* Default temperature trigger: 48°C
* Default interval: 30 seconds
* Default fan timer in force mode: 15 seconds
