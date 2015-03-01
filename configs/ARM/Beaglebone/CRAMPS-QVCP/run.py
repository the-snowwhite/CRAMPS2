#!/usr/bin/python

import sys
import os
import subprocess
import importlib
import argparse
from time import *
from machinekit import launcher


launcher.register_exit_handler()
#launcher.set_debug_level(5)
os.chdir(os.path.dirname(os.path.realpath(__file__)))

try:
    launcher.check_installation()                                     # make sure the Machinekit installation is sane
    launcher.cleanup_session()                                        # cleanup a previous session
    launcher.load_bbio_file('cramps2_cape.bbio')                         # load a BBB universal overlay
    launcher.install_comp('thermistor_check.comp')
#    launcher.install_comp('gantry.comp')                              # install a comp HAL component of not already installed
    launcher.start_process("configserver -n CRAMPS_QVCP-3D ~/Machineface")   # start the configserver
    launcher.start_process('linuxcnc CRAMPS_QVCP.ini')                        # start linuxcnc
except subprocess.CalledProcessError:
    launcher.end_session()
    sys.exit(1)

while True:
    sleep(1)
    launcher.check_processes()
