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
# Authors: Ronaldo Maia <romaia@async.com.br>
#

import random
import time
import urllib

from bicho.utils import debug
from bicho.progress import progress


_interfaces = {}

class Interface(object):
    required_fields = []

    def __init__(self, options):
        self.options = options

    def check_configuration(self):
        valid = all([self.options.has_key(key) for key in
                        self.required_fields])
        return valid


class Backend(Interface):

    def send_data(self, data):
        raise NotImplementedError

    def done(self):
        pass

    def want_bug(self, bug_id):
        pass


class Frontend(Interface):
    parser_class = None

    def __init__(self, options):
        Interface.__init__(self, options)
        self._current_bug = 0

        assert self.parser_class
        self.parser = self.parser_class()

    def prepare(self):
        raise NotImplementedError

    def get_bug_url(self, bug_id):
        raise NotImplementedError

    def read_page(self, url):
        debug('Reading page: %s' % url)
        if url.startswith('http:'):
            data = urllib.urlopen(url).read()
        else:
            data = file(url).read()

        return data

    def get_total_bugs(self):
        return len(self.bugs)

    def get_next_bug(self):
        try:
            bug = self.bugs[self._current_bug]
        except IndexError:
            return None
        self._current_bug += 1
        return bug

    def analyze_bug(self, bug_id):
        url = self.get_bug_url(bug_id)

        html = self.read_page(url)
        self.parser.set_html(html)
        return self.parser.parse_bug()

    def run(self, backend):
        random.seed()

        i = 0
        total = self.get_total_bugs()

        pbar = progress
        pbar.set_max_value(total)

        while True:
            bug_id = self.get_next_bug()
            if not bug_id:
                break

            i+=1
            progress.set_message('Analysing bug %s' % bug_id)
            pbar.update(i)
            if not backend.want_bug(bug_id):
                debug('Ignoring bug %s' % bug_id)
                continue

            bug = self.analyze_bug(bug_id)
            if bug is None:
                debug('Error retrieving bug %s' % bug_id)
                continue

            debug('Bug %s (changes=%s, comments=%s)' % (bug_id,
                                len(bug.changes), len(bug.comments)))
            backend.send_data(bug)

            if not self.options.get('fast', '0') == '1':
                _long = random.randint(0,20)
                debug('sleeping for %s seconds' % _long)
                time.sleep(_long)


def register_interface(name, klass):
    _interfaces[name] = klass

def _get_interface(type, name):
    if name not in _interfaces:
        __import__('bicho.%s.%s' % (type, name))

    if name not in _interfaces:
        raise TypeError('Interface "%s" is not registered' % name)

    return _interfaces[name]

def create_frontend(options):
    opts = options.frontend_options
    klass = _get_interface('frontends', opts['type'])
    return klass(opts)

def create_backend(options):
    opts = options.backend_options
    klass = _get_interface('backends', opts['type'])
    return klass(opts)

