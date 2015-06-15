#!/usr/bin/python
import math

from machinekit import rtapi as rt
from machinekit import hal
from machinekit import config as c

from config import velocity_extrusion as ve
from config import uniprint_3d
from config import base
from config import storage


# HAL file for BeagleBone + TCT paralell port cape with 5 steppers and 3D printer board
rt.init_RTAPI()
c.load_ini('test.ini')

base.setup_motion()
uniprint_3d.init_hardware()
storage.init_storage('storage.ini')

# Gantry component for Z Axis
base.init_gantry(axisIndex=2)

# reading functions
uniprint_3d.hardware_read()
base.gantry_read(gantryAxis=2, thread='servo-thread')
hal.addf('motion-command-handler', 'servo-thread')

# Axis-of-motion Specific Configs (not the GUI)
ve.velocity_extrusion('servo-thread')
# X [0] Axis
base.setup_stepper(section='AXIS_0', axisIndex=0, stepgenIndex=0)
# Y [1] Axis
base.setup_stepper(section='AXIS_1', axisIndex=1, stepgenIndex=1)
# Z [2] Axis
base.setup_stepper(section='AXIS_2', axisIndex=2, stepgenIndex=2,
              thread='servo-thread', gantry=True, gantryJoint=0)
base.setup_stepper(section='AXIS_2', axisIndex=2, stepgenIndex=3,
            gantry=True, gantryJoint=1)
# Extruder, velocity controlled
base.setup_stepper(section='AXIS_3', stepgenIndex=4, velocitySignal='ve-extrude-vel')
# TODO ABP

numFans = int(c.find('FDM', 'NUM_FANS'))
numExtruders = int(c.find('FDM', 'NUM_EXTRUDERS'))
numLights = int(c.find('FDM', 'NUM_LIGHTS'))

# Fans
for i in range(0, numFans):
    base.setup_fan('f%i' % i, thread='servo-thread')
for i in range(0, numExtruders):
    uniprint_3d.setup_exp('exp%i' % i)

# Temperature Signals
base.create_temperature_control(name='hbp', section='HBP',
                                hardwareOkSignal='temp-hw-ok',
                                thread='servo-thread')
for i in range(0, numExtruders):
    base.create_temperature_control(name='e%i' % i, section='EXTRUDER_%i' % i,
                                    coolingFan='f%i' % i, hotendFan='exp%i' % i,
                                    hardwareOkSignal='temp-hw-ok',
                                    thread='servo-thread')

# Extruder Multiplexer
base.setup_extruder_multiplexer(extruders=numExtruders, thread='servo-thread')

# LEDs
for i in range(0, numLights):
    base.setup_light('l%i' % i, thread='servo-thread')
# HB LED
uniprint_3d.setup_hbp_led(thread='servo-thread')

# Standard I/O - EStop, Enables, Limit Switches, Etc
errorSignals = ['gpio-hw-error', 'pwm-hw-error', 'temp-hw-error',
                'watchdog-error', 'hbp-error']
for i in range(0, numExtruders):
    errorSignals.append('e%i-error' % i)
base.setup_estop(errorSignals, thread='servo-thread')
base.setup_tool_loopback()
# Probe
base.setup_probe(thread='servo-thread')
# Setup Hardware
uniprint_3d.setup_hardware(thread='servo-thread')

# write out functions
hal.addf('motion-controller', 'servo-thread')
base.gantry_write(gantryAxis=2, thread='servo-thread')
uniprint_3d.hardware_write()

# Storage
storage.read_storage()

# start haltalk server after everything is initialized
# else binding the remote components on the UI might fail
hal.loadusr('haltalk', wait=True)
