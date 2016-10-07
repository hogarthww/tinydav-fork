# Unittests for creator module.
# Copyright (C) 2009  Manuel Hermann <manuel-hermann@gmx.net>
#
# This file is part of tinydav.
#
# tinydav is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Unittests for creator module."""

from xml.etree.ElementTree import Element
import sys
import unittest

from tinydav import creator

PYTHONVERSION = sys.version_info[:2]  # (2, 5) or (2, 6)


class TestAddNamespaces(unittest.TestCase):
    """Test creator._addnamespaces."""

    def test_addnamespaces(self):
        """Test creator._addnamespaces."""
        namespaces = {"a": "ABC:", "b": "XXX:"}
        element = Element("foo")
        creator._addnamespaces(element, namespaces)
        expect = {"xmlns:b": "XXX:", "xmlns:a": "ABC:"}
        self.assertEqual(element.attrib, expect)


class TestCreatePropFind(unittest.TestCase):
    """Test creator.create_propfind function."""

    def test_create_propfind(self):
        """Test WebDAVClient._create_propfind."""
        # allprops
        xml = creator.create_propfind(False, None, None, None)
        self.assertEqual(xml, b'<propfind xmlns="DAV:"><allprop /></propfind>')
        # names only
        xml = creator.create_propfind(True, None, None, None)
        self.assertEqual(
            xml, b'<propfind xmlns="DAV:"><propname /></propfind>')
        # properties
        xml = creator.create_propfind(False, ["{DC:}author"], None, None)
        if PYTHONVERSION >= (2, 7):
            self.assertEqual(xml, b'<propfind xmlns:ns0="DC:" '
                                  b'xmlns="DAV:"><prop>'
                                  b'<ns0:author /></prop>'
                                  b'</propfind>')
        else:
            self.assertEqual(xml, b'<propfind xmlns="DAV:"><prop>'
                                  b'<ns0:author xmlns:ns0="DC:" /></prop>'
                                  b'</propfind>')
        # include
        xml = creator.create_propfind(False, None,
                                      ["supported-report-set"], None)
        self.assertEqual(xml, b'<propfind xmlns="DAV:"><allprop />'
                              b'<include><supported-report-set /></include>'
                              b'</propfind>')


class TestCreatePropPatch(unittest.TestCase):
    """Test creator.create_proppatch function."""

    def test_create_proppatch_set(self):
        """Test WebDAVClient._create_proppatch: set property"""
        # set only
        setprops = {"CADN:author": "me", "CADN:created": "2009-09-09 13:31"}
        ns = {"CADN": "CADN:"}
        xml = creator.create_proppatch(setprops, None, ns)
        self.assertEqual(xml, b'<propertyupdate xmlns="DAV:" xmlns:CADN="CADN:">'
                              b'<set>'
                              b'<prop>'
                              b'<CADN:created>2009-09-09 13:31'
                              b'<CADN:author>me</CADN:author>'
                              b'</CADN:created>'
                              b'</prop>'
                              b'</set>'
                              b'</propertyupdate>')

    def test_create_proppatch_remove(self):
        """Test WebDAVClient._create_proppatch: remove property"""
        # remove only
        delprops = ["DEL:xxx"]
        ns = {"DEL": "DEL:"}
        xml = creator.create_proppatch(None, delprops, ns)

        self.assertEqual(xml, b'<propertyupdate xmlns="DAV:" xmlns:DEL="DEL:">'
                              b'<remove>'
                              b'<prop><DEL:xxx /></prop>'
                              b'</remove>'
                              b'</propertyupdate>')

    def test_create_proppatch_setremove(self):
        """Test WebDAVClient._create_proppatch: set and remove property"""
        # set and del
        setprops = {"CADN:author": "me", "CADN:created": "2009-09-09 13:31"}
        delprops = ["DEL:xxx"]
        ns = {"CADN": "CADN:", "DEL": "DEL:"}
        xml = creator.create_proppatch(setprops, delprops, ns)
        self.assertEqual(xml, b'<propertyupdate xmlns="DAV:" xmlns:CADN="CADN:"'
                              b' xmlns:DEL="DEL:">'
                              b'<set>'
                              b'<prop>'
                              b'<CADN:created>2009-09-09 13:31'
                              b'<CADN:author>me</CADN:author>'
                              b'</CADN:created>'
                              b'</prop>'
                              b'</set>'
                              b'<remove>'
                              b'<prop><DEL:xxx /></prop>'
                              b'</remove>'
                              b'</propertyupdate>')


