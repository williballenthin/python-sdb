from vstruct import VStruct
from vstruct.primitives import v_bytes
from vstruct.primitives import v_uint32
from vstruct.primitives import v_wstr
from vstruct.primitives import v_enum


PATCH_ACTIONS = v_enum()
PATCH_ACTIONS.PATCH_REPLACE = 0x2
PATCH_ACTIONS.PATCH_MATCH = 0x4

MAX_MODULE = 32


# from: https://github.com/evil-e/sdb-explorer/blob/master/sdb.h
class PATCHBITS(VStruct):
    def __init__(self):
        VStruct.__init__(self)
        self.opcode = v_uint32(enum=PATCH_ACTIONS)
        self.action_size = v_uint32()  # size of entire structure
        self.pattern_size = v_uint32()  # size of pattern field
        self.rva = v_uint32()
        self.unknown = v_uint32()
        self.module_name = v_wstr(size=MAX_MODULE)
        self.pattern = v_bytes(size=0)

    def pcb_pattern_size(self):
        if self.pattern_size > 0x10000:
            print("warning: pattern_size probably incorrect")
            self["pattern"].vsSetLength(0x10000)
        else:
            self["pattern"].vsSetLength(self.pattern_size)
