import sys
import logging

import vstruct
import vivisect
import envi
import envi.archs.i386 as M

import sdb
from sdb import SDB_TAGS
from sdb_dump_common import SdbIndex
from sdb_dump_common import item_get_child
from sdb_dump_common import item_get_children


logging.basicConfig(level=logging.DEBUG)
g_logger = logging.getLogger("sdb_dump_patch")
g_logger.setLevel(logging.DEBUG)


def disassemble(buf, base=0):
    d = M.i386Disasm()
    offset = 0
    while True:
        if offset >= len(buf):
            break
        o = d.disasm(buf, offset, base)
        yield "0x%x: %s" % (base + offset, str(o))
        offset += o.size


class GreedyVArray(vstruct.VArray):
    def __init__(self, C):
        vstruct.VArray.__init__(self)
        self._C = C

    def vsParse(self, bytez, offset=0, fast=False):
        soffset = offset
        while offset < len(bytez):
            c = self._C()
            try:
                offset = c.vsParse(bytez, offset=offset, fast=False)
            except:
                break
            self.vsAddElement(c)
        return offset

    def vsParseFd(self, fd):
        raise NotImplementedError()


def _main(sdb_path, patch_name):
    from sdb import SDB
    with open(sdb_path, "rb") as f:
        buf = f.read()

    g_logger.debug("loading database")
    s = SDB()
    s.vsParse(bytearray(buf))
    g_logger.debug("done loading database")

    index = SdbIndex()
    g_logger.debug("indexing strings")
    index.index_sdb(s)
    g_logger.debug("done indexing strings")

    library = item_get_child(s.database_root, SDB_TAGS.TAG_LIBRARY)

    for shim_ref in item_get_children(library, SDB_TAGS.TAG_SHIM_REF):
        patch = item_get_child(shim_ref, SDB_TAGS.TAG_PATCH)
        name_ref = item_get_child(patch, SDB_TAGS.TAG_NAME)
        name = index.get_string(name_ref.value.reference)
        bits = item_get_child(patch, SDB_TAGS.TAG_PATCH_BITS)

        if name == patch_name:
            ps = GreedyVArray(sdb.PATCHBITS)
            ps.vsParse(bits.value.value)

            for i, _ in ps:
                p = ps[int(i)]
                print(p.tree())
                print("  disassembly:")
                for l in disassemble(str(p.pattern), p.rva):
                    print("    " + l)
                print("")


def main():
    import sys
    return sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
