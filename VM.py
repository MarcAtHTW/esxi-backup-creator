#!/usr/bin/python

class VM(object):

    vmId = ""
    name = ""
    file = ""
    guestOs = ""
    version = ""



    def __init__(self, vmId, name, file, guestOs, version):
        self.vmId = vmId
        self.name = name
        self.file = file
        self.guestOs = guestOs
        self.version = version

    def __init__(self):
        self=self


