from machinekit import hal


def setup_temperature_io(name):
    index = 0
    if name == 'hbp':
        index = 0
    elif name == 'hbc':
        index = 1
    elif name[0] == 'e':
        index = 2 + int(name[1])
    else:
        raise RuntimeError('temperature io name not known')

    hal.Pin('motion.analog-out-io-%02i' % index).link('%s-temp-set' % name)
    hal.Pin('motion.analog-in-%02i' % index).link('%s-temp-meas' % name)
    hal.Pin('motion.digital-in-%02i' % index).link('%s-temp-in-range' % name)


def setup_fan_io(name):
    if name[0] == 'f':
        index = 12 + int(name[1])
    else:
        raise RuntimeError('fan io name not known')

    hal.Pin('motion.analog-out-io-%02i' % index).link('%s-set' % name)
    hal.Pin('motion.analog-in-%02i' % index).link('%s-set' % name)


def setup_light_io(name):
    if name[0] == 'l':
        index = 26 + int(name[1]) * 4
    else:
        raise RuntimeError('light io name not known')

    for m, color in enumerate(('r', 'g', 'b', 'w')):
        hal.Pin('motion.analog-out-io-%02i' % (index + m)) \
           .link('%s-%s' % (name, color))
        hal.Pin('motion.analog-in-%02i' % (index + m)) \
           .link('%s-%s' % (name, color))


def setup_probe_io():
    hal.Pin('motion.analog-out-38').link('probe-sel-f')
    hal.Pin('motion.digital-out-00').link('probe-enable')


def setup_ve_io():
    hal.Pin('motion.analog-out-41').link('ve-cross-section')
    hal.Pin('motion.analog-out-42').link('ve-line-width')
    hal.Pin('motion.analog-out-43').link('ve-line-height')
    hal.Pin('motion.analog-out-io-44').link('ve-filament-dia')
    hal.Pin('motion.analog-out-io-45').link('ve-jog-velocity')
    hal.Pin('motion.analog-out-io-46').link('ve-jog-distance')
    hal.Pin('motion.digital-out-io-01').link('ve-extruder-en')
    hal.Pin('motion.digital-out-io-02').link('ve-jog-trigger')
    hal.Pin('motion.digital-in-12').link('ve-jog-trigger')

