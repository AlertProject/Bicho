# Copyright (C) 2007  GSyC/LibreSoft
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
# Authors:  Daniel Izquierdo Cortazar   <dizquierdo@gsyc.escet.urjc.es>
#           Ronaldo Maia                <romaia@async.com.br>
#

import re
from BeautifulSoup import BeautifulSoup

from bicho.domain import Change, Attachment, Comment
from bicho.frontends.baseparser import BaseParser, str_to_date
from bicho.frontends.utils import url_get_attr
from bicho.interfaces import Frontend, register_interface
from bicho.utils import debug


class SourceForgeParser(BaseParser):
    # FIXME: Sourceforge assignee is the full name instead of the username.
    # All other fields are the username.

    paths = dict(
        summary     = '/html/body/div/div[2]/div[4]/div/div/span[2]/strong',
        description = '/html/body/div/div[2]/div[4]/div[2]/p[1]',
        open_date    = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[1]',
        reporter    = '/html/body/div/div[2]/div[4]/div[2]/div/p/a',
        priority    = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[2]',
        status      = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[3]',
        resolution  = '/html/body/div/div[2]/div[4]/div[2]/div[1]/p[4]',
        assignee    = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[1]',
        category    = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[2]',
        group       = '/html/body/div/div[2]/div[4]/div[2]/div[2]/p[3]',
    )

    field_map = {
        'status_id': 'status',
        'resolution_id': 'resolution',
        'assigned_to': 'assignee',
    }

    # FIXME: We should have a way to detecte reponened bugs
    status_map = {
        'Open': 'OPEN',
        'Pending': 'RESOLVED', #XXX
        'Closed': 'RESOLVED',
        'Deleted': 'RESOLVED',
    }

    resolution_map = {
        'Fixed': 'FIXED',
        'Invalid': 'INVALID',
        'Duplicate': 'DUPLICATE',
        "Works For Me": 'INVALID'
        # Remind, Accepted
    }

    def get_comments(self, soup):
        cmts = soup.findAll(lambda tag: tag.get('class', '').strip() ==
                                                        u'artifact_comment')
        who_path = '/td/div/div[1]/p'
        cmt_path = '/td/div/div[2]/p'
        comments = []

        for cmt in cmts:
            who = list(self.xpath(who_path, cmts[0]))
            _, date = who[0].strip().split('Date: ')
            person = who[3].contents[0]

            cmt = self.xpath(cmt_path, cmts[0])
            self.remove_br(cmt)
            text = cmt.contents[0]
            comments.append(Comment(person=person,
                                    date=str_to_date(date),
                                    comment=text))

        return comments

    def get_changes(self, soup):
        field_path = '/td'
        old_value_path = '/td[2]'
        when_path = '/td[3]'
        person_path = '/td[4]'

        header = soup.findAll('h4', {'id': 'changebar'})[0]
        table = header.fetchNextSiblings('div')[0].table
        changes = []
        if not table:
            return changes

        rows = table.findAll('tr')
        for row in rows[1:]:
            sf_field = self.xpath(field_path, row).contents[0].strip()
            field = self.field_map.get(sf_field, sf_field)
            if not field:
                debug('IGNORING %s' % sf_field)
                continue

            if not self._cache.has_key(field):
                debug('IGNORING %s' % sf_field)
                continue

            new = self._cache[field]
            old = self.xpath(old_value_path, row).contents[0].strip()
            self._cache[field] = old

            field, old, new = self._sanityze_change(field, old, new)

            date = self.xpath(when_path, row).contents[0].strip()
            person = self.xpath(person_path, row).contents[0].strip()

            change = Change(person=person, date=str_to_date(date),
                            field=field, old_value=old, new_value=new)
            changes.append(change)

        return changes

    def get_attachments(self, soup):
        Attachment
        return []

    def get_reporter(self, soup):
        tag = self.xpath(self.paths['reporter'], soup)
        return list(tag)[0]

    def get_open_date(self, soup):
        tag = self.xpath(self.paths['open_date'], soup)
        return list(tag)[-1][6:]

    def get_summary(self, soup):
        tag = self.xpath(self.paths['summary'], soup)
        summary, bug_id = tag.contents[0].split(' - ID: ')
        return summary

    def get_bug_id(self, soup):
        tag = self.xpath(self.paths['summary'], soup)
        summary, bug_id = tag.contents[0].split(' - ID: ')
        return bug_id

    def get_description(self, soup):
        tag = self.xpath(self.paths['description'], soup)
        [t.extract() for t in tag.findAll('br')]
        return tag.contents[0]

    @classmethod
    def get_total_bugs(cls, html):
        soup = BeautifulSoup(html)
        pager = cls.xpath('/html/body/div/div[2]/form/div/div[2]', soup)
        total_bugs = int(pager.contents[0].split('&nbsp;')[4])
        return int(total_bugs)

    @classmethod
    def get_bug_links(cls, html):
        soup = BeautifulSoup(html)
        bugs = []

        links = soup.findAll('a')
        for link in links:
            url_str = str(link.get('href'))

            # Bugs URLs
            if re.search("tracker", url_str) and re.search("aid", url_str):
                bugs.append(url_get_attr(url_str, 'aid'))

        return bugs


class SourceForgeFrontend(Frontend):
    required_fields = ['project', 'group_id', 'atid']
    parser_class = SourceForgeParser
    domain = "http://sourceforge.net"

    def get_bug_url(self, bug_id):
        bug_url = "%s/tracker/?func=detail&aid=%s&group_id=%s&atid=%s" % (
                    self.domain, bug_id, self.group_id, self.atid)
        return bug_url

    def prepare(self):
        bugs = []
        urls = []

        self.group_id = self.options['group_id']
        self.atid = self.options['atid']

        url = "%s/tracker/?limit=100&group_id=%s&atid=%s" % (
                    self.domain, self.group_id, self.atid)
        html = self.read_page(url)

        urls = [url]
        #total_bugs = SourceForgeParser.get_total_bugs(html)
        #for i in xrange(0, total_bugs, 100):
        #    urls.append(url+'&offset=%s' % i)

        for url in urls:
            html = self.read_page(url)
            bugs.extend(SourceForgeParser.get_bug_links(html))

        self.bugs = bugs


register_interface("sourceforge", SourceForgeFrontend)

if __name__ == "__main__":
    #sf = "http://sourceforge.net/tracker/index.php?"
    #url = "%sfunc=detail&aid=1251682&group_id=2435&atid=102435" % sf
    #cont = urllib.urlopen(url).read()

    fname = 'samples/sf2.html'
    cont = file(fname).read()

    parser = SourceForgeParser(cont)
    bug = parser.parse_bug()

    print bug
    for change in bug.changes:
        print change



