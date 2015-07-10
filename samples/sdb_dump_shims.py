import sys
import logging

import sdb
from sdb import SDB_TAGS
from sdb import SDB_TAG_TYPES
from sdb_dump_common import isBadItem
from sdb_dump_common import getTagName
from sdb_dump_common import formatValue
from sdb_dump_common import formatValueType

logging.basicConfig()
g_logger = logging.getLogger("sdb_dump_shims")
g_logger.setLevel(logging.DEBUG)


def item_get_child(item, child_tag):
    v = item.value
    if not v.vsHasField("children"):
        raise RuntimeError("item doesnt have children")
    for _, c in v.children:
        if isBadItem(c):
            continue
        if c.header.tag == child_tag:
            return c
    raise IndexError("failed to find child with tag %s", hex(child_tag))


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
        return self._strindex[offset]


class SdbDumper(object):
    def __init__(self, db):
        self._db = db
        self._index = SdbIndex()
        self._index.index_sdb(self._db)

    def _formatValue(self, item):
        m = (item.header.valuetype & 0xF0) << 8
        if m == SDB_TAG_TYPES.TAG_TYPE_STRINGREF:
            ref = item.value.reference
            try:
                return self._index.get_string(ref)
            except IndexError:
                return "UNRESOLVED_STRINGREF:" + hex(ref)
        else:
            return formatValue(item)

    def dump_item_array(self, items, indent=""):
        for _, c in items:
            if isBadItem(c):
                continue
            for l in self.dump_item(c, indent):
                yield l

    def dump_item(self, item, indent=""):
        if isBadItem(item):
            return

        v = item.value
        # TODO: need to also support the following reftypes
        #  - PATCH_REF
        #  - MSI_TRANSFORM_REF
        #  - FLAG_REF
        if item.header.tag == SDB_TAGS.TAG_SHIM_REF:
            ref_item = item_get_child(item, SDB_TAGS.TAG_SHIM_TAGID)
            name_item = item_get_child(item, SDB_TAGS.TAG_NAME)

            name_ref = name_item.value
            if not isinstance(name_ref, sdb.SDBValueStringRef):
                raise RuntimeError("unexpected TAG_NAME value type")
            name = self._index.get_string(name_ref.reference)

            shim_ref = ref_item.value
            if not isinstance(shim_ref, sdb.SDBValueDword):
                raise RuntimeError("unexpected SHIM_TAGID value type")
            shim_item = self._index.get_item(shim_ref.value)

            # have to hardcode the parent tag name, since the ref may point
            #   within the SHIM node
            yield u"{indent:s}<{tag:s}>".format(
                indent=indent,
                tag="SHIM")

            yield u"{indent:s}<!-- SHIM_REF name:'{name:s}' offset:{offset:s} -->".format(
                indent=indent + "  ", name=name, offset=hex(shim_ref.value))

            for l in self.dump_item_array(shim_item, indent=indent + "  "):
                yield l

            # have to hardcode the parent tag name, since the ref may point
            #   within the SHIM node
            yield u"{indent:s}</{tag:s}>".format(
                indent=indent,
                tag="SHIM")

        elif v.vsHasField("children"):
            yield u"{indent:s}<{tag:s}>".format(
                indent=indent,
                tag=getTagName(item.header))

            for l in self.dump_item_array(v.children, indent=indent+"  "):
                yield l

            yield u"{indent:s}</{tag:s}>".format(
                indent=indent,
                tag=getTagName(item.header))
        else:
            yield u"{indent:s}<{tag:s} type='{type_:s}'>{data:s}</{tag:s}>".format(
                indent=indent,
                type_=formatValueType(item),
                data=self._formatValue(item),
                tag=getTagName(item.header))


    def dump_database(self):
        for i in self.dump_item(self._db.database_root):
            yield i


def main(sdb_path):
    from sdb import SDB
    with open(sdb_path, "rb") as f:
        buf = f.read()

    s = SDB()
    s.vsParse(buf)

    d = SdbDumper(s)
    for l in d.dump_database():
        sys.stdout.write(l.encode("utf-8"))
        sys.stdout.write("\n")


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
