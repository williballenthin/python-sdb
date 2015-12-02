import logging
import sys

import vstruct
from vstruct.primitives import *

g_logger = logging.getLogger("sdb")


class InvalidSDBFileError(Exception):
    pass


class SDBHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.unknown0 = v_uint32()
        self.unknown1 = v_uint32()
        self.magic = v_str(size=4)

    def pcb_magic(self):
        if self.magic != "sdbf":
            raise InvalidSDBFileError("invalid magic")


SDB_TAG_TYPES = v_enum()
SDB_TAG_TYPES.TAG_TYPE_NULL = 0x1000
SDB_TAG_TYPES.TAG_TYPE_WORD = 0x3000
SDB_TAG_TYPES.TAG_TYPE_DWORD = 0x4000
SDB_TAG_TYPES.TAG_TYPE_QWORD = 0x5000
SDB_TAG_TYPES.TAG_TYPE_STRINGREF = 0x6000
SDB_TAG_TYPES.TAG_TYPE_LIST = 0x7000
SDB_TAG_TYPES.TAG_TYPE_STRING = 0x8000
SDB_TAG_TYPES.TAG_TYPE_BINARY = 0x9000
SDB_KNOWN_TAG_TYPES = SDB_TAG_TYPES._vs_reverseMap.keys()

