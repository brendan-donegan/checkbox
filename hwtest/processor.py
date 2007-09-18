import os

from hwtest.lib.conversion import string_to_int


class Processor(object):

    def __init__(self, **kwargs):
        self.properties = kwargs


class ProcessorManager(object):

    default_filename = os.path.join(os.sep, 'proc', 'cpuinfo')

    def __init__(self, filename=None):
        self._filename = filename or self.default_filename

    def get_processors(self):
        processors = []
        cpuinfo = {}
        fd = file(self._filename, "r")

        for line in map(lambda l: l.strip(), fd.readlines()):
            if not line:
                processor = Processor(**cpuinfo)
                processors.append(processor)
                cpuinfo = {}
            elif line.find(":") != -1:
                (key, value) = line.split(':', 1)
                key = key.strip()
                key = key.replace(' ', '_')
                value = value.strip()
                cpuinfo[key] = string_to_int(value)

        return processors
