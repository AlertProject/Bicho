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

from storm.locals import (Unicode, Int, DateTime,
                          Reference, ReferenceSet)

#from storm import database
#database.DEBUG = True
from bicho.interfaces import DBBackend, register_interface

SETUP_COMMANDS = {
    "SQLite": (
        """CREATE TABLE IF NOT EXISTS GeneralInfo (
        idBug       INTEGER PRIMARY KEY ,
        Project   VARCHAR,
        Url   VARCHAR,
        Tracker   VARCHAR,
        Date     DATETIME)""",
        
        """CREATE TABLE IF NOT EXISTS Bugs (
        idBug       INTEGER PRIMARY KEY ,
        Summary      VARCHAR,
        Description  TEXT,
        DateSubmitted    DATETIME,
        Status       VARCHAR,
        Resolution   VARCHAR,
        Severity     VARCHAR,
        Priority     VARCHAR,
        Category     VARCHAR,
        AssignedTo     VARCHAR,
        SubmittedBy     VARCHAR)""",

        """CREATE TABLE IF NOT EXISTS Comments (
        id           INTEGER PRIMARY KEY,
        idBug       INTEGER,
        date         DATETIME,
        person       VARCHAR,
        comment      TEXT)""",

        """CREATE TABLE IF NOT EXISTS Attachments (
        id           INTEGER PRIMARY KEY,
        idBug       INTEGER,
        name         VARCHAR,
        type         VARCHAR,
        description  TEXT,
        url          VARCHAR)""",

        """CREATE TABLE IF NOT EXISTS Changes (
        id           INTEGER PRIMARY KEY,
        idBug       INTEGER,
        field        VARCHAR,
        old_value    VARCHAR,
        new_value    VARCHAR,
        date         DATETIME,
        person       VARCHAR)""",
    ),

    "MySQL": (
        """CREATE TABLE IF NOT EXISTS GeneralInfo (
        idBug       INTEGER PRIMARY KEY ,
        Project     VARCHAR(256),
        Url VARCHAR(256),
        Tracker   VARCHAR(256),
        Date DATETIME)""",
        
        """CREATE TABLE IF NOT EXISTS Bugs (
        idBug       INTEGER PRIMARY KEY ,
        Summary      TEXT,
        Description  TEXT,
        DateSubmitted    DATETIME,
        Status       VARCHAR(128),
        Resolution   VARCHAR(128),
        Severity     VARCHAR(128),
        Priority     VARCHAR(128),
        Category     VARCHAR(128),
        AssignedTo     VARCHAR(128),
        SubmmitedBy     VARCHAR(256))""",

        """CREATE TABLE IF NOT EXISTS Comments (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        idBug       INTEGER,
        Date         DATETIME,
        SubmmitedBy       VARCHAR(256),
        Comment      TEXT)""",

        """CREATE TABLE IF NOT EXISTS Attachments (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        idBug       INTEGER,
        Name         VARCHAR(128),
        Type         VARCHAR(128),
        Description  TEXT,
        Url          TEXT)""",

        """CREATE TABLE IF NOT EXISTS Changes (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        idBug       INTEGER,
        Field        VARCHAR(128),
        OldValue    VARCHAR(128),
        NewValue    VARCHAR(128),
        Date         DATETIME,
        SubmmitedBy       VARCHAR(256))""",
    ),
}

class GeneralInfo(object):
  __storm_table__ = "GeneralInfo"

  idBug = Int(primary=True)
  Project = Unicode()
  Url = Unicode()
  Tracker = Unicode()
  Date = Unicode()


  def __init__(self, generalinfo):
        self.project = genrealinfo.project
        self.url = generalinfo.url
        self.tracker = generalinfo.tracker
        self.date = generalinfo.date 

class Attachment(object):
    __storm_table__ = "Attachments"

    id = Int(primary=True)
    idBug = Int()
    name = Unicode()
    description = Unicode()
    url = Unicode()

    def __init__(self, attachment):
        self.name = attachment.name
        self.type = attachment.type
        self.description = attachment.description
        self.url = attachment.url


class Comment(object):
    __storm_table__ = "Comments"

    id = Int(primary=True)
    idBug = Int()
    date = DateTime()
    person = Unicode()
    comment = Unicode()

    def __init__(self, comment):
        self.date = comment.date
        self.person = comment.person
        self.comment = comment.comment


class Change(object):
    __storm_table__ = "Changes"

    id = Int(primary=True)
    idBug = Int()
    field = Unicode()
    old_value = Unicode()
    new_value = Unicode()
    date = DateTime()
    person = Unicode()

    def __init__(self, change):
        self.field = change.field
        self.old_value = change.old_value
        self.new_value = change.new_value
        self.date = change.date
        self.person = change.person


class Bug(object):
    __storm_table__ = "Bugs"

    idBug = Int(primary=True)
    summary = Unicode()
    description = Unicode()
    open_date = DateTime()
    status = Unicode()
    resolution = Unicode()
    priority = Unicode()
    severity = Unicode()
    category = Unicode()
    assignee = Unicode()
    reporter = Unicode()

    comments = ReferenceSet(idBug, Comment.idBug)
    changes = ReferenceSet(idBug, Change.idBug)
    attachments = ReferenceSet(idBug, Attachment.idBug)
    generalinfo = ReferenceSet(idBug, GeneralInfo.idBug)

    def __init__(self, bug):
        self.idBug = bug.idBug
        self.update(bug)

    def update(self, bug):
        self.summary = bug.summary
        self.description = bug.description
        self.open_date = bug.open_date
        self.status = bug.status
        self.resolution = bug.resolution
        self.priority = bug.priority
        self.severity = bug.severity
        self.category = bug.category
        self.assignee = bug.assignee
        self.reporter = bug.reporter


class SQLBugBackend(DBBackend):
    required_fields = ['db_uri']
    setup_commands = SETUP_COMMANDS

    def __init__(self, options):
        self.options = options

    #
    #   Frontend Impletmentation
    #

    def send_data(self, data):
        bug = self.store.get(Bug, data.idBug)
        if not bug:
            bug = Bug(data)
            self.store.add(bug)
        else:
            bug.update(data)

        for change in data.changes[bug.changes.count():]:
            bug.changes.add(Change(change))

        for comment in data.comments[bug.comments.count():]:
            bug.comments.add(Comment(comment))

        for attachment in data.attachments[bug.attachments.count():]:
            bug.attachments.add(Attachment(attachment))

        self.store.flush()

    def want_bug(self, idBug):
        return True


register_interface('sqlbug', SQLBugBackend)

