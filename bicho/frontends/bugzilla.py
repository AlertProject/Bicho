# Copyright (C) 2008  GSyC/LibreSoft
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.es>
#          Ronaldo Francisco Maia       <romaia@async.com.br>
#

import urllib
import datetime
from BeautifulSoup import BeautifulSoup

from bicho.domain import Change, Comment
from bicho.frontends.baseparser import BaseParser
from bicho.frontends.utils import get_domain
from bicho.interfaces import Frontend, register_interface
from bicho.utils import debug

def date_from_bz(string):
    date, time, tz = string.split(' ')
    params = [int(i) for i in date.split('-') + time.split(':')]
    full_date = datetime.datetime(*params)
    return full_date

class BugzillaParser(BaseParser):
    paths = dict(
        bug_id      = '/bugzilla/bug/bug_id',
        description = '/bugzilla/bug/long_desc[0]/thetext',
        summary     = '/bugzilla/bug/short_desc',
        reporter    = '/bugzilla/bug/reporter',
        priority    = '/bugzilla/bug/priority',
        severity    = '/bugzilla/bug/bug_severity',
        status      = '/bugzilla/bug/bug_status',
        resolution  = '/bugzilla/bug/resolution',
        open_date   = '/bugzilla/bug/creation_ts',
        assignee    = '/bugzilla/bug/assigned_to',
        category    = '/bugzilla/bug/bug_severity',     # ?
        group       = '/bugzilla/bug/component',        # ?
        last_changed = '/bugzilla/bug/delta_ts'
    )

    converter = dict(
        bug_id=int,
        open_date = date_from_bz,
        last_changed = date_from_bz,
    )

    field_map = {
        'Status': u'status',
        'Resolution': u'resolution',
    }


    domain = None

    def get_comments(self, soup):
        cmts = soup.findAll('long_desc')
        comments = []
        for c in cmts[1:]:
            person = self.xpath('/who', c).contents[0].strip()
            date = date_from_bz(self.xpath('/bug_when', c).contents[0])
            text = self.xpath('/thetext', c).contents[0].strip()
            comments.append(Comment(person=person,
                                    date=date, comment=text))
        return comments

    def get_changes(self, soup):
        if not self.domain:
            return []

        bug_id = self.xpath(self.paths['bug_id'], soup).contents[0]
        activity_url = "%sshow_activity.cgi?id=%s" % (self.domain, bug_id)
        debug("Analysing activity %s" % activity_url)
        data = urllib.urlopen(activity_url).read()
        return self.parse_changes(data)

    def get_attachments(self, soup):
        return []

    @classmethod
    def parse_changes(cls, html):
        soup = BeautifulSoup(html)
        cls.remove_comments(soup)
        remove_tags = ['a', 'span']
        [i.replaceWith(i.contents[0]) for i in soup.findAll(remove_tags)]
        changes = []

        tables = soup.findAll('table')
        # We need the first table with 5 cols in the first line
        table = None
        for table in tables:
            if len(table.tr.findAll('th')) == 5:
                break

        if table is None:
            return changes

        rows = list(table.findAll('tr'))
        for row in rows[1:]:
            cols = list(row.findAll('td'))
            if len(cols) == 5:
                person = cols[0].contents[0].strip()
                person = person.replace('&#64;', '@')
                date = date_from_bz(cols[1].contents[0].strip())
                field = cols[2].contents[0].strip()
                removed = cols[3].contents[0].strip()
                added = cols[4].contents[0].strip()
            else:
                field = cols[0].contents[0].strip()
                removed = cols[1].contents[0].strip()
                added = cols[2].contents[0].strip()

            field, removed, added = cls._sanityze_change(field, removed,
                                                          added)

            change = Change(person=person, date=date, field=field,
                            old_value=removed, new_value=added)
            changes.append(change)

        return changes


class BugzillaFrontend(Frontend):
    required_fields = ['project', 'url']
    parser_class = BugzillaParser

    def get_bug_url(self, bug_id):
        return "%sshow_bug.cgi?id=%s&ctype=xml" % (self.domain, bug_id)

    def prepare(self):
        self.url = self.options['url']
        self.fast = self.options['fast'] == '1'
        self.domain = get_domain(self.url)
        self.parser.domain = self.domain

        data = self.read_page(self.url + "&ctype=csv")
        lines = data.split('\n')[1:]
        self.bugs = [line.split(',')[0] for line in lines]


register_interface("bugzilla", BugzillaFrontend)

if __name__ == '__main__':
    #url = "http://bugs.async.com.br/"
    #data = BugzillaFrontend.analyze_bug_page(3912, url)

    fname = 'samples/bz.xml'
    cont = file(fname).read()

    parser = BugzillaParser(cont)
    bug = parser.parse_bug()
    print bug

    fname = 'samples/bz_changes3.html'
    cont = file(fname).read()
    changes = BugzillaParser.parse_changes(cont)
    print len(changes)
    for change in changes:
        print change

