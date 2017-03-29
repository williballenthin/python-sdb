import sys
import logging
import binascii
from datetime import datetime

import sdb
from sdb import SDB_TAGS
from sdb import SDB_TAG_TYPES
from sdb_dump_common import isBadItem
from sdb_dump_common import getTagName
from sdb_dump_common import formatValue
from sdb_dump_common import formatValueType
from sdb_dump_common import SdbIndex
from sdb_dump_common import item_get_child
from sdb_dump_common import formatGuid


logging.basicConfig(level=logging.DEBUG)
g_logger = logging.getLogger("sdb_dump_info")
g_logger.setLevel(logging.DEBUG)


def parse_windows_timestamp(i):
    return datetime.utcfromtimestamp(float(i) * 1e-7 - 11644473600).isoformat("T")


class SdbInfoDumper(object):
    def __init__(self, db):
        self._db = db
        self._index = SdbIndex()
        g_logger.debug("indexing strings")
        self._index.index_sdb(self._db)
        g_logger.debug("done indexing strings")

    def dump_info(self):
        name_ref = item_get_child(self._db.database_root,
                                  SDB_TAGS.TAG_NAME).value.reference
        name = self._index.get_string(name_ref)
        yield "name: %s" % name

        try:
            database_id = item_get_child(self._db.database_root,
                                         SDB_TAGS.TAG_DATABASE_ID).value.value
            database_id = formatGuid(database_id)
            yield "database id: %s" % database_id
        except KeyError:
            pass

        try:
            ts = item_get_child(self._db.database_root, SDB_TAGS.TAG_TIME).value.value
            ts = parse_windows_timestamp(ts)
            yield "timestamp: %s" % ts
        except KeyError:
            pass

        try:
            compiler_version_ref = item_get_child(self._db.database_root,
                                                  SDB_TAGS.TAG_COMPILER_VERSION).value.reference
            compiler_version = self._index.get_string(compiler_version_ref)
            yield "compiler version: %s" % compiler_version
        except KeyError:
            pass

        try:
            os_platform = hex(item_get_child(self._db.database_root,
                                             SDB_TAGS.TAG_OS_PLATFORM).value.value)
            yield "os platform: %s" % os_platform
        except KeyError:
            pass


def _main(sdb_path):
    from sdb import SDB
    with open(sdb_path, "rb") as f:
        buf = f.read()

    g_logger.debug("loading database")
    s = SDB()
    s.vsParse(bytearray(buf))
    g_logger.debug("done loading database")

    d = SdbInfoDumper(s)
    for l in d.dump_info():
        sys.stdout.write(l.encode("utf-8"))
        sys.stdout.write("\n")


def main():
    import sys
    return sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
