#!/bin/bash
cp fanctrl.py /usr/bin/fanctrl
chmod +x /usr/bin/fanctrl
if [ "$1" == "cron" ]; then
  echo "* * * * *  $USER  /usr/bin/fanctrl $1" > /etc/cron.d/fanctrl;
fi
