import sys
import logging

import sdb
from sdb import SDB_TAGS
from sdb import SDB_TAG_TYPES
from sdb_dump_common import isBadItem
from sdb_dump_common import getTagName
from sdb_dump_common import formatValue
from sdb_dump_common import formatValueType
from sdb_dump_common import SdbIndex
from sdb_dump_common import item_get_child

logging.basicConfig()
g_logger = logging.getLogger("sdb_dump_shims")
g_logger.setLevel(logging.INFO)


class SdbShimDumper(object):
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
            # have to hardcode the parent tag name, since the ref may point
            #   within the SHIM node
            yield u"{indent:s}<{tag:s}>".format(
                indent=indent,
                tag="SHIM")

            ref_item = None
            name_item = None
            try:
                ref_item = item_get_child(item, SDB_TAGS.TAG_SHIM_TAGID)
            except KeyError:
                yield u"{indent:s}<!-- SHIM_REF missing SHIM_TAGID -->".format(
                    indent=indent + "  ")
                g_logger.debug("SHIM_REF missing SHIM_TAGID")

            try:
                name_item = item_get_child(item, SDB_TAGS.TAG_NAME)
            except KeyError:
                yield u"{indent:s}<!-- SHIM_REF missing NAME -->".format(
                    indent=indent + "  ")
                g_logger.debug("SHIM_REF missing NAME")

            if ref_item and name_item:
                name_ref = name_item.value
                if not isinstance(name_ref, sdb.SDBValueStringRef):
                    raise RuntimeError("unexpected TAG_NAME value type")
                name = self._index.get_string(name_ref.reference)

                shim_ref = ref_item.value
                if not isinstance(shim_ref, sdb.SDBValueDword):
                    raise RuntimeError("unexpected SHIM_TAGID value type")
                shim_item = self._index.get_item(shim_ref.value)

                yield u"{indent:s}<!-- SHIM_REF name:'{name:s}' offset:{offset:s} -->".format(
                    indent=indent + "  ", name=name, offset=hex(shim_ref.value))

                for l in self.dump_item_array(shim_item, indent=indent + "  "):
                    yield l
            else:
                yield u"{indent:s}<!-- unresolved SHIM_REF -->".format(
                    indent=indent + "  ")
                g_logger.debug("unresolved SHIM_REF")

                if name_item:
                    name_ref = name_item.value
                    if not isinstance(name_ref, sdb.SDBValueStringRef):
                        raise RuntimeError("unexpected TAG_NAME value type")
                    name = self._index.get_string(name_ref.reference)
                    yield u"{indent:s}<!-- SHIM_REF name:'{name:s}' -->".format(
                        indent=indent + "  ", name=name)

                if ref_item:
                    shim_ref = ref_item.value
                    if not isinstance(shim_ref, sdb.SDBValueDword):
                        raise RuntimeError("unexpected SHIM_TAGID value type")
                    shim_item = self._index.get_item(shim_ref.value)
                    yield u"{indent:s}<!-- SHIM_REF offset:'{offset:s}' -->".format(
                        indent=indent + "  ", offset=hex(shim_ref.value))

            # have to hardcode the parent tag name, since the ref may point
            #   within the SHIM node
            yield u"{indent:s}</{tag:s}>".format(
                indent=indent,
                tag="SHIM")

        elif v.vsHasField("children"):
            yield u"{indent:s}<{tag:s}>".format(
                indent=indent,
                tag=getTagName(item.header))

            for l in self.dump_item_array(v.children, indent=indent + "  "):
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
        yield '<?xml version="1.0" encoding="UTF-8"?>'
        for i in self.dump_item(self._db.database_root):
            yield i


def _main(sdb_path):
    from sdb import SDB
    with open(sdb_path, "rb") as f:
        buf = f.read()

    s = SDB()
    try:
        s.vsParse(bytearray(buf))
    except sdb.InvalidSDBFileError:
        g_logger.error("not an SDB file: %s" % (sdb_path))
        return -1

    d = SdbShimDumper(s)
    for l in d.dump_database():
        sys.stdout.write(l.encode("utf-8"))
        sys.stdout.write("\n")


def main():
    import sys
    return sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
