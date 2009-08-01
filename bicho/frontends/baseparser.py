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

import datetime

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Comment as BFComment

from bicho.domain import Bug

def str_to_date(string):
    if not string:
        return

    date, time = string.split(' ')
    params = [int(i) for i in date.split('-') + time.split(':')]
    full_date = datetime.datetime(*params)
    return full_date


class BaseParser(object):
    paths = {}
    converter = {}
    field_map = {}
    status_map = {}
    resolution_map = {}

    converter = dict(
        bug_id = int,
        open_date = str_to_date,
        last_changed = str_to_date,
    )

    _cache = {}

    def __init__(self, html=None):
        if html:
            self.set_html(html)

    @classmethod
    def _sanityze_change(self, field, old_value, new_value):
        field = self.field_map.get(field, field)
        old_value = old_value.strip()
        new_value = new_value.strip()
        if field == 'status':
            old_value = self.status_map.get(old_value, old_value)
            new_value = self.status_map.get(new_value, new_value)
        elif field == 'resolution':
            old_value = self.resolution_map.get(old_value, old_value)
            new_value = self.resolution_map.get(new_value, new_value)

        return field, old_value, new_value

    @classmethod
    def remove_comments(cls, soup):
        cmts = soup.findAll(text=lambda text:isinstance(text,
                            BFComment))
        [comment.extract() for comment in cmts]

    @classmethod
    def remove_tag(cls, soup, tag):
        [t.extract() for t in soup.findAll(tag)]

    @classmethod
    def remove_br(cls, soup):
        cls.remove_tag(soup, 'br')

    @classmethod
    def xpath(cls, path, soup):
        elements = path.split('/')

        cur = soup
        for e in elements:
            if not e:
                continue

            index = 0
            if e.endswith(']'):
               e, index = e.strip(']').split('[')
               index = int(index)-1

            children = cur.findAll(e, recursive=False)
            try:
                cur = children[index]
            except IndexError:
                # Try to workaround tbody being optional.
                if e == 'tbody':
                    continue
                return None

        return cur

    def set_html(self, html):
        self.soup = BeautifulSoup(html)


    def _get_field(self, field, soup):
        value = None
        if hasattr(self, 'get_%s' % field):
            method = getattr(self, 'get_%s' % field)
            value = method(soup)
        elif field in self.paths.keys():
            tag = self.xpath(self.paths[field], soup)
            if tag and tag.contents:
                value = tag.contents[0].strip()

        conv = self.converter.get(field)
        if conv:
            value = conv(value)

        return value

    def parse_bug(self, html=None):
        if html:
            soup = BeautifulSoup(html)
        else:
            soup = self.soup
        self.remove_comments(soup)

        kargs = {}
        for field in Bug.fields:
            try:
                value = self._get_field(field, soup)
            except AttributeError:
                return None

            self._cache[field] = value
            kargs[field] = value

        return Bug(**kargs)


