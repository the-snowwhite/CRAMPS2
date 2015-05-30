#!/usr/bin/python

import sys
import os
import subprocess
import importlib
import argparse
from time import *
from machinekit import launcher
#from machinekit import config

launcher.register_exit_handler()
launcher.set_debug_level(5)
launcher.set_machinekit_ini('machinekit.ini')
os.chdir(os.path.dirname(os.path.realpath(__file__)))
#c = config.Config()
#os.environ["MACHINEKIT_INI"] = c.MACHINEKIT_INI

parser = argparse.ArgumentParser(description='This is the MibRap-X run script '
                                 'it demonstrates how a run script could look like '
                                 'and of course starts the MibRapX config')

parser.add_argument('-v', '--video', help='Starts the video server', action='store_true')

args = parser.parse_args()

try:
    launcher.check_installation()
    launcher.cleanup_session()
    launcher.load_bbio_file('cramps2_cape.bbio')
    launcher.install_comp('thermistor_check.comp')
    launcher.install_comp('reset.comp')
    launcher.start_process("configserver -n MibRap-X ~/Machineface")
    if args.video:
        launcher.start_process('videoserver --ini video.ini Webcam1')
    launcher.start_process('linuxcnc MibRapX.ini')
except subprocess.CalledProcessError:
    launcher.end_session()
    sys.exit(1)

while True:
    sleep(1)
    launcher.check_processes()
