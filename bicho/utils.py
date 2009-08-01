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
# Authors: Carlos Garcia Campos <carlosgc@gsyc.escet.urjc.es>
#          Added class OptionsStore by: Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#

import os
import sys
import getopt
import ConfigParser

last_messages = ['',] * 10
from bicho.progress import progress

class OptionsStore:
    #Pattern singleton applied

    __shared_state = {"frontend": None,
                      "backend": None,

                      "help": False,

                      "db_driver_out": 'sqlite',
                      "db_user_out": 'bicho',
                      "db_password_out": 'bicho',
                      "db_database_out": 'bicho',
                      "db_hostname_out": 'localhost',
                      "db_port_out": '3306'}

    def __init__(self, params):
        self.__dict__.update(self.__shared_state)
        self.load_from_file()
        self.parse_from_parameters(params)

    def load_from_file(self):
        _conf = ConfigParser.ConfigParser()

        _conf.read([os.path.join('/etc', 'bicho'),
                    os.path.expanduser('~/.bicho'),
                    os.path.join(os.getcwd(), 'bicho.ini')])

        if _conf.has_section('General'):
            for opt, value in _conf.items('General'):
                setattr(self, opt, value)

        self.frontend_options = {}
        self.backend_options = {}

        if _conf.has_section(self.frontend):
            for opt, value in _conf.items(self.frontend):
                self.frontend_options[opt] = value

        if _conf.has_section(self.backend):
            for opt, value in _conf.items(self.backend):
                self.backend_options[opt] = value

    def parse_from_parameters(self, params):
        short_opts = "h"
        long_opts = ["help"]

        try:
            opts, args = getopt.getopt(params, short_opts, long_opts)
        except getopt.GetoptError, e:
            print e
            return False

        for opt, value in opts:
            if opt in ("-h", "--help"):
                self.help = True

        return True

    def verify(self):
        correct = True

        if self.frontend is None:
            printerr("Required parameter 'frontend' is missing")
            correct = False

        if self.backend is None:
            printerr("Required parameter 'backend' is missing")
            correct = False

        return correct

try:
    log_file = file('bicho.log', 'w')
except IOError:
    log_file = None

def printerr(message=''):
    message += '\n'
    sys.stderr.write(message)
    sys.stderr.flush()

def debug(message):
    message = "DBG: " + message
    last_messages.append(message)
    last_messages.pop(0)
    if not progress.finished:
        progress.update()

    if log_file:
        log_file.write(message + '\n')
        log_file.flush()


