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

'''
class SQLite(object):

  def __init__(self, opts):
    self.options = opts
    db_name = "%s:%s.db" % (opts['db_driver'],opts['db_database'])
    self.database = create_database(db_name)
    self.store = Store(self.database)
    self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                       "id integer primary key," +
                       "Project varchar(256), " +
                       "Url varchar(256), " +
                       "Tracker varchar(256), " +
                       "Date datetime)")

    self.store.execute ("CREATE TABLE  IF NOT EXISTS Bugs (" +
                       "id integer primary key," +
                       "idBug varchar(128)," +
                       "Summary text," +
                       "Description text,"+
                       "DateSubmitted datetime,"+
                       "Status varchar(64),"+
                       "Resolution varchar(64),"+
                       "Severity varchar(64),"+
                       "Priority varchar(64),"+
                       "Category varchar(128),"+
                       "IGroup varchar(128),"+
                       "AssignedTo varchar(128),"+
                       "SubmittedBy varchar(128)) DEFAULT CHARSET=utf8")

    self.store.execute("CREATE TABLE IF NOT EXISTS Comments (" + 
                       "id integer primary key," +  
                       "idBug varchar(128)," +
                       "DateSubmitted datetime,"+
                       "SubmittedBy varchar(128), " + 
                       "Comment text)")

    self.store.execute("CREATE TABLE IF NOT EXISTS Attachments (" +
                       "id integer primary key," +
                       "idBug varchar(128)," +
                       "Name varchar(256), " +
                       "Type varchar(256), " +
                       "Description text, " + 
                       "Url varchar(256))")

    self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                       "id integer primary key," +
                       "idBug varchar(128)," +
                       "Field varchar(256), " +
                       "OldValue varchar(256), " +
                       "NewValue varchar(256), " +
                       "Date datetime, " +
                       "SubmittedBy varchar(256))") 
'''
class DBMySQL(DBDatabase):
  def __init__(self, opts):
    self.options = opts

    try:
      print opts['db_driver']
      self.database = create_database(opts['db_driver'] +"://"+ 
                      opts['db_user'] +":"+ opts['db_password']
                      +"@"+ opts['db_hostname'] +":"+
                      opts['db_port']+"/"+ opts['db_database'])
    except DatabaseModuleError, e:
      raise DBDatabaseDriverNotAvailable(str (e))
    except ImportError:
      raise DBDatabaseDriverNotSupported
    except: 
      raise

    self.store = Store(self.database)
    
    self.store.execute("CREATE TABLE IF NOT EXISTS GeneralInfo(" +
                       "id int auto_increment primary key," +
                       "Project varchar(256), " +
                       "Url varchar(256), " +
                       "Tracker varchar(256), " +
                       "Date datetime)")

    self.store.execute ("CREATE TABLE  IF NOT EXISTS Bugs (" +
                       "id int auto_increment primary key," +
                       "idBug varchar(128)," +
                       "Summary text," +
                       "Description text,"+
                       "DateSubmitted datetime,"+
                       "Status varchar(64),"+
                       "Resolution varchar(64),"+
                       "Severity varchar(64),"+
                       "Priority varchar(64),"+
                       "Category varchar(128),"+
                       "IGroup varchar(128),"+
                       "AssignedTo varchar(128),"+
                       "SubmittedBy varchar(128)) DEFAULT CHARSET=utf8")

    self.store.execute("CREATE TABLE IF NOT EXISTS Comments (" + 
                       "id int auto_increment primary key," +  
                       "idBug varchar(128)," +
                       "DateSubmitted datetime,"+
                       "SubmittedBy varchar(128), " + 
                       "Comment text)")

    self.store.execute("CREATE TABLE IF NOT EXISTS Attachments (" +
                       "id int auto_increment primary key," +
                       "idBug varchar(128)," +
                       "Name varchar(256), " +
                       "Type varchar(256), " +
                       "Description text, " + 
                       "Url varchar(256))")

    self.store.execute("CREATE TABLE IF NOT EXISTS Changes (" +
                       "id int auto_increment primary key," +
                       "idBug varchar(128)," +
                       "Field varchar(256), " +
                       "OldValue varchar(256), " +
                       "NewValue varchar(256), " +
                       "Date datetime, " +
                       "SubmittedBy varchar(256))")


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
    idbug = Unicode()
    name = Unicode()
    type = Unicoe()
    description = Unicode()
    url = Unicode()

    def __init__(self, idbug, attachment):
        self.idbug = idbug
        self.name = attachment.name
        self.type = attachment.type
        self.description = attachment.description
        self.url = attachment.url


class DBComment(object):
    __storm_table__ = "Comments"

    id = Int(primary=True)
    idbug = Unicode()
    datesumitted = DateTime()
    submittedby = Unicode()
    comment = Unicode()

    def __init__(self, idbug, comment):
        self.idbug = idbug
        self.datesubmitted = comment.datesubmitted
        self.submittedby = comment.submittedby
        self.comment = comment.comment


class DBChange(object):
    __storm_table__ = "Changes"

    id = Int(primary=True)
    idbug = Unicode()
    field = Unicode()
    old_value = Unicode()
    new_value = Unicode()
    date = DateTime()
    submittedby = Unicode()

    def __init__(self, idbug, change):
        self.idbug = idbug
        self.field = change.field
        self.old_value = change.old_value
        self.new_value = change.new_value
        self.date = change.date
        self.submittedby = change.submittedby


class DBBug(object):
    __storm_table__ = "Bugs"

    id = Int(primary=True)
    idbug = Unicode()
    summary = Unicode()
    description = Unicode()
    datesubmitted = DateTime()
    status = Unicode()
    resolution = Unicode()
    priority = Unicode()
    severity = Unicode()
    category = Unicode()
    igroup = Unicode()
    assignedto = Unicode()
    submittedby = Unicode()

    def __init__(self, bug):
        self.idbug = bug.idbug
        self.summary = bug.summary
        self.description = bug.description
        self.datesubmitted = bug.datesubmitted
        self.status = bug.status
        self.resolution = bug.resolution
        self.priority = bug.priority
        self.severity = bug.severity
        self.category = bug.category
        self.igroup = bug.igroup
        self.assignedto = bug.assignedto
        self.submitted = bug.submittedby


class DBBackend(Backend):
    database_map = dict(
      #sqlite=SQLite
        mysql=DBMySQL
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
            self.db.store.add(DBChange(bug.idbug, change))

        for comment in data.comments:
            self.db.store.add(DBComment(bug.idbug, comment))

        for attachment in data.attachments:
            self.db.store.add(DBAttachment(bug.idbug, attachment))

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

