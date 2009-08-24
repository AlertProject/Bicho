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
        """CREATE TABLE IF NOT EXISTS Bugs (
        bug_id       INTEGER PRIMARY KEY ,
        summary      VARCHAR,
        description  TEXT,
        open_date    DATETIME,
        status       VARCHAR,
        resolution   VARCHAR,
        severity     VARCHAR,
        priority     VARCHAR,
        category     VARCHAR,
        assignee     VARCHAR,
        reporter     VARCHAR)""",

        """CREATE TABLE IF NOT EXISTS Comments (
        id           INTEGER PRIMARY KEY,
        bug_id       INTEGER,
        date         DATETIME,
        person       VARCHAR,
        comment      TEXT)""",

        """CREATE TABLE IF NOT EXISTS Attachments (
        id           INTEGER PRIMARY KEY,
        bug_id       INTEGER,
        name         VARCHAR,
        type         VARCHAR,
        description  TEXT,
        url          VARCHAR)""",

        """CREATE TABLE IF NOT EXISTS Changes (
        id           INTEGER PRIMARY KEY,
        bug_id       INTEGER,
        field        VARCHAR,
        old_value    VARCHAR,
        new_value    VARCHAR,
        date         DATETIME,
        person       VARCHAR)""",
    ),

    "MySQL": (
        """CREATE TABLE IF NOT EXISTS Bugs (
        bug_id       INTEGER PRIMARY KEY ,
        summary      TEXT,
        description  TEXT,
        open_date    DATETIME,
        status       VARCHAR(128),
        resolution   VARCHAR(128),
        severity     VARCHAR(128),
        priority     VARCHAR(128),
        category     VARCHAR(128),
        assignee     VARCHAR(128),
        reporter     VARCHAR(128))""",

        """CREATE TABLE IF NOT EXISTS Comments (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        bug_id       INTEGER,
        date         DATETIME,
        person       VARCHAR(128),
        comment      TEXT)""",

        """CREATE TABLE IF NOT EXISTS Attachments (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        bug_id       INTEGER,
        name         VARCHAR(128),
        type         VARCHAR(128),
        description  TEXT,
        url          TEXT)""",

        """CREATE TABLE IF NOT EXISTS Changes (
        id           INTEGER AUTO_INCREMENT PRIMARY KEY,
        bug_id       INTEGER,
        field        VARCHAR(128),
        old_value    VARCHAR(128),
        new_value    VARCHAR(128),
        date         DATETIME,
        person       VARCHAR(128))""",
    ),
}


class Attachment(object):
    __storm_table__ = "Attachments"

    id = Int(primary=True)
    bug_id = Int()
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
    bug_id = Int()
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
    bug_id = Int()
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

    bug_id = Int(primary=True)
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

    comments = ReferenceSet(bug_id, Comment.bug_id)
    changes = ReferenceSet(bug_id, Change.bug_id)
    attachments = ReferenceSet(bug_id, Attachment.bug_id)

    def __init__(self, bug):
        self.bug_id = bug.bug_id
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
        bug = self.store.get(Bug, data.bug_id)
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

    def want_bug(self, bug_id):
        return True


register_interface('sqlbug', SQLBugBackend)

