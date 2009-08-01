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

from bicho.interfaces import Backend, register_interface

class StdoutBackend(Backend):
    """A simple backend that prints to stdout"""


    def want_bug(self, bug_id):
        return True

    def send_data(self, data):
        print data
        print "Bug: %s (comments: %s, changes: %s, attachments: %s)" % (
                data.bug_id, len(data.comments), len(data.changes),
                len(data.attachments))

    def done(self):
        print 'Done!'


register_interface("stdout", StdoutBackend)

