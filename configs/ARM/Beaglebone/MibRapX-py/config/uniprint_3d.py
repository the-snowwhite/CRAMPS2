from machinekit import hal
from machinekit import rtapi as rt
from machinekit import config as c

import base


def hardware_read():
    hal.addf('hpg.capture-position', 'servo-thread')
    hal.addf('bb_gpio.read', 'servo-thread')


def hardware_write():
    hal.addf('hpg.update', 'servo-thread')
    hal.addf('bb_gpio.write', 'servo-thread')


def init_hardware():
    watchList = []

    # load low-level drivers
    rt.loadrt('hal_bb_gpio', output_pins='807,819,826,926', input_pins='941')
    prubin = '%s/%s' % (c.Config().EMC2_RTLIB_DIR, c.find('PRUCONF', 'PRUBIN'))
    rt.loadrt(c.find('PRUCONF', 'DRIVER'),
              pru=0, num_stepgens=5, num_pwmgens=0,
              prucode=prubin, halname='hpg')

    # Python user-mode HAL module to interface with an I2C gpio extender
    hal.loadusr('hal_gpio_mcp23017',
                name='i2c-gpio',
                bus_id=2,
                address=32,
                interval=0.05,
                delay=2.5,
                input_pins='A00,A01,A02,A03,A04,A05,A06,A07,B06,B07',
                output_pins='B00,B01,B02,B03,B04,B05',
                wait_name='i2c-gpio')
    watchList.append(['i2c-gpio', 0.1])

    # Python user-mode HAL module to interface with an I2C PWM generator
    hal.loadusr('hal_pwm_pca9685',
                name='i2c-pwm',
                bus_id=2,
                address=67,
                interval=0.1,
                delay=2.6,
                wait_name='i2c-pwm')
    watchList.append(['i2c-pwm', 0.2])

    # Python user-mode HAL module to interface with an I2C ADC and convert it to temperature
    defaultThermistor = 'semitec_103GT_2'
    hal.loadusr('hal_temp_ads7828',
                name='i2c-temp',
                bus_id=2,
                address=72,
                interval=0.05,
                delay=2.7,
                filter_size=1,
                channels='00:%s,01:%s,02:%s,03:%s,04:%s,05:none,06:none,07:none'
                % (c.find('HBP', 'THERMISTOR', defaultThermistor),
                   c.find('EXTRUDER_0', 'THERMISTOR', defaultThermistor),
                   c.find('EXTRUDER_1', 'THERMISTOR', defaultThermistor),
                   c.find('EXTRUDER_2', 'THERMISTOR', defaultThermistor),
                   c.find('EXTRUDER_3', 'THERMISTOR', defaultThermistor)),
                wait_name='i2c-temp')
    watchList.append(['i2c-temp', 0.1])

    base.usrcomp_status('i2c-gpio', 'gpio-hw', thread='servo-thread')
    base.usrcomp_status('i2c-pwm', 'pwm-hw', thread='servo-thread')
    base.usrcomp_status('i2c-temp', 'temp-hw', thread='servo-thread')
    base.usrcomp_watchdog(watchList, 'estop-reset', thread='servo-thread',
                          errorSignal='watchdog-error')


