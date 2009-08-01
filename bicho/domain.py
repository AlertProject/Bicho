# -*- coding: utf-8 -*-
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
# Authors:  Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#           Ronaldo Maia            <romaia@async.com.br>
#

class DomainObject(object):
    fields = []

    def __init__(self, **kargs):
        kargs_keys = kargs.keys()

        for key in self.fields:
            if key in kargs_keys:
                setattr(self, key, kargs[key])
            else:
                setattr(self, key, None)

class GeneralInfo(DomainObject):
    fields = ['project', 'url', 'tracker', 'date']


class Attachment(DomainObject):
    fields = ['bug_id', 'name', 'description', 'url', 'type']


class Comment(DomainObject):
    fields = ['bug_id', 'date', 'person', 'comment']

    def __repr__(self):
        rep = (u'<Comment person=%s date=%s> ' % (
                self.person, self.date))
        return rep



class Change(DomainObject):
    fields = ['bug_id', 'date', 'field', 'person', 'old_value', 'new_value']

    def __repr__(self):
        rep = (u'<Change person=%s date=%s field="%s" old_value="%s"'
                ' new_value="%s">' % (
                self.person, self.date, self.field, self.old_value,
                self.new_value))
        return rep


class Bug(DomainObject):
    fields = ['bug_id', 'summary', 'description', 'open_date',
              'status', 'resolution', 'priority', 'severity',
              'category', 'group',
              'assignee', 'reporter', 'last_changed',
              'comments', 'attachments', 'changes']

    statuses = ['NEW', 'ASSIGNED', 'REOPENED', 'RESOLVED']
    resolutions = ['FIXED', 'INVALID', 'DUPLICATE']

    def __repr__(self):
        rep = ('<Bug id=%s summary="%s" status=%s resolution=%s '
               'open_date=%s last_changed=%s '
               'assignee="%s" comments=%s>' % (
                self.bug_id, self.summary, self.status, self.resolution,
                self.open_date, self.last_changed,
                self.assignee, len(self.comments)))
        return rep.encode('utf-8')
