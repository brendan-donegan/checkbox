#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import re
import posixpath

from checkbox.lib.cache import cache
from checkbox.lib.pci import Pci

from checkbox.properties import String
from checkbox.registry import Registry
from checkbox.registries.command import CommandRegistry


UNKNOWN = "Unknown"


class UnknownName(object):
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        name = self._function(self._instance, *args, **kwargs)
        if name.startswith("Unknown ("):
            name = UNKNOWN

        return name


class DeviceRegistry(Registry):
    """Registry for HAL device information.

    Each item contained in this registry consists of the properties of
    the corresponding HAL device.
    """

    def __init__(self, properties):
        self._properties = properties

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.items()]

        return "\n".join(strings)

    def _get_category(self):
        if "net.interface" in self._properties:
            return "NETWORK"

        if "pci.device_class" in self._properties:
            class_id = self._properties["pci.device_class"]
            subclass_id = self._properties["pci.device_subclass"]

            if class_id == Pci.BASE_CLASS_NETWORK:
                return "NETWORK"

            if class_id == Pci.BASE_CLASS_DISPLAY:
                return "VIDEO"

            if class_id == Pci.BASE_CLASS_SERIAL \
               and subclass_id == Pci.CLASS_SERIAL_USB:
                return "USB"

            if class_id == Pci.BASE_CLASS_STORAGE:
                if subclass_id == Pci.CLASS_STORAGE_SCSI:
                    return "SCSI"

                if subclass_id == Pci.CLASS_STORAGE_IDE:
                    return "IDE"

                if subclass_id == Pci.CLASS_STORAGE_FLOPPY:
                    return "FLOPPY"

                if subclass_id == Pci.CLASS_STORAGE_RAID:
                    return "RAID"

            if class_id == Pci.BASE_CLASS_COMMUNICATION \
               and subclass_id == Pci.CLASS_COMMUNICATION_MODEM:
                return "MODEM"

            if class_id == Pci.BASE_CLASS_INPUT \
               and subclass_id == Pci.CLASS_INPUT_SCANNER:
                return "SCANNER"

            if class_id == Pci.BASE_CLASS_MULTIMEDIA:
                if subclass_id == Pci.CLASS_MULTIMEDIA_VIDEO:
                    return "CAPTURE"

                if subclass_id == Pci.CLASS_MULTIMEDIA_AUDIO:
                    return "AUDIO"

            if class_id == Pci.BASE_CLASS_SERIAL \
               and subclass_id == Pci.CLASS_SERIAL_FIREWIRE:
                return "FIREWIRE"

            if class_id == Pci.BASE_CLASS_BRIDGE \
               and (subclass_id == Pci.CLASS_BRIDGE_PCMCIA \
                    or subclass_id == Pci.CLASS_BRIDGE_CARDBUS):
                return "SOCKET"

        if "info.capabilities" in self._properties:
            capabilities = self._properties["info.capabilities"]
            if "input.keyboard" in capabilities:
                return "KEYBOARD"

            if "input.mouse" in capabilities:
                return "MOUSE"

        if "storage.drive_type" in self._properties:
            drive_type = self._properties["storage.drive_type"]
            if drive_type == "cdrom":
                return "CDROM"

            if drive_type == "disk":
                return "DISK"

            if drive_type == "floppy":
                return "FLOPPY"

        if "pci.vendor_id" in self._properties \
           or "usb_device.vendor_id" in self._properties:
            return "OTHER"

        return None

    def _get_bus(self):
        return self._properties.get("linux.subsystem", UNKNOWN)

    def _get_driver(self):
        return self._properties.get("info.linux.driver", UNKNOWN)

    def _get_path(self):
        return self._properties.get("linux.sysfs_path", "").replace("/sys", "")

    def _get_type(self):
        # Strip the string literals generated by HAL
        for property in ("ccwgroup.ctc.type",
                         "ccwgroup.lcs.type",
                         "ibmebus.type",
                         "mmc.type",
                         "net.arp_proto_hw_id"):
            if property in self._properties:
                return self._properties[property]

        if "battery.type" in self._properties:
            name = self._properties["battery.type"]
            if name == "primary":
                name = "battery"
            return name

        if "info.category" in self._properties:
            category = self._properties["info.category"]
            if category == "bluetooth_acl":
                return "ACL"
            if category == "bluetooth_sco":
                return "SCO"
            if category == "bluetooth_hci":
                return "USB"

        if "killswitch.type" in self._properties:
            name = self._properties["killswitch.type"]
            if name == "wwan":
                name = "wimax"
            if name != "unknown":
                return name

        if "scsi.type" in self._properties:
            name = self._properties["scsi.type"]
            name_to_type = {
                "disk": "0",
                "tape": "1",
                "printer": "2",
                "processor": "3",
                "cdrom": "5",
                "scanner": "6",
                "medium_changer": "8",
                "comm": "9",
                "raid": "12"}
            if name in name_to_type:
                return name_to_type[name]

        return None

    def _get_vendor_id(self):
        if "info.subsystem" in self._properties:
            vendor_id = "%s.vendor_id" % self._properties["info.subsystem"]
            if vendor_id in self._properties:
                return self._properties[vendor_id]

        return None

    def _get_product_id(self):
        if "info.subsystem" in self._properties:
            product_id = "%s.product_id" % self._properties["info.subsystem"]
            if product_id in self._properties:
                return self._properties[product_id]

        return None

    def _get_subvendor_id(self):
        return self._properties.get("pci.subsys_vendor_id")

    def _get_subproduct_id(self):
        return self._properties.get("pci.subsys_product_id")

    @UnknownName
    def _get_vendor(self):
        bus = self._get_bus()

        # Ignore subsystems using parent for vendor
        if bus in ("drm", "rfkill"):
            return UNKNOWN

        for property in ("battery.vendor",
                         "ieee1394.vendor",
                         "scsi.vendor",
                         "info.vendor"):
            if property in self._properties:
                return self._properties[property]

        return UNKNOWN

    @UnknownName
    def _get_product(self):
        bus = self._get_bus()

        # Ignore subsystems using parent for product
        if bus in ("drm", "net", "platform", "scsi_generic",
                   "scsi_host", "tty", "video4linux"):
            return UNKNOWN

        if "usb.interface.number" in self._properties:
            return UNKNOWN

        if self._properties.get("info.category") == "ac_adapter":
            return UNKNOWN

        for property in ("alsa.device_id",
                         "alsa.card_id",
                         "sound.card_id",
                         "battery.model",
                         "ieee1394.product",
                         "killswitch.name",
                         "oss.device_id",
                         "scsi.model",
                         "pnp.id",
                         "info.product"):
            if property in self._properties:
                return self._properties[property]

        return UNKNOWN

    def items(self):
        return (
            ("path", self._get_path()),
            ("bus", self._get_bus()),
            ("category", self._get_category()),
            ("driver", self._get_driver()),
            ("type", self._get_type()),
            ("vendor_id", self._get_vendor_id()),
            ("product_id", self._get_product_id()),
            ("subvendor_id", self._get_subvendor_id()),
            ("subproduct_id", self._get_subproduct_id()),
            ("vendor", self._get_vendor()),
            ("product", self._get_product()))


