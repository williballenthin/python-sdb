import hashlib

from lxml import etree


def strip_comments(tree):
    # via: http://stackoverflow.com/a/10437575/87207
    comments = tree.xpath('//comment()')

    for c in comments:
        p = c.getparent()
        p.remove(c)


def tree_cmp(a, b):
    # sorting precendence:
    #  - no children before has children
    #  - tag name, alphanumerically
    #  - if no children, by value 
    #  - if children, by number of children
    #  - if children, by children values
    if len(a) != len(b):
        if len(a) == 0:
            return -1
        elif len(b) == 0:
            return 1

    if a.tag != b.tag:
        return cmp(a.tag, b.tag)

    if len(a) == 0:
        return cmp(a.text, b.text)
    else:
        if len(a) != len(b):
            return cmp(len(a), len(b))
        else:
            return cmp(etree.tostring(a, method="text", encoding="UTF-8"),
                       etree.tostring(b, method="text", encoding="UTF-8"))


def sort_tree(tree):
    for child in tree:
        sort_tree(child)

    # `cmp` is python 2.x only
    sorted_children = sorted(tree, cmp=tree_cmp)
    for child in tree:
        tree.remove(child)
    for child in reversed(sorted_children):
        tree.insert(0, child)


TEST_XML = """<?xml version="1.0" encoding="UTF-8"?>
<_>
<b>b</b>
<a><a>b</a></a>
<a><a>a</a></a>
<a>b</a>
<a>a</a>
</_>"""

# expected output:
"""
<_>
  <a>a</a>
  <a>b</a>
  <b>b</b>
  <a>
    <a>a</a>
  </a>
  <a>
    <a>b</a>
  </a>
</_>
"""


def _main(xml_path):
    with open(xml_path, "rb") as f:
        xml = f.read()

    # `remove_blank_text` is lxml only
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.fromstring(xml, parser=parser)
    #tree = etree.fromstring(TEST_XML, parser=parser)

    strip_comments(tree)
    sort_tree(tree)

    for exe in tree.iterfind("EXE"):
        #print(etree.tostring(exe, pretty_print=True, encoding="UTF-8"))
        name = exe.find("NAME").text
        app_name = exe.find("APP_NAME").text
        exe_id = exe.find("EXE_ID").text
        exe_xml = etree.tostring(exe, method="xml", encoding="UTF-8")
        m = hashlib.md5()
        m.update(exe_xml)
        print("%s|%s|%s|%s" % (exe_id,
                               app_name.encode("UTF-8"),
                               name.encode("UTF-8"),
                               m.hexdigest()))


def main():
    import sys
    return sys.exit(_main(*sys.argv[1:]))


if __name__ == "__main__":
    main()
