import base64
import logging
import binascii
import string
import xml.sax.saxutils

from sdb import SDB_TAGS
from sdb import SDB_TAG_TYPES

g_logger = logging.getLogger("sdb_dump_common")
g_logger.setLevel(logging.DEBUG)


def getTagName(header):
    tagname = SDB_TAGS.vsReverseMapping(header.tag)
    if tagname is None:
        return "UNKNOWN_%s" % (hex(header.tag & 0xFFFF))
    tagname = str(tagname.partition("TAG_")[2])

    # valid XML cannot begin with a digit
    if tagname[0] in string.digits:
        return "_" + tagname
    else:
        return tagname


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
        return xml.sax.saxutils.escape(item.value.value)
    elif m == SDB_TAG_TYPES.TAG_TYPE_NULL:
        return ""
    elif m == SDB_TAG_TYPES.TAG_TYPE_QWORD:
        return hex(item.value.value).rstrip("L")
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


class SdbIndex(object):
    def __init__(self):
        self._itemindex = {}  # type: Mapping[int, SdbItem]
        self._strindex = {}  # type: Mapping[int, str]

    def index_sdb(self, db):
        o = len(db.header)
        indexes_root = db.indexes_root
        self._itemindex_item(o, indexes_root)
        o += len(indexes_root)

        database_root = db.database_root
        self._itemindex_item(o, database_root)
        o += len(database_root)

        strtab_root = db.strtab_root
        self._itemindex_item(o, strtab_root)
        o += len(strtab_root)

        # len(strtab) - len(strtab value) == 6
        # 01 78 ?? ?? ?? ?? (children_size:uint32)
        offset = 0x6
        for fieldname, field in db.strtab_root.value.children.vsGetFields():
            if isBadItem(field):
                offset += len(field)
                continue
            self._strindex[offset] = field.value.value
            offset += len(field)

    def _itemindex_item(self, offset, item):
        value = item.value

        # some items may have the same starting offset, so we take the first one
        # eg. given an item array, and the first item in the array, we want the array
        if offset not in self._itemindex:
            self._itemindex[offset] = item

        if value.vsHasField("children"):
            offset += value.vsGetOffset("children")
            children = value.children
            self._itemindex[offset] = children
            for child_id, child in children:
                if isBadItem(child):
                    offset += len(child)
                    continue
                # you might be tempted to use vsGetOffset(child_id)... don't.
                # internally it has to iterate all fields and do a __len__ on them,
                #   so this ends up taking quadratic time.
                # instead, we track the offset ourselves.
                self._itemindex_item(offset, child)
                offset += len(child)

    def get_item(self, offset):
        return self._itemindex[offset]

    def get_string(self, offset):
        return xml.sax.saxutils.escape(self._strindex[offset])


def item_get_children(item, child_tag):
    v = item.value
    if not v.vsHasField("children"):
        raise RuntimeError("item doesnt have children")

    for _, c in v.children:
        if isBadItem(c):
            continue
        if c.header.tag == child_tag:
            yield c


def item_get_child(item, child_tag):
    v = item.value
    if not v.vsHasField("children"):
        raise RuntimeError("item doesnt have children")
 
    for c in item_get_children(item, child_tag):
        return c
    raise IndexError("failed to find child with tag %s"  % hex(child_tag))

