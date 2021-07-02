from ctypes import *


class Enum:
    def __init__(self, enum_name, members):
        self.cls = type(enum_name, (c_int,), members)
        self.cls.__name__ = "Enum"
        self.cls.__repr__ = Enum.__repr__

    def __repr__(self):
        memb = {y: x for x, y in self.__class__.__dict__.items() if not x.startswith('_')}
        if self.value not in memb:
            print("%s: %s not in %s" % (self.__class__, self.value, self.__class__.__dict__))
            return str(self.value) + " /* out of range */"
        return memb[self.value]
