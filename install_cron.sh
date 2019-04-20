#!/bin/bash
echo -e "$(crontab -l)\n* * * * *  /usr/bin/fanctrl $1" | crontab -
