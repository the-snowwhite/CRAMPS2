import math

from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

import rcomps
import storage
import motion


def velocity_jog(thread):
    ''' Velocity extruding jog support '''
    # from ui
    jogVelocity = hal.newsig('ve-jog-velocity', hal.HAL_FLOAT)
    jogDirection = hal.newsig('ve-jog-direction', hal.HAL_BIT)
    jogDistance = hal.newsig('ve-jog-distance', hal.HAL_FLOAT)
    jogTrigger = hal.newsig('ve-jog-trigger', hal.HAL_BIT)
    jogDtg = hal.newsig('ve-jog-dtg', hal.HAL_FLOAT)
    jogContinous = hal.newsig('ve-jog-continous', hal.HAL_BIT)
    # helper signals
    jogEnable = hal.newsig('ve-jog-enable', hal.HAL_BIT)
    jogVelocityNeg = hal.newsig('ve-jog-velocity-neg', hal.HAL_FLOAT)
    jogVelocitySigned = hal.newsig('ve-velocity-signed', hal.HAL_FLOAT)
    jogTime = hal.newsig('ve-jog-time', hal.HAL_FLOAT)
    jogTimeLeft = hal.newsig('ve-jog-time-left', hal.HAL_FLOAT)
    jogActive = hal.newsig('ve-jog-active', hal.HAL_BIT)

    baseVel = hal.Signal('ve-base-vel')
    extruderEn = hal.Signal('ve-extruder-en')

    neg = rt.newinst('neg', 'neg.ve-jog-velocity-neg')
    hal.addf(neg.name, thread)
    neg.pin('in').link(jogVelocity)
    neg.pin('out').link(jogVelocityNeg)

    mux2 = rt.newinst('mux2', 'mux2.ve-jog-velocity-signed')
    hal.addf(mux2.name, thread)
    mux2.pin('in0').link(jogVelocity)
    mux2.pin('in1').link(jogVelocityNeg)
    mux2.pin('sel').link(jogDirection)
    mux2.pin('out').link(jogVelocitySigned)

    div2 = rt.newinst('div2', 'div2.ve-jog-time')
    hal.addf(div2.name, thread)
    div2.pin('in0').link(jogDistance)
    div2.pin('in1').link(jogVelocity)
    div2.pin('out').link(jogTime)

    oneshot = rt.newinst('oneshot', 'oneshot.ve-jog-active')
    hal.addf(oneshot.name, thread)
    oneshot.pin('in').link(jogTrigger)
    oneshot.pin('width').link(jogTime)
    oneshot.pin('time-left').link(jogTimeLeft)
    oneshot.pin('rising').set(1)
    oneshot.pin('falling').set(1)
    oneshot.pin('retriggerable').set(1)
    oneshot.pin('out').link(jogActive)

    or2 = rt.newinst('or2', 'or2.ve-jog-enable')
    hal.addf(or2.name, thread)
    or2.pin('in0').link(jogContinous)
    or2.pin('in1').link(jogActive)
    or2.pin('out').link(jogEnable)

    mux2 = rt.newinst('mux2', 'mux2.ve-base-vel')
    hal.addf(mux2.name, thread)
    mux2.pin('in0').set(0.0)
    mux2.pin('in1').link(jogVelocitySigned)
    mux2.pin('sel').link(jogEnable)
    mux2.pin('out').link(baseVel)

    mult2 = rt.newinst('mult2', 'mult2.ve-jog-dtg')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').link(jogVelocity)
    mult2.pin('in1').link(jogTimeLeft)
    mult2.pin('out').link(jogDtg)

    # disable extruder on jog
    reset = rt.newinst('reset', 'reset.extruder-en1')
    hal.addf(reset.name, thread)
    reset.pin('rising').set(True)
    reset.pin('falling').set(True)
    reset.pin('retriggerable').set(True)
    reset.pin('reset-bit').set(False)
    reset.pin('trigger').link(jogTrigger)
    reset.pin('out-bit').link(extruderEn)

    reset = rt.newinst('reset', 'reset.extruder-en2')
    hal.addf(reset.name, thread)
    reset.pin('rising').set(True)
    reset.pin('falling').set(False)
    reset.pin('retriggerable').set(True)
    reset.pin('reset-bit').set(False)
    reset.pin('trigger').link(jogContinous)
    reset.pin('out-bit').link(extruderEn)

    rcomps.create_ve_jog_rcomp()


