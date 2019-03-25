# Raspberry PI 3: Fan control

This script keeps your SBC healthy by regularly checking cpu temperature
and running an externally attached fan when necessary.

## Installation

### Requirements
```bash
$ sudo apt install python3 python3-pip
$ pip install -r requirements.txt
```

### Installation without cron
Run `./install.sh` to install `fanctrl` only.

```bash
$ ./install.sh
```

### Installation with cron
By running `./install.sh cron`, `fanctrl` is installed and added as a cronjob under `etc/cron.d/fanctrl`.

```bash
# All fan events will be stored in fan_log.txt:
$ ./install.sh cron /home/$USER/fan_log.txt

# Alternative: do not store logging information:
$ ./install.sh cron
```

## Usage

When installed with a cronjob, there is no need to run `fanctrl` manually as temperature checks are
performed every 60 seconds.

To manually run the fan, execute `fanctrl -f`:

```bash
# Run the fan, no matter the actual cpu temperature
$ fanctrl -f
```


## TODO

- [ ] Add documentation for installing a cooling fan onto a SBC
