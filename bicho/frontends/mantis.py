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
# Authors:  Ronaldo Maia                <romaia@async.com.br>
#

from BeautifulSoup import BeautifulSoup
import urllib

from bicho.domain import Change, Attachment, Comment
from bicho.frontends.baseparser import BaseParser, str_to_date
from bicho.frontends.utils import url_get_attr
from bicho.interfaces import Frontend, register_interface

class MantisParser(BaseParser):
    paths = dict(
        bug_id      = '/html/body/table[3]/tbody/tr[3]/td',
        summary     = '/html/body/table[3]/tbody/tr[13]/td[2]',
        description = '/html/body/table[3]/tbody/tr[14]/td[2]',
        reporter    = '/html/body/table[3]/tbody/tr[5]/td[2]',
        priority    = '/html/body/table[3]/tbody/tr[7]/td[2]',
        status      = '/html/body/table[3]/tbody/tr[8]/td[2]',
        resolution  = '/html/body/table[3]/tbody/tr[7]/td[4]',
        assignee    = '/html/body/table[3]/tbody/tr[6]/td[2]',
        category    = '',
        group       = '',
        open_date   = '/html/body/table[3]/tbody/tr[3]/td[5]',
        last_changed = '/html/body/table[3]/tbody/tr[3]/td[6]',
    )

    field_map = {
        'Status': u'status',
        'Resolution': u'resolution',
        'Assigned To': u'assignee',
    }

    status_map = {
        'new': u'NEW',
        'assigned': u'ASSIGNED',
    }

    resolution_map = {
    }

    def get_summary(self, soup):
        summary = self.xpath(self.paths['summary'], soup).contents[0].strip()
        return summary.split(': ')[1]

    def get_comments(self, soup):
        cmts = soup.findAll(lambda tag: tag.get('class', '').strip() ==
                                                        u'bugnote')
        who_path = 'td'
        cmt_path = 'td[2]'
        comments = []

        for cmt in cmts:
            who = list(self.xpath(who_path, cmt))
            person = who[5].strip()
            date = who[10].contents[0].strip()

            cmt = self.xpath(cmt_path, cmt)
            self.remove_br(cmt)
            text = cmt.contents[0]

            comments.append(Comment(person=person,
                                    date=str_to_date(date),
                                    comment=text))
        return comments

    def get_changes(self, soup):
        div = soup.findAll(lambda tag: tag.get('id', '').strip() ==
                                                        u'history_open')
        if not div:
            return []

        cmts = div[0].findAll('tr')
        who_path = 'td'
        cmt_path = 'td[2]'
        changes = []

        for cmt in cmts[2:]:
            tds = cmt.findAll('td')
            values = tds[3].contents[0].strip()
            if values.find('=&gt;') == -1:
                continue

            old, new = values.split('=&gt;')
            date = tds[0].contents[0].strip()
            person = tds[1].contents[0].strip()
            field = tds[2].contents[0].strip()

            field, old, new = self._sanityze_change(field, old, new)

            changes.append(Change(person=person,
                                  date=str_to_date(date),
                                  field=field,
                                  old_value=old,
                                  new_value=new))
        return changes

    def get_attachments(self, soup):
        Attachment
        return []

    @classmethod
    def get_bug_links(cls, html):
        soup = BeautifulSoup(html)
        cls.remove_comments(soup)

        bugs = set()
        links = soup.findAll('a')

        for link in links:
            url_str = str(link.get('href'))

            if url_str.startswith('view.php?'):
                bugs.add(url_get_attr(url_str, 'id'))

        return bugs

    @classmethod
    def get_total_bugs(cls, html):
        soup = BeautifulSoup(html)
        path = '/html/body/div/div[2]/form/div/div[2]'
        path = '/html/body/form/table/tbody/tr/td'
        pager = cls.xpath(path, soup)
        total_bugs = pager.contents[0].split(' ')[6].split(')')[0]
        return int(total_bugs)


class MantisFrontend(Frontend):
    required_fields = ['project', 'domain', 'query']
    parser_class = MantisParser

    def prepare(self):
        domain = self.options['domain']
        query = self.options['query']

        url = urllib.basejoin(domain, 'csv_export.php') + '?%s' % query
        data = self.read_page(url)
        lines = data.split('\n')[1:]
        print len(lines)
        self.bugs = [line.split(',')[0] for line in lines]

    def get_bug_url(self, bug_id):
        domain = "http://www.mantisbt.org/demo"
        bug_url = "%s/view.php?id=%s" % (domain, bug_id)
        return bug_url


register_interface("mantis", MantisFrontend)

if __name__ == "__main__":
    fname = 'samples/mantis3.html'
    cont = file(fname).read()

    parser = MantisParser()
    parser.set_html(cont)
    bug = parser.parse_bug()

    print bug
    for change in bug.comments:
        print change

    for change in bug.changes:
        print change



