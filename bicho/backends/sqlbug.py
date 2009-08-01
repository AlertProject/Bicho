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
#

from storm.locals import Store, Unicode, Int, create_database, DateTime

#from storm import database
#database.DEBUG = True
from bicho.interfaces import Backend, register_interface
from bicho.domain import Bug, Attachment, Comment, Change, GeneralInfo

class SQLite(object):

    def __init__(self, opts):
        self.options = opts

        db_name = "%s:%s.db" % (opts['db_driver'],
                                opts['db_database'])
        self.database = create_database(db_name)
        self.store = Store(self.database)

        self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                           "id integer primary key," +
                           "project varchar(256), " +
                           "url varchar(256), " +
                           "tracker varchar(256), " +
                           "date varchar(128))")

        self.store.execute("CREATE TABLE IF NOT EXISTS Bugs (" +
                           "id integer primary key," +
                           "bug_id varchar," +
                           "summary varchar, " +
                           "description text," +
                           "open_date DATETIME,"+
                           "status varchar,"+
                           "resolution varchar,"+
                           "severity varchar,"+
                           "priority varchar,"+
                           "category varchar,"+
                           #"group varchar,"+
                           "assignee varchar,"+
                           "reporter varchar)")

        self.store.execute("CREATE TABLE IF NOT EXISTS Comments (" +
                           "id integer primary key," +
                           "bug_id varchar(128)," +
                           "date DATETIME,"+
                           "person varchar(128), " +
                           "comment text)")

        self.store.execute("CREATE TABLE IF NOT EXISTS Attachments (" +
                           "id integer primary key," +
                           "bug_id varchar(128)," +
                           "name varchar(256), " +
                           "type varchar(256), " +
                           "description text, " +
                           "url varchar(256))")

        self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                           "id integer primary key," +
                           "bug_id varchar(128)," +
                           "field varchar(256), " +
                           "old_value varchar(256), " +
                           "new_value varchar(256), " +
                           "date DATETIME, " +
                           "person varchar(256))")


class DBGeneralInfo(object):
    __storm_table__ = "GeneralInfo"

    id = Int(primary=True)
    project = Unicode()
    url = Unicode()
    tracker = Unicode()
    date = DateTime()

    def __init__(self, info):
        self.project = info.project
        self.url = info.url
        self.tracker = info.tracker
        self.date = info.date



class DBAttachment(object):
    __storm_table__ = "Attachments"

    id = Int(primary=True)
    bug_id = Unicode()
    name = Unicode()
    description = Unicode()
    url = Unicode()

    def __init__(self, bug_id, attachment):
        self.bug_id = bug_id
        self.name = attachment.name
        self.type = attachment.type
        self.description = attachment.description
        self.url = attachment.url


class DBComment(object):
    __storm_table__ = "Comments"

    id = Int(primary=True)
    bug_id = Unicode()
    date = DateTime()
    person = Unicode()
    comment = Unicode()

    def __init__(self, bug_id, comment):
        self.bug_id = bug_id
        self.date = comment.date
        self.person = comment.person
        self.comment = comment.comment


class DBChange(object):
    __storm_table__ = "Changes"

    id = Int(primary=True)
    bug_id = Unicode()
    field = Unicode()
    old_value = Unicode()
    new_value = Unicode()
    date = DateTime()
    person = Unicode()

    def __init__(self, bug_id, change):
        self.bug_id = bug_id
        self.field = change.field
        self.old_value = change.old_value
        self.new_value = change.new_value
        self.date = change.date
        self.person = change.person


class DBBug(object):
    __storm_table__ = "Bugs"

    id = Int(primary=True)
    bug_id = Unicode()
    summary = Unicode()
    description = Unicode()
    open_date = DateTime()
    status = Unicode()
    resolution = Unicode()
    priority = Unicode()
    severity = Unicode()
    category = Unicode()
    #group = Unicode()
    assignee = Unicode()
    reporter = Unicode()

    def __init__(self, bug):
        self.bug_id = bug.bug_id
        self.summary = bug.summary
        self.description = bug.description
        self.open_date = bug.open_date
        self.status = bug.status
        self.resolution = bug.resolution
        self.priority = bug.priority
        self.severity = bug.severity
        self.category = bug.category
        #self.group = bug.group
        self.assignee = bug.assignee
        self.reporter = bug.reporter


class DBBackend(Backend):
    database_map = dict(
        sqlite=SQLite
    )

    object_map = dict(
        Bug=DBBug,
        Attachment=DBAttachment,
        Change=DBChange,
        Comment=DBComment,
        GeneralInfo=DBGeneralInfo
    )

    required_fields = ['db_driver', 'db_user', 'db_password', 'db_database',
                       'db_hostname', 'db_port']

    def __init__(self, options):
        self.options = options

    def _get_database(self):
        driver = self.options['db_driver']
        return self.database_map[driver](self.options)

    def _insert_general_info(self, info):
        db_info = DBGeneralInfo(info)
        self.store.add(db_info)
        self.store.flush()

    def _insert_bug(self, dbBug):
        self.store.add(dbBug)
        self.store.flush()

    def _insert_comment(self, dbComment):
        self.store.add(dbComment)
        self.store.flush()

    def _insert_attachment(self, dbAttach):
        self.store.add(dbAttach)
        self.store.flush()

    def _insert_change(self, dbChange):
        self.store.add(dbChange)
        self.store.flush()

    #
    #   Frontend Impletmentation
    #

    def send_data(self, data):
        bug = DBBug(data)
        self.db.store.add(bug)
        for change in data.changes:
            self.db.store.add(DBChange(bug.bug_id, change))

        for comment in data.comments:
            self.db.store.add(DBComment(bug.bug_id, comment))

        for attachment in data.attachments:
            self.db.store.add(DBAttachment(bug.bug_id, attachment))

        self.db.store.flush()

    def done(self):
        self.db.store.commit()

    def check_configuration(self):
        valid = all([self.options.has_key(key) for key in
                        self.required_fields])
        if valid:
            self.db = self._get_database()
        return valid


register_interface('sqlbug', DBBackend)

