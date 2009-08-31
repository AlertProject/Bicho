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
# Authors:  Ronaldo Maia            <romaia@async.com.br>
#

import datetime
from storm.locals import DateTime, Unicode, Int, Date

#from storm import database
#database.DEBUG = True
from bicho.interfaces import DBBackend, register_interface

SETUP_COMMANDS = {
    "SQLite": ("""
            CREATE TABLE IF NOT EXISTS bugs (
                id                  INTEGER PRIMARY KEY,
                bug_id              INTEGER,
                open_date           DATETIME,
                closed_date         DATETIME,
                status              VARCHAR,
                resolution          VARCHAR,
                total_comments      INTEGER,
                total_changes       INTEGER,
                total_attachments   INTEGER,
                last_changed        DATETIME,
                last_visited        DATETIME
            )""",
            """CREATE TABLE IF NOT EXISTS user_facts (
                user            VARCHAR,
                timestamp       DATE,
                open_bugs       INTEGER,
                fixed_bugs      INTEGER,
                dup_bugs        INTEGER,
                invalid_bugs    INTEGER,
                reopenen_bugs   INTEGER,
                comments        INTEGER,
                attachments     INTEGER,
                PRIMARY KEY (user, timestamp)
            )""",
            """CREATE TABLE IF NOT EXISTS bug_facts (
                bug_id      INTEGER,
                user        VARCHAR,
                timestamp   DATE,
                comments    INTEGER,
                attachments INTEGER,
                PRIMARY KEY (bug_id, user, timestamp)
            )"""),

    "MySQL": ("""
            CREATE TABLE IF NOT EXISTS bugs (
                id                  INTEGER AUTO_INCREMENT PRIMARY KEY,
                bug_id              INTEGER,
                open_date           DATETIME,
                closed_date         DATETIME,
                status              VARCHAR(128),
                resolution          VARCHAR(128),
                total_comments      INTEGER,
                total_changes       INTEGER,
                total_attachments   INTEGER,
                last_changed        DATETIME,
                last_visited        DATETIME
            )""",
            """CREATE TABLE IF NOT EXISTS user_facts (
                user            VARCHAR(128),
                timestamp       DATE,
                open_bugs       INTEGER,
                fixed_bugs      INTEGER,
                dup_bugs        INTEGER,
                invalid_bugs    INTEGER,
                reopenen_bugs   INTEGER,
                comments        INTEGER,
                attachments     INTEGER,
                PRIMARY KEY (user, timestamp)
            )""",
            """CREATE TABLE IF NOT EXISTS bug_facts (
                bug_id      INTEGER,
                user        VARCHAR(128),
                timestamp   DATE,
                comments    INTEGER,
                attachments INTEGER,
                PRIMARY KEY (bug_id, user, timestamp)
            )"""),
}

class UserFacts(object):
    __storm_table__ = 'user_facts'
    __storm_primary__ = "user", "timestamp"

    user = Unicode()
    timestamp = Date()
    open_bugs = Int(default=0)
    fixed_bugs = Int(default=0)
    dup_bugs = Int(default=0)
    invalid_bugs = Int(default=0)
    reopenen_bugs = Int(default=0)
    comments = Int(default=0)
    attachments = Int(default=0)


class BugFacts(object):
    __storm_table__ = 'bug_facts'
    __storm_primary__ = "bug_id", "user", "timestamp"

    bug_id = Int()
    user = Unicode()
    timestamp = Date()
    comments = Int()
    attachments = Int()


class Bug(object):
    __storm_table__ = 'bugs'

    id = Int(primary=True)
    bug_id = Int()
    open_date = DateTime()
    closed_date = DateTime()
    status = Unicode()
    resolution = Unicode()
    total_comments = Int(default=0)
    total_changes = Int(default=0)
    total_attachments = Int(default=0)
    last_changed = DateTime()
    last_visited = DateTime()

    def __init__(self, bug_id):
        self.bug_id = bug_id

    def update(self, bug):
        self.open_date = bug.open_date
        # XXX: Close date
        self.status = bug.status
        self.resolution = bug.resolution
        self.total_comments = len(bug.comments)
        self.total_changes = len(bug.changes)
        self.total_attachments = len(bug.attachments)
        self.last_changed = bug.last_changed
        self.last_visited = datetime.datetime.today()


class DWHBackend(DBBackend):
    """This backend outputs to a data warehouse.
    Required Configuration neededs:

    - db_uri: an uri for the database following this pattern:

    db_uri=scheme://username:password@hostname:port/database_name
    """
    required_fields = ['db_uri']
    setup_commands = SETUP_COMMANDS

    def __init__(self, options):
        self.options = options

    def _get_user_fact(self, user, date):
        fact = self.store.find(UserFacts,
                               UserFacts.user == user,
                               UserFacts.timestamp == date).one()
        if not fact:
            fact = UserFacts()
            fact.user = user
            fact.timestamp = date
            self.store.add(fact)

        return fact

    def _add_user_facts(self, bug, new_data):
        if not bug.open_date:
            fact = self._get_user_fact(new_data.reporter,
                                       new_data.open_date.date())
            fact.open_bugs += 1

        # We only want to consider the changes we have not seen yet.
        old_changes = bug.total_changes
        for c in new_data.changes[old_changes:]:
            fact = self._get_user_fact(c.person, c.date.date())
            if c.field == 'resolution':
                if c.new_value == 'FIXED':
                    fact.fixed_bugs += 1
                    bug.closed_date = c.date
                elif c.new_value == 'DUPLICATE':
                    fact.dup_bugs += 1
                    bug.closed_date = c.date
                elif len(c.new_value):
                    fact.invalid_bugs += 1
                    bug.closed_date = c.date
            if c.field == 'status' and c.new_value == 'REOPENED':
                fact.reopenen_bugs += 1

        # Again, we only want the new comments, not the old ones.
        old_comments = bug.total_comments
        for c in new_data.comments[old_comments:]:
            fact = self._get_user_fact(c.person, c.date.date())
            fact.comments += 1

    def _add_bug_facts(self, bug, new_data):
        pass

    def _get_bug(self, bug_id):
        bug = self.store.find(Bug,
                                 Bug.bug_id == bug_id).one()
        if not bug:
            bug = Bug(bug_id)
            self.store.add(bug)

        return bug

    #
    #   Frontend Impletmentation
    #

    def want_bug(self, bug_id):
        bug = self.store.find(Bug,
                               Bug.bug_id == int(bug_id)).one()

        # We have no information about the bug yet. Of course we want ;)
        if not bug:
            return True

        if not bug.last_visited:
            return True

        # If we already vistited the bug today, lets way a bit.
        if bug.last_visited.date() < datetime.date.today():
            return True

        return False

    def send_data(self, new_data):
        bug = self._get_bug(int(new_data.bug_id))
        self._add_user_facts(bug, new_data)
        self._add_bug_facts(bug, new_data)
        bug.update(new_data)
        self.store.flush()




register_interface('dwh', DWHBackend)

