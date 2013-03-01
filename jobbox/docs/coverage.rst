Job Coverage
============

This document summarizes job / test coverage as provided by JobBox

Hardware Jobs
^^^^^^^^^^^^^

============= ====================================== ========================
Category Name          Hardware in scope                   Description
============= ====================================== ========================
audio         Sound card, headphone jacks, etc       basic functionality tests
benchmarks    CPUs, GPUs, Disks, Network             assorted benchmarks
bluetooth     Bluetooth hardware                     basic functionality tests
camera        video input devices, webcams           basic functionality tests 
cpu           CPU                                    basic cpu features
disk          Hard drives and SSD                    basic functionality and capacity tests
esata         eSATA-connected disks
expresscard   Express cards
fingerprint   Fingerprint scanners
firewire      Firewire-connected disks
floppy        Floppy disks
graphics      Integrated and discrete GPUSs
input         Mouse, touchpad and touchscreen
keys          Special hardware keys
led           Indicator LEDs
mediacard     Memory card readers (SD, uSD, xD)
memory        RAM
monitor       CRT and LCD monitors
networking    Ethernet, WiFI and modem
optical       optical drives (CDs, DVDs)
peripheral    external printer and modem tests
stress        entire machine                         extended stress testing
============= ====================================== ========================

Software Jobs 
^^^^^^^^^^^^^

================= ==========================
Category Name         Software in scope
================= ==========================
codecs            software audio codecs
daemons           essential system daemons 
install           apt-get and oem-config
panel_clock_test  date and time display and control 
panel_reboot      reboot control
piglit            various piglit tests (graphics)
rendercheck       various rendercheck tests (graphics)
server-services   typical server services
================= ==========================

Power management jobs
^^^^^^^^^^^^^^^^^^^^^

================ ==========================
Category Name           Description 
================ ==========================
hibernate        whole-system suspend-to-disk
suspend          whole-system suspend-to-ram
power-management fine-grained ACPI tests
================ ==========================

Misc jobs
^^^^^^^^^

============= ==========================
Category Name        Description
============= ==========================
info          hardware information logs 
local         local jobs (checkbox legacy)
miscellanea   other assorted jobs
resource      software and hardware probes that enable specific tests
smoke         smoke tests for checkbox job management
============= ==========================
