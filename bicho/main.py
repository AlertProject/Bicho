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
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#          Ronaldo Francisco Maia       <romaia@async.com.br>
#

import sys

from bicho.utils import OptionsStore, printerr, debug
from bicho.interfaces import create_frontend, create_backend
from bicho.progress import progress


USAGE = """
Usage: %(program_name)s [options] [URL]

It extracts data from bug tracking systems from a project given

Available frontend types:
    %(frontends)s

Available backend types:
    %(backends)s
"""

def print_usage():
    frontends = 'FIXME'
    backends = 'FIXME'

    print USAGE % dict(program_name = 'bicho',
                       frontends = frontends,
                       backends = backends,
                    )



class Bicho(object):

    def __init__ (self, options):
        self.options = options
        debug("Bicho object created")

    def run(self, frontend, backend):
        print "Running Bicho"
        print "Frontend: %s  => Backend: %s" % (type(frontend).__name__,
                                                type(backend).__name__)
        print
        progress.start()
        progress.set_message('Preparing...')
        frontend.prepare()
        try:
            frontend.run(backend)
        finally:
            backend.done()
        progress.set_message('Done.')
        progress.update()
        progress.finish()


def main(params):
    options = OptionsStore(params)

    if options.help:
        print_usage()
        return 0

    error = False

    if not options.verify():
        printerr("Some options are not correct")
        error = True

    frontend = create_frontend(options)
    if not frontend.check_configuration():
        printerr("Check configuration for frontend '%s'" % options.frontend)
        error = True

    backend = create_backend(options)
    if not backend.check_configuration():
        printerr("Check configuration for backend '%s'" % options.backend)
        error = True

    if error:
        return 1

    b = Bicho(options)
    b.run(frontend, backend)

    return 0

if __name__ == "__main__":
    main(sys.argv)
