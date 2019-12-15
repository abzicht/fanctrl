#!/bin/sh

systemdfile="/lib/systemd/system/fanctrl.service"
echo "
[Unit]
Description=Fan Controller
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /usr/bin/fanctrl -l /var/log/fanctrl.txt

[Install]
WantedBy=multi-user.target
" > ${systemdfile}
chmod 644 ${systemdfile}
systemctl daemon-reload
systemctl enable fanctrl.service
systemctl start  fanctrl.service
systemctl status fanctrl.service