class HalRegistry(CommandRegistry):
    """Registry for HAL information.

    Each item contained in this registry consists of the udi as key and
    the corresponding device registry as value.
    """

    # Command to retrieve hal information.
    command = String(default="lshal")

    def _ignore_device(self, device):
        # Ignore devices without bus or product information
        if device.bus == UNKNOWN \
           or device.product == UNKNOWN:
            return True

        # Ignore virtual devices
        if "virtual" in device.path.split(posixpath.sep):
            return True

        return False

    @cache
    def items(self):
        items = []
        for record in self.split("\n\n"):
            if not record:
                continue

            path = None
            properties = {}
            for line in record.split("\n"):
                match = re.match(r"udi = '(.*)'", line)
                if match:
                    udi = match.group(1)
                    path = udi.split("/")[-1]
                    continue

                match = re.match(r"  (.*) = (.*) \((.*?)\)", line)
                if match:
                    key = match.group(1)
                    value = match.group(2).strip()
                    type_name = match.group(3)
                    if type_name == "bool":
                        value = bool(value == "true")
                    elif type_name == "double":
                        value = float(value.split()[0])
                    elif type_name == "int" or type_name == "uint64":
                        value = int(value.split()[0])
                    elif type_name == "string":
                        value = str(value.strip("'"))
                    elif type_name == "string list":
                        value = [v.strip("'")
                                for v in value.strip("{}").split(", ")]
                    else:
                        raise Exception, "Unknown type: %s" % type_name

                    properties[key] = value

            device = DeviceRegistry(properties)
            if not self._ignore_device(device):
                items.append((path, device))

        return items


factory = HalRegistry
