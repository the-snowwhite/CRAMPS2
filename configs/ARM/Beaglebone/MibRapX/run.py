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
    launcher.load_bbio_file('paralell_cape3.bbio')
    launcher.install_comp('thermistor_check.comp')
    launcher.install_comp('reset.comp')
    launcher.install_comp('led_dim.comp')
    launcher.start_process("configserver -n Uni-print-3D ~/Machineface")
    launcher.start_process('linuxcnc UNIPRINT-3D.ini')
except subprocess.CalledProcessError:
    launcher.end_session()
    sys.exit(1)

while True:
    sleep(1)
    launcher.check_processes()