class TestCreateLock(unittest.TestCase):
    """Test creator.create_lock function."""

    def test_create_lock(self):
        """Test creator.create_lock."""
        xml = creator.create_lock()
        self.assertEqual(xml, b'<lockinfo xmlns="DAV:"><lockscope>'
                              b'<exclusive /></lockscope><locktype><write />'
                              b'</locktype></lockinfo>')

    def test_create_illegal_scope(self):
        """Test creator.create_lock with illegal scope."""
        self.assertRaises(
            ValueError,
            creator.create_lock,
            scope="everything"
        )

    def test_create_lock_owner(self):
        """Test creator.create_lock with given owner."""
        xml = creator.create_lock(owner="me")
        self.assertEqual(xml, '<lockinfo xmlns="DAV:"><lockscope><exclusive />'
                              '</lockscope><locktype><write /></locktype>'
                              '<owner>me</owner></lockinfo>')

    def test_create_lock_owner_element(self):
        """Test creator.create_lock with given owner element."""
        owner = Element("name")
        owner.text = "me"
        xml = creator.create_lock(owner=owner)
        self.assertEqual(xml, '<lockinfo xmlns="DAV:"><lockscope><exclusive />'
                              '</lockscope><locktype><write /></locktype>'
                              '<owner><name>me</name></owner></lockinfo>')


class TestCreateReport(unittest.TestCase):
    """Test creator.create_report function."""

    def test_create_version_tree_report(self):
        """Test creator.create_report_version_tree."""
        # default report
        xml = creator.create_report_version_tree()
        self.assertEqual(xml, b'<version-tree xmlns="DAV:" />')
        # properties
        xml = creator.create_report_version_tree(["creator-displayname"])
        self.assertEqual(xml, b'<version-tree xmlns="DAV:"><prop>'
                              b'<creator-displayname />'
                              b'</prop></version-tree>')
        # additional xml
        elements = [Element("foo", {"bar": "1"})]
        xml = creator.create_report_version_tree(elements=elements)
        self.assertEqual(xml, b'<version-tree xmlns="DAV:">'
                              b'<foo bar="1" /></version-tree>')

    def test_create_expand_property_report(self):
        """Test creator.create_report_version_tree."""
        # default report
        xml = creator.create_report_expand_property()
        self.assertEqual(xml, b'<expand-property xmlns="DAV:" />')
        # properties
        xml = creator.create_report_expand_property("creator-displayname")
        self.assertEqual(xml, b'<expand-property xmlns="DAV:">'
                              b'<property name="creator-displayname" />'
                              b'</expand-property>')
        # property-list
        p = ["foo", "bar"]
        xml = creator.create_report_expand_property(p)
        self.assertEqual(xml, b'<expand-property xmlns="DAV:">'
                              b'<property name="foo" />'
                              b'<property name="bar" />'
                              b'</expand-property>')
        # property-dict
        p = {
            "foo": "bar",
            "bar": ["a", "b"],
            "baz": {
                "c": None,
                "d": "e",
            }
        }
        xml = creator.create_report_expand_property(p)
        self.assertEqual(xml, b'<expand-property xmlns="DAV:">'
                              b'<property name="baz">'
                         b'<property name="c" />'
                         b'<property name="d">'
                         b'<property name="e" />'
                         b'</property>'
                              b'</property>'
                              b'<property name="foo">'
                         b'<property name="bar" />'
                              b'</property>'
                              b'<property name="bar">'
                         b'<property name="a" />'
                         b'<property name="b" />'
                              b'</property>'
                              b'</expand-property>')
        # additional xml
        elements = [Element("foo", {"bar": "1"})]
        xml = creator.create_report_expand_property(elements=elements)
        self.assertEqual(xml, b'<expand-property xmlns="DAV:">'
                              b'<foo bar="1" /></expand-property>')