SDB_TAGS = v_enum()
SDB_TAGS.TAG_DATABASE = (0x1 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_LIBRARY = (0x2 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_INEXCLUDE = (0x3 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_SHIM = (0x4 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_PATCH = (0x5 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_APP = (0x6 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_EXE = (0x7 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_MATCHING_FILE = (0x8 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_SHIM_REF = (0x9 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_PATCH_REF = (0xA | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_LAYER = (0xB | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_FILE = (0xC | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_APPHELP = (0xD | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_LINK = (0xE | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_DATA = (0xF | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_MSI_TRANSFORM = (0x10 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_MSI_TRANSFORM_REF = (0x11 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_MSI_PACKAGE = (0x12 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_FLAG = (0x13 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_MSI_CUSTOM_ACTION = (0x14 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_FLAG_REF = (0x15 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_ACTION = (0x16 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_LOOKUP = (0x17 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_STRINGTABLE = (0x801 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_INDEXES = (0x802 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_INDEX = (0x803 | SDB_TAG_TYPES.TAG_TYPE_LIST)
SDB_TAGS.TAG_NAME = (0x1 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_DESCRIPTION = (0x2 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_MODULE = (0x3 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_API = (0x4 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_VENDOR = (0x5 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_APP_NAME = (0x6 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_COMMAND_LINE = (0x8 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_COMPANY_NAME = (0x9 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_DLLFILE = (0xA | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_WILDCARD_NAME = (0xB | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_PRODUCT_NAME = (0x10 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_PRODUCT_VERSION = (0x11 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_FILE_DESCRIPTION = (0x12 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_FILE_VERSION = (0x13 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_ORIGINAL_FILENAME = (0x14 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_INTERNAL_NAME = (0x15 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_LEGAL_COPYRIGHT = (0x16 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_16BIT_DESCRIPTION = (0x17 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_APPHELP_DETAILS = (0x18 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_LINK_URL = (0x19 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_LINK_TEXT = (0x1A | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_APPHELP_TITLE = (0x1B | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_APPHELP_CONTACT = (0x1C | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_SXS_MANIFEST = (0x1D | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_DATA_STRING = (0x1E | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_MSI_TRANSFORM_FILE = (0x1F | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_16BIT_MODULE_NAME = (0x20 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_LAYER_DISPLAYNAME = (0x21 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_COMPILER_VERSION = (0x22 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_ACTION_TYPE = (0x23 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_EXPORT_NAME = (0x24 | SDB_TAG_TYPES.TAG_TYPE_STRINGREF)
SDB_TAGS.TAG_SIZE = (0x1 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_OFFSET = (0x2 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_CHECKSUM = (0x3 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_SHIM_TAGID = (0x4 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PATCH_TAGID = (0x5 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_MODULE_TYPE = (0x6 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VERDATEHI = (0x7 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VERDATELO = (0x8 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VERFILEOS = (0x9 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VERFILETYPE = (0xA | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PE_CHECKSUM = (0xB | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PREVOSMAJORVER = (0xC | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PREVOSMINORVER = (0xD | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PREVOSPLATFORMID = (0xE | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PREVOSBUILDNO = (0xF | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PROBLEMSEVERITY = (0x10 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_LANGID = (0x11 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VER_LANGUAGE = (0x12 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_ENGINE = (0x14 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_HTMLHELPID = (0x15 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_INDEX_FLAGS = (0x16 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_FLAGS = (0x17 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_DATA_VALUETYPE = (0x18 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_DATA_DWORD = (0x19 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_LAYER_TAGID = (0x1A | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_MSI_TRANSFORM_TAGID = (0x1B | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_LINKER_VERSION = (0x1C | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_LINK_DATE = (0x1D | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_UPTO_LINK_DATE = (0x1E | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_OS_SERVICE_PACK = (0x1F | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_FLAG_TAGID = (0x20 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_RUNTIME_PLATFORM = (0x21 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_OS_SKU = (0x22 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_OS_PLATFORM = (0x23 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_APP_NAME_RC_ID = (0x24 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VENDOR_NAME_RC_ID = (0x25 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_SUMMARY_MSG_RC_ID = (0x26 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_VISTA_SKU = (0x27 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_DESCRIPTION_RC_ID = (0x28 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_PARAMETER1_RC_ID = (0x29 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_TAGID = (0x801 | SDB_TAG_TYPES.TAG_TYPE_DWORD)
SDB_TAGS.TAG_STRINGTABLE_ITEM = (0x801 | SDB_TAG_TYPES.TAG_TYPE_STRING)
SDB_TAGS.TAG_INCLUDE = (0x1 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_GENERAL = (0x2 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_MATCH_LOGIC_NOT = (0x3 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_APPLY_ALL_SHIMS = (0x4 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_USE_SERVICE_PACK_FILES = (0x5 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_MITIGATION_OS = (0x6 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_BLOCK_UPGRADE = (0x7 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_INCLUDEEXCLUDEDLL = (0x8 | SDB_TAG_TYPES.TAG_TYPE_NULL)
SDB_TAGS.TAG_TIME = (0x1 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_BIN_FILE_VERSION = (0x2 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_BIN_PRODUCT_VERSION = (0x3 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_MODTIME = (0x4 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_MASK_KERNEL = (0x5 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_UPTO_BIN_PRODUCT_VERSION = (0x6 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_DATA_QWORD = (0x7 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_MASK_USER = (0x8 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAGS_NTVDM1 = (0x9 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAGS_NTVDM2 = (0xA | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAGS_NTVDM3 = (0xB | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_MASK_SHELL = (0xC | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_UPTO_BIN_FILE_VERSION = (0xD | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_MASK_FUSION = (0xE | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_PROCESSPARAM = (0xF | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_LUA = (0x10 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_FLAG_INSTALL = (0x11 | SDB_TAG_TYPES.TAG_TYPE_QWORD)
SDB_TAGS.TAG_PATCH_BITS = (0x2 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_FILE_BITS = (0x3 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_EXE_ID = (0x4 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_DATA_BITS = (0x5 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_MSI_PACKAGE_ID = (0x6 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_DATABASE_ID = (0x7 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_INDEX_BITS = (0x801 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_APP_ID = (0x11 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_FIX_ID = (0x10 | SDB_TAG_TYPES.TAG_TYPE_BINARY)
SDB_TAGS.TAG_MATCH_MODE = (0x1 | SDB_TAG_TYPES.TAG_TYPE_WORD)
SDB_TAGS.TAG_TAG = (0x801 | SDB_TAG_TYPES.TAG_TYPE_WORD)
SDB_TAGS.TAG_INDEX_TAG = (0x802 | SDB_TAG_TYPES.TAG_TYPE_WORD)
SDB_TAGS.TAG_INDEX_KEY = (0x803 | SDB_TAG_TYPES.TAG_TYPE_WORD)

SDB_KNOWN_TAGS = set([c & 0xFF for c in SDB_TAGS._vs_reverseMap.keys()])


class SDBItemHeader(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.tagtype = v_uint8()
        self.valuetype = v_uint8()

    @property
    def tag(self):
        return (self.valuetype << 8) | self.tagtype

    def __str__(self):
        return "SDBItemHeader(tagtype: 0x%x, valuetype: 0x%x)" % (self.tagtype, self.valuetype)


class SDBItemArray(vstruct.VArray):
    def __init__(self, size=0):
        """
        size is number of bytes this array takes up
        """
        vstruct.VArray.__init__(self)
        self.size = size

    def vsSetLength(self, size):
        self.size = size

    def vsParse(self, bytez, offset=0):
        # we have to override vsParse since we have
        #   variably sized items, and have to keep
        #   parsing them until we overrun the prescribed
        #   buffer
        start_offset = offset
        while offset - start_offset < self.size:
            i = SDBItem()
            offset = i.vsParse(bytez, offset=offset)
            self.vsAddElement(i)
        return offset

    def __len__(self):
        return self.size + 0x4


class SDBValueList(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.children = SDBItemArray()

    def pcb_size(self):
        self["children"].vsSetLength(self.size)

    def __len__(self):
        return self.size + (self.size % 2) + 0x4


class SDBValueString(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.value = v_wstr(size=0)

    def pcb_size(self):
        self["value"].vsSetLength(self.size)

    def __len__(self):
        return self.size + 0x4


class SDBValueBinary(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.size = v_uint32()
        self.value = v_bytes(size=0)

    def pcb_size(self):
        self["value"].vsSetLength(self.size)

    def __len__(self):
        return self.size + (self.size % 2) + 0x4


class SDBValueNull(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)


class SDBValueWord(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.value = v_uint16()


class SDBValueDword(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.value = v_uint32()


class SDBValueQword(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.value = v_uint64()


class SDBValueStringRef(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.reference = v_uint32()


def getItemClass(header):
    m = (header.valuetype & 0xF0) << 8
    if m == SDB_TAG_TYPES.TAG_TYPE_LIST:
        return SDBValueList
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRINGREF:
        return SDBValueStringRef
    elif m == SDB_TAG_TYPES.TAG_TYPE_DWORD:
        return SDBValueDword
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRING:
        return SDBValueString
    elif m == SDB_TAG_TYPES.TAG_TYPE_NULL:
        return SDBValueNull
    elif m == SDB_TAG_TYPES.TAG_TYPE_QWORD:
        return SDBValueQword
    elif m == SDB_TAG_TYPES.TAG_TYPE_BINARY:
        return SDBValueBinary
    elif m == SDB_TAG_TYPES.TAG_TYPE_WORD:
        return SDBValueWord
    else:
        raise RuntimeError("Unexpected itemtype: 0x%x" % header.valuetype)


class SDBItem(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        # this is what we *should* have
        # however, empirically, it seems there are occasionally
        #   junk bytes in the file. we can only detect this by
        #   peeking at two bytes (tag type, value type) and checking
        #   our list of known tag combos, while possibly not consuming
        #   those bytes.
        # so, we stuff the parsing logic in vsParse
        #
        # self.header = SDBItemHeader()
        # self.value = SDBValueNULL()

    def vsParse(self, bytez, offset=0):
        b1 = bytez[offset]
        b2 = bytez[offset+1]

        if b1 not in SDB_KNOWN_TAGS and (b2 & 0xF0) << 8 not in SDB_KNOWN_TAG_TYPES:
            g_logger.warning("ignoring byte [offset=%s]: 0x%02x 0x%02x",
                    hex(offset), b1, b2)
            self.vsAddField("unknown", v_uint8())
        else:
            self.vsAddField("header", SDBItemHeader())
            self.vsAddField("value", SDBValueNull())

        # copied from vstruct
        for fname in self._vs_fields:
            fobj = self._vs_values.get(fname)
            offset = fobj.vsParse(bytez, offset=offset)
            self._vsFireCallbacks(fname)
        return offset

    def pcb_header(self):
        c = getItemClass(self.header)
        self.vsSetField("value", c())

    def __str__(self):
        return "SDBItem(tag: 0x%x, type: %s)" % (self.header.tag,
                                               self["value"].__class__.__name__)


class SDB(vstruct.VStruct):
    def __init__(self):
        vstruct.VStruct.__init__(self)
        self.header = SDBHeader()
        self.indexes_root = SDBItem()
        self.database_root = SDBItem()
        self.strtab_root = SDBItem()