def setup_hardware(thread):
    # PWM
    # HBP
    hal.Pin('i2c-pwm.out-00.enable').set(True)
    hal.Pin('i2c-pwm.out-00.value').link('hbp-temp-pwm')
    # configure extruders
    for n in range(0, 4):
        hal.Pin('i2c-pwm.out-%02i.enable' % (n + 1)).set(True)
        hal.Pin('i2c-pwm.out-%02i.value' % (n + 1)).link('e%i-temp-pwm' % n)
    # configure fans
    for n in range(0, 4):
        hal.Pin('i2c-pwm.out-%02i.enable' % (n + 5)).link('f%i-pwm-enable' % n)
        hal.Pin('i2c-pwm.out-%02i.value' % (n + 5)).link('f%i-pwm' % n)
        hal.Signal('f%i-pwm-enable' % n).set(True)
    # configure exps
    for n in range(0, 2):
        hal.Pin('i2c-pwm.out-%02i.enable' % (n + 9)).link('exp%i-pwm-enable' % n)
        hal.Pin('i2c-pwm.out-%02i.value' % (n + 9)).link('exp%i-pwm' % n)
        hal.Signal('exp%i-pwm' % n).set(1.0)
    # configure leds
    for n, color in enumerate(('g', 'r', 'b', 'w')):
        hal.Pin('i2c-pwm.out-%02i.enable' % (n + 11)).set(True)
        hal.Pin('i2c-pwm.out-%02i.value' % (n + 11)).link('l0-%s-out' % color)
    # PWM0
    hal.Pin('i2c-pwm.out-15.enable').set(True)
    hal.Pin('i2c-pwm.out-15.value').set(0.0)

    # GPIO
    hal.Pin('i2c-gpio.A.in-00').link('limit-0-home')    # X
    hal.Pin('i2c-gpio.A.in-01').link('limit-1-home')    # Y
    hal.Pin('i2c-gpio.A.in-02').link('limit-2-0-home')  # ZR
    hal.Pin('i2c-gpio.A.in-03').link('limit-2-1-home')  # ZL
    hal.Pin('i2c-gpio.A.in-04').link('probe-signal')
    # hal.Pin('i2c-gpio.A.in-05').link('sensor1')
    # hal.Pin('i2c-gpio.A.in-06').link('sensor1')
    # hal.Pin('i2c-gpio.A.in-07').link('sensor1')
    hal.Pin('i2c-gpio.B.out-00').link('e0-enable')
    hal.Pin('i2c-gpio.B.out-01').link('e1-enable')
    hal.Pin('i2c-gpio.B.out-02').link('e2-enable')
    hal.Pin('i2c-gpio.B.out-03').link('e3-enable')
    hal.Pin('i2c-gpio.B.out-04').link('led-hbp-info')
    hal.Pin('i2c-gpio.B.out-05').link('led-hbp-hot')
    hal.Pin('i2c-gpio.B.in-06').link('pwr-mon')
    hal.Pin('i2c-gpio.B.in-07').link('hbp-mon')

    # Adjust as needed for your switch polarity
    hal.Pin('i2c-gpio.A.in-00.invert').set(True)
    hal.Pin('i2c-gpio.A.in-01.invert').set(True)
    hal.Pin('i2c-gpio.A.in-02.invert').set(True)
    hal.Pin('i2c-gpio.A.in-03.invert').set(True)
    hal.Pin('i2c-gpio.A.in-04.invert').set(True)
    hal.Pin('i2c-gpio.A.in-05.invert').set(True)
    hal.Pin('i2c-gpio.A.in-06.invert').set(True)
    hal.Pin('i2c-gpio.A.in-07.invert').set(True)
    hal.Pin('i2c-gpio.B.out-00.invert').set(False)
    hal.Pin('i2c-gpio.B.out-01.invert').set(False)
    hal.Pin('i2c-gpio.B.out-02.invert').set(False)
    hal.Pin('i2c-gpio.B.out-03.invert').set(False)
    hal.Pin('i2c-gpio.B.out-04.invert').set(False)
    hal.Pin('i2c-gpio.B.out-05.invert').set(False)
    hal.Pin('i2c-gpio.B.in-06.invert').set(False)
    hal.Pin('i2c-gpio.B.in-07.invert').set(False)

    # Enable pullup for mechanical endstops
    hal.Pin('i2c-gpio.A.in-00.pullup').set(True)
    hal.Pin('i2c-gpio.A.in-01.pullup').set(True)
    hal.Pin('i2c-gpio.A.in-02.pullup').set(True)
    hal.Pin('i2c-gpio.A.in-03.pullup').set(True)
    hal.Pin('i2c-gpio.A.in-04.pullup').set(True)
    hal.Pin('i2c-gpio.A.in-05.pullup').set(False)
    hal.Pin('i2c-gpio.A.in-06.pullup').set(False)
    hal.Pin('i2c-gpio.A.in-07.pullup').set(False)
    hal.Pin('i2c-gpio.B.in-06.pullup').set(False)
    hal.Pin('i2c-gpio.B.in-07.pullup').set(False)

    # ADC
    hal.Pin('i2c-temp.ch-00.value').link('hbp-temp-meas')
    hal.Pin('i2c-temp.ch-01.value').link('e0-temp-meas')
    hal.Pin('i2c-temp.ch-02.value').link('e1-temp-meas')
    hal.Pin('i2c-temp.ch-03.value').link('e2-temp-meas')
    hal.Pin('i2c-temp.ch-04.value').link('e3-temp-meas')
    #hal.Pin('i2c-temp.ch-05.value').link('ain0')
    #hal.Pin('i2c-temp.ch-06.value').link('ain1')
    #hal.Pin('i2c-temp.ch-07.value').link('ain2')

    # Stepper
    hal.Pin('hpg.stepgen.00.steppin').set(812)
    hal.Pin('hpg.stepgen.00.dirpin').set(811)
    hal.Pin('hpg.stepgen.01.steppin').set(816)
    hal.Pin('hpg.stepgen.01.dirpin').set(815)
    hal.Pin('hpg.stepgen.02.steppin').set(913)
    hal.Pin('hpg.stepgen.02.dirpin').set(925)
    hal.Pin('hpg.stepgen.03.steppin').set(922)
    hal.Pin('hpg.stepgen.03.dirpin').set(921)
    hal.Pin('hpg.stepgen.04.steppin').set(911)
    hal.Pin('hpg.stepgen.04.dirpin').set(942)

    # charge pump
    chargePump = rt.loadrt('charge_pump')
    hal.addf('charge-pump', thread)
    hal.Pin('charge-pump.out').link('charge-pump-out')
    hal.Pin('charge-pump.enable').link('emcmot-0-enable')

    # charge pump tied to machine power
    hal.Pin('bb_gpio.p8.out-19').link('charge-pump-out')
    # Monitor estop input from hardware
    hal.Pin('bb_gpio.p9.in-41').link('estop-in')
    hal.Pin('bb_gpio.p9.in-41.invert').set(True)
    # drive estop-sw
    hal.Pin('bb_gpio.p8.out-07').link('estop-out')
    hal.Pin('bb_gpio.p8.out-07.invert').set(True)

    # Tie machine power signal to the Parport Cape LED
    # Feel free to tie any other signal you like to the LED
    hal.Pin('bb_gpio.p8.out-26').link('emcmot-0-enable')
    # hal.Pin('bb_gpio.p8.out-26.invert').set(True)

    # link emcmot.xx.enable to stepper driver enable signals


def setup_hbp_led(thread):
    tempMeas = hal.Signal('hbp-temp-meas')
    ledHbpHot = hal.newsig('led-hbp-hot', hal.HAL_BIT)
    ledHbpInfo = hal.newsig('led-hbp-info', hal.HAL_BIT)

    # low temp
    comp = rt.newinst('comp', 'comp.hbp-info')
    hal.addf(comp.name, thread)
    comp.pin('in0').set(50.0)
    comp.pin('in1').link(tempMeas)
    comp.pin('hyst').set(2.0)
    comp.pin('out').link(ledHbpInfo)

    # high temp
    comp = rt.newinst('comp', 'comp.hbp-hot')
    hal.addf(comp.name, thread)
    comp.pin('in0').link(tempMeas)
    comp.pin('in1').set(50.0)
    comp.pin('hyst').set(2.0)
    comp.pin('out').link(ledHbpHot)


def setup_exp(name):
    hal.newsig('%s-pwm' % name, hal.HAL_FLOAT, init=0.0)
    hal.newsig('%s-enable' % name, hal.HAL_BIT, init=False)
