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
#

import urllib
import cgi

def get_domain(url):
    strings = url.split('/')
    return strings[0] + "//" + strings[2] + "/"

def url_join(base, *kwargs):
    retval = [base.strip('/')]

    for comp in kwargs:
        retval.append(comp.strip('/'))

    return "/".join(retval)

def url_strip_protocol(url):
    p = url.find("://")
    if p == -1:
        return url

    p += 3
    return url[p:]

def url_get_attr(url, attr=None):
    query = urllib.splitquery(url)
    try:
        if query[1] is None:
            return None;
    except IndexError:
        return None

    attrs = cgi.parse_qsl(query[1])
    if attr is None:
        return attrs

    for a in attrs:
        if attr in a:
            return a[1]

    return None


