#!/usr/bin/env python
import web
import sys
import json

#sys.path.insert(0, '/home/romaia/GRAD/bicho')
sys.path.insert(0, '../../')
from bicho.www.graph import LineGraph
from bicho.www.metrics import Metrics
web.runwsgi = web.runfcgi

urls = (
    '/', 'index',
    '/bug_status/', 'bug_status',
    '/user_activity/', 'user_activity',
    '/api/(.*)/', 'api',
    '/xml', 'xml',
)

HOST = 'http://127.0.0.1/bicho'
BASE_URL = '%s/server.py' % HOST

_globals = {
    'domain': HOST,
    'base_url': BASE_URL,
}
render = web.template.render('templates/', globals=_globals)
_globals['render'] = render


class index:
    def GET(self):
        return render.index()


class bug_status:
    def GET(self):
        input = web.input(year=2009)
        months, lines = Metrics.get_bug_status_data(int(input.year), '../../')
        g = LineGraph()
        g.add_line('New', lines['open_bugs'])
        g.add_line('Fixed', lines['fixed_bugs'])
        g.add_line('Invalid', lines['invalid_bugs'])
        g.add_line('Dup', lines['dup_bugs'])
        g.add_line('Reopened', lines['reopenen_bugs'])
        g.set_x_labels(months)

        return render.bug_status(g, input.year)


class user_activity:
    def GET(self):
        input = web.input(year=2009)
        months, lines = Metrics.get_user_activity_data(int(input.year), '../../')
        g = LineGraph()
        g.set_x_labels(months)

        top = []
        for key, value in lines.items():
            top.append((sum(value)/len(value), key))
        top.sort()
        top.reverse()

        for avg, user in top[:5]:
            name = user.split('@')[0]
            g.add_line(name, lines[user])

        return render.user_activity(g, input.year)


class api:
    data_map = dict(
        bug_status=Metrics.get_bug_status_data,
        user_activity=Metrics.get_user_activity_data
    )

    def GET(self, data):
        input = web.input(year=2009)
        months, lines = self.data_map[data](int(input.year), '../../')
        retval = dict(months=months, data=lines)
        web.header('Content-Type', 'text/plain')
        return json.dumps(retval, sort_keys=True, indent=4)

from BeautifulSoup import BeautifulSoup
class xml:
    metrics = {
        'M2*': 'get_comment_activity',
        'M26': 'get_open_bugs',
        'M29': 'get_percentage_resolved_bugs',
        'M30': 'get_total_bugs',
        'M33*': 'get_total_users',
        'bug_life_time (days)': 'get_bug_life_time',
    }
    def GET(self):
        web.header('Content-Type', 'text/xml')
        m = Metrics('../../')
        output = ''

        for key, value in self.metrics.items():
            value = getattr(m, value)()
            output += """
    <GenericItem>
        <resource>%s</resource>
        <metric>%s</metric>
        <value>%s</value>
    </GenericItem>""" % ('stoq', key, value)

        output = """<GenericItems>%s
</GenericItems>""" % output
        return output


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
