import sys
import logging

from sdb_dump_common import isBadItem
from sdb_dump_common import getTagName
from sdb_dump_common import formatValue
from sdb_dump_common import formatValueType
from sdb_dump_common import SdbIndex
from sdb import SDB_TAG_TYPES

logging.basicConfig()
g_logger = logging.getLogger("sdb_dump_database")
g_logger.setLevel(logging.WARN)


class SdbDatabaseDumper(object):
    def __init__(self, sdb):
        self._sdb = sdb
        self._strindex = SdbIndex()
        self._strindex.index_sdb(sdb)

    def _formatValue(self, item):
        m = (item.header.valuetype & 0xF0) << 8
        if m == SDB_TAG_TYPES.TAG_TYPE_STRINGREF:
            ref = item.value.reference
            return self._strindex.get_string(ref)
        else:
            return formatValue(item)

    def _dump_item(self, item, indent=""):
        if isBadItem(item):
            return

        v = item.value
        if v.vsHasField("children"):
            yield u"{indent:s}<{tag:s}>".format(
                indent=indent,
                tag=getTagName(item.header))

            for _, c in v.children:
                if isBadItem(c):
                    continue
                for l in self._dump_item(c, indent + "  "):
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

    def dump(self):
        if self._strindex is None:
            self._build_string_index()

        for i in self._dump_item(self._sdb.database_root):
            yield i


def _main(sdb_path):
    from sdb import SDB

    with open(sdb_path, "rb") as f:
        buf = f.read()

    s = SDB()
    s.vsParse(bytearray(buf))

    d = SdbDatabaseDumper(s)
    for l in d.dump():
        sys.stdout.write(l.encode("utf-8"))
        sys.stdout.write("\n")


def main():
    import sys
    return sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
