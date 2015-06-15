from machinekit import hal


def init_storage(fileName):
    # Python user-mode HAL module for storing values
    hal.loadusr('hal_storage', name='storage', file=fileName,
                autosave=True, wait_name='storage')


def read_storage():
    hal.Pin('storage.read-trigger').set(True)  # trigger read


def setup_gantry_storage(gantryAxis, gantryJoint):
    hal.Pin('storage.gantry.home-offset-%i-%i' % (gantryAxis, gantryJoint)) \
       .link('home-offset-%i-%i' % (gantryAxis, gantryJoint))


def setup_ve_storage():
    hal.Pin('storage.retract.velocity').link('ve-retract-vel')
    hal.Pin('storage.retract.length').link('ve-retract-len')
    hal.Pin('storage.filament.diameter').link('ve-filament-dia')
    hal.Pin('storage.extruder.jog-velocity').link('ve-jog-velocity')


def setup_light_storage(name):
    for color in ('r', 'g', 'b', 'w'):
        hal.Pin('storage.%s.%s' % (name, color)).link('%s.%s' % (name, color))
