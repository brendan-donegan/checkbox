from dbus import Interface, SystemBus
from commands import getoutput


class Device(object):

    def __init__(self, hal_device):
        self._children = []
        self._device = hal_device
        self.properties = hal_device.GetAllProperties()
        self.udi = self.properties["info.udi"]
        self.parent = None

    def add_child(self, device):
        self._children.append(device)
        device.parent = self

    def get_children(self):
        return self._children


class DeviceManager(object):

    def __init__(self, bus=None):
        self._bus = bus or SystemBus()
        manager = self._bus.get_object("org.freedesktop.Hal",
                                       "/org/freedesktop/Hal/Manager")
        self._manager = Interface(manager, "org.freedesktop.Hal.Manager")

        version = getoutput('/usr/sbin/hald --version')
        self.version = version.rsplit(': ')[1]

    def get_devices(self):
        devices = []
        for udi in self._manager.GetAllDevices():
            hal_device = self._bus.get_object("org.freedesktop.Hal", udi)
            hal_device = Interface(hal_device, "org.freedesktop.Hal.Device")
            device = Device(hal_device)
            devices.append(device)

        return devices
