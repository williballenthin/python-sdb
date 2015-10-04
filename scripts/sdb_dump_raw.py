import sys
import logging

from sdb_dump_common import isBadItem
from sdb_dump_common import getTagName
from sdb_dump_common import formatValue
from sdb_dump_common import formatValueType

g_logger = logging.getLogger("sdb_dump_raw")


def dump_item(item, indent=""):
    if isBadItem(item):
        return

    v = item.value
    if v.vsHasField("children"):
        yield u"{indent:s}<{tag:s}>".format(
            indent=indent,
            tag=str(getTagName(item.header)))

        for _, c in v.children:
            if isBadItem(c):
                continue
            for l in dump_item(c, indent + "  "):
                yield l

        yield u"{indent:s}</{tag:s}>".format(
            indent=indent,
            tag=str(getTagName(item.header)))
    else:
        yield u"{indent:s}<{tag:s} type='{type_:s}'>{data:s}</{tag:s}>".format(
            indent=indent,
            type_=str(formatValueType(item)),
            data=formatValue(item),
            tag=str(getTagName(item.header)))


def dump(sdb):
    for i in dump_item(sdb.indexes_root):
        yield i

    for i in dump_item(sdb.database_root):
        yield i

    for i in dump_item(sdb.strtab_root):
        yield i


def _main(sdb_path):
    from sdb import SDB
    with open(sdb_path, "rb") as f:
        buf = f.read()

    s = SDB()
    s.vsParse(bytearray(buf))

    for l in dump(s):
        sys.stdout.write(l.encode("utf-8"))
        sys.stdout.write("\n")


def main():
    import sys
    sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
