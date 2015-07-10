import base64
import binascii
import logging

from sdb import SDB_TAGS
from sdb import SDB_TAG_TYPES

logging.basicConfig()
g_logger = logging.getLogger("sdb_dump_common")
g_logger.setLevel(logging.WARN)


def getTagName(header):
    tagname = SDB_TAGS.vsReverseMapping(header.tag)
    if tagname is None:
        return "UNKNOWN_%s" % (hex(header.tag & 0xFF0F))
    return str(tagname.partition("TAG_")[2])


def formatGuid(h):
    return "%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x" % \
        (h[3], h[2], h[1], h[0],
        h[5], h[4],
        h[7], h[6],
        h[8], h[9],
        h[10], h[11], h[12], h[13], h[14], h[15])


def formatValue(item):
    m = (item.header.valuetype & 0xF0) << 8
    if m == SDB_TAG_TYPES.TAG_TYPE_LIST:
        raise RuntimeError("cannot format complex TAG_TYPE_LIST")
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRINGREF:
        return hex(item.value.reference)
    elif m == SDB_TAG_TYPES.TAG_TYPE_DWORD:
        return hex(item.value.value)
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRING:
        return item.value.value
    elif m == SDB_TAG_TYPES.TAG_TYPE_NULL:
        return ""
    elif m == SDB_TAG_TYPES.TAG_TYPE_QWORD:
        return hex(item.value.value)
    elif m == SDB_TAG_TYPES.TAG_TYPE_WORD:
        return hex(item.value.value)
    elif m == SDB_TAG_TYPES.TAG_TYPE_BINARY:
        # we're just guessing here ;-)
        if item.value.size == 0x10 and getTagName(item.header).endswith("_ID"):
            return formatGuid(item.value.value)
        else:
            return str(binascii.hexlify(item.value.value))
    else:
        raise RuntimeError("cannot format unknown value type: 0x%x", item.header.valuetype)


def formatValueType(item):
    m = (item.header.valuetype & 0xF0) << 8
    if m == SDB_TAG_TYPES.TAG_TYPE_LIST:
        raise RuntimeError("cannot format complex TAG_TYPE_LIST")
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRINGREF:
        return "stringref"
    elif m == SDB_TAG_TYPES.TAG_TYPE_DWORD:
        return "integer"
    elif m == SDB_TAG_TYPES.TAG_TYPE_STRING:
        return "string"
    elif m == SDB_TAG_TYPES.TAG_TYPE_NULL:
        return "null"
    elif m == SDB_TAG_TYPES.TAG_TYPE_QWORD:
        return "integer"
    elif m == SDB_TAG_TYPES.TAG_TYPE_WORD:
        return "integer"
    elif m == SDB_TAG_TYPES.TAG_TYPE_BINARY:
        tag = (item.header.valuetype << 8) | item.header.tagtype
        if tag == SDB_TAGS.TAG_DATABASE_ID:
            return "guid"
        else:
            return "hex"
    else:
        raise RuntimeError("cannot format unknown value type: 0x%x", item.header.valuetype)


def isBadItem(item):
    return item.vsHasField("unknown")
