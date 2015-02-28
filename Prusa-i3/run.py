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
    launcher.check_installation()
    launcher.cleanup_session()
    launcher.load_bbio_file('cramps2_cape.bbio')
    launcher.install_comp('thermistor_check.comp')
    launcher.install_comp('reset.comp')
    launcher.start_process("configserver -n Prusa-i3 ~/Machineface")
    launcher.start_process('linuxcnc CRAMPS2.ini')
except subprocess.CalledProcessError:
    launcher.end_session()
    sys.exit(1)

while True:
    sleep(1)
    launcher.check_processes()