def velocity_extrusion(thread):
    # from motion/ui
    xvel = hal.newsig('ve-xvel', hal.HAL_FLOAT)
    yvel = hal.newsig('ve-yvel', hal.HAL_FLOAT)
    zvel = hal.newsig('ve-zvel', hal.HAL_FLOAT)
    crossSection = hal.newsig('ve-cross-section', hal.HAL_FLOAT)
    filamentDia = hal.newsig('ve-filament-dia', hal.HAL_FLOAT)
    extrudeScale = hal.newsig('ve-extrude-scale', hal.HAL_FLOAT)
    extrudeAccelAdjGain = hal.newsig('ve-extrude-accel-adj-gain', hal.HAL_FLOAT)
    retractVel = hal.newsig('ve-retract-vel', hal.HAL_FLOAT)
    retractLen = hal.newsig('ve-retract-len', hal.HAL_FLOAT)
    maxVelocity = hal.newsig('ve-max-velocity', hal.HAL_FLOAT)
    # helper signals
    nozzleVelSigned = hal.newsig('ve-nozzle-vel-signed', hal.HAL_FLOAT)
    nozzleVel = hal.newsig('ve-nozzle-vel', hal.HAL_FLOAT)
    nozzleDischarge = hal.newsig('ve-nozzle-discharge', hal.HAL_FLOAT)
    filamentDiaSquared = hal.newsig('ve-filament-dia-squared', hal.HAL_FLOAT)
    filamentArea = hal.newsig('ve-filament-area', hal.HAL_FLOAT)
    extrudeRate = hal.newsig('ve-extrude-rate', hal.HAL_FLOAT)
    extrudeRateScaled = hal.newsig('ve-extrude-rate-scaled', hal.HAL_FLOAT)
    extrudeAccel = hal.newsig('ve-extrude-accel', hal.HAL_FLOAT)
    extrudeAccelAdj = hal.newsig('ve-extrude-accel-adj', hal.HAL_FLOAT)
    extrudeRateAdj = hal.newsig('ve-extrude-rate-adj', hal.HAL_FLOAT)
    extruderEn = hal.newsig('ve-extruder-en', hal.HAL_BIT)
    retractVelNeg = hal.newsig('ve-retract-vel-neg', hal.HAL_FLOAT)
    retractTime = hal.newsig('ve-retract-time', hal.HAL_FLOAT)
    retract = hal.newsig('ve-retract', hal.HAL_BIT)
    extrudeVel = hal.newsig('ve-extrude-vel', hal.HAL_FLOAT)
    baseVel = hal.newsig('ve-base-vel', hal.HAL_FLOAT)

    # take all the actual speeds from the axes and calculate resulting speed.
    xvel += 'axis.0.joint-vel-cmd'
    yvel += 'axis.1.joint-vel-cmd'
    zvel += 'axis.2.joint-vel-cmd'

    hypot = rt.newinst('hypot', 'hypot.ve-nozze-vel')
    hal.addf(hypot.name, thread)
    hypot.pin('in0').link(xvel)
    hypot.pin('in1').link(yvel)
    hypot.pin('in2').link(zvel)
    hypot.pin('out').link(nozzleVelSigned)

    absComp = rt.newinst('abs', 'abs.ve-nozzle-vel')
    hal.addf(absComp.name, thread)
    absComp.pin('in').link(nozzleVelSigned)
    absComp.pin('out').link(nozzleVel)

    # multiply area with speed and we get discharge (mm^3 per second)
    mult2 = rt.newinst('mult2', 'mult2.ve-nozzle-discharge')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').link(crossSection)
    mult2.pin('in1').link(nozzleVel)
    mult2.pin('out').link(nozzleDischarge)

    # calculate filament cross section area
    # PI divided by 4
    mult2 = rt.newinst('mult2', 'mult2.ve-filament-dia')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').link(filamentDia)
    mult2.pin('in1').link(filamentDia)
    mult2.pin('out').link(filamentDiaSquared)

    mult2 = rt.newinst('mult2', 'mult2.ve-filament-area')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').set(math.pi / 4)
    mult2.pin('in1').link(filamentDiaSquared)
    mult2.pin('out').link(filamentArea)

    # calculate extrude rate
    div2 = rt.newinst('div2', 'div2.ve-extrude-rate')
    hal.addf(div2.name, thread)
    div2.pin('in0').link(nozzleDischarge)
    div2.pin('in1').link(filamentArea)
    div2.pin('out').link(extrudeRate)

    # scale extrude rate
    mult2 = rt.newinst('mult2', 'mult2.ve-extrude-rate-scaled')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').link(extrudeRate)
    mult2.pin('in1').link(extrudeScale)
    mult2.pin('out').link(extrudeRateScaled)

    # these are used for a small offset in velocity during acceleration (buildup pressure inside
    # the nozzle because of the current speed. Take the maximum accel you've specified in .ini
    # get acceleration into lincurve
    ddt = rt.newinst('ddt', 'ddt.ve-extruder-accel')
    hal.addf(ddt.name, thread)
    ddt.pin('in').link(extrudeRateScaled)
    ddt.pin('out').link(extrudeAccel)

    mult2 = rt.newinst('mult2', 'mult2.ve-extrude-accel-adj')
    hal.addf(mult2.name, thread)
    mult2.pin('in0').link(extrudeAccel)
    mult2.pin('in1').link(extrudeAccelAdjGain)
    mult2.pin('out').link(extrudeAccelAdj)

    # get adjusted speed for adding to current speed during acceleration
    sum2 = rt.newinst('sum2', 'sum2.ve-extrude-rate-adj')
    hal.addf(sum2.name, thread)
    sum2.pin('in0').link(extrudeRateScaled)
    sum2.pin('in1').link(extrudeAccelAdj)
    sum2.pin('out').link(extrudeRateAdj)

    # negative retract velocity
    neg = rt.newinst('neg', 'neg.ve-rectract-vel-neg')
    hal.addf(neg.name, thread)
    neg.pin('in').link(retractVel)
    neg.pin('out').link(retractVelNeg)

    # calculate retract time
    div2 = rt.newinst('div2', 'div2.ve-retract-time')
    hal.addf(div2.name, thread)
    div2.pin('in0').link(retractLen)
    div2.pin('in1').link(retractVel)
    div2.pin('out').link(retractTime)

    # We want the retract-charge to run for a fixed time:
    # when sel0 set to "1" meaning motion with extrusion" the on the rising edge
    # there will temporarily be also sel1 which is high, meaning a pre-charge because the
    # sel combination is 11
    # when sel1 set to "0" meaning decoupling motion with extrusion" then the falling edge
    # will trigger a 01 combination, meaning a retract

    # trigger a retract/unretract move when extruder is enable or disabled
    oneshot = rt.newinst('oneshot', 'oneshot.ve-retract')
    hal.addf(oneshot.name, thread)
    oneshot.pin('rising').set(True)
    oneshot.pin('falling').set(True)
    oneshot.pin('retriggerable').set(True)
    oneshot.pin('width').link(retractTime)
    oneshot.pin('out').link(retract)

    retract += 'motion.feed-hold'  # stop motion until retract/unretract finished

    # jogging needs to be inserted here
    velocity_jog(thread)

    # now the solution of Andy Pugh for automatically retracting/priming
    #00 = motion without extrusion, jog
    #01 = retract
    #10 = motion with extrusion
    #11 = unretract, pre-charge
    mux4 = rt.newinst('mux4', 'mux4.ve-extrude-vel')
    hal.addf(mux4.name, thread)
    mux4.pin('in0').link(baseVel)
    mux4.pin('in1').link(retractVelNeg)
    mux4.pin('in2').link(extrudeRateAdj)
    mux4.pin('in3').link(retractVel)
    mux4.pin('out').link(extrudeVel)
    mux4.pin('sel0').link(retract)
    mux4.pin('sel1').link(extruderEn)

    # default values
    retractLen.set(c.find('EXTRUDER_0', 'RETRACT_LEN'))
    retractVel.set(c.find('EXTRUDER_0', 'RETRACT_VEL'))
    filamentDia.set(c.find('EXTRUDER_0', 'FILAMENT_DIA'))
    maxVelocity.set(c.find('EXTRUDER_0', 'MAX_VELOCITY'))  # TODO shoud be on a per Extruder base
    extrudeAccelAdjGain.set(0.05)
    extrudeScale.set(1.0)
    if baseVel.writers < 1:  # can only write when jogging not configured
        baseVel.set(0.0)

    rcomps.create_ve_params_rcomp()
    storage.setup_ve_storage()
    motion.setup_ve_io()
