#!/usr/bin/python
# /etc/init.d/rpi-rescue.py
### BEGIN INIT INFO
# Provides:          rpi-rescue.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

import os
import subprocess
import time
import logging

def main():
    logging.basicConfig(filename='/var/log/rpi-rescue.log', level=logging.INFO, format='%(message)s %(asctime)s', datefmt='%m/%d/%Y %I:%M:%S')
    while True:
        time.sleep(120)
        print time.clock()
        print time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        sub = subprocess.call('ping -c 10 192.168.1.1 -I eth0',shell=True)
        if int(sub) == 1:
            logging.info('rebooted at : ')
            subprocess.call('reboot')
        else:
            logging.info('OK at : ')

if __name__ == '__main__':
    main()