import urllib

class LineGraph(object):
    domain = "http://chart.apis.google.com/chart?"

    width = 450
    height = 250
    type = "lc"         #line chart
    axis = "x,y"
    colors = ("FF9900", "4D89F9" )
    colors = ("CC0000", "75507B", "729FCF", "73D216", "C17D11", "EDD400")

    def __init__(self):
        self.url = self.domain
        self._labels = []
        self._lines = []
        self._x_label = ''
        self._y_label = ''
        self.params = dict(cht=self.type,
                           chs="%sx%s" % (self.width, self.height),
                           chxt=self.axis,
                           chco=','.join(self.colors),
                           chdlp='b',           # Legend position
                           chg="9,25,1,5"      # dashed lines
                           )

    def set_x_labels(self, labels):
        self._x_label += '0:|' + '|'.join(labels)

    def _set_axis_labels(self):
        self.params['chxl'] = "0:|%s|1:|%s" % (self._x_label, self._y_label)

    def _set_data_labels(self, *args):
        self.params['chdl'] = '|'.join(args)

    def _set_data(self, *args):
        self.data = 's:'
        m = max([max(i) for i in args])
        m = max(m, 100)
        self.max = m
        self._y_label += '|1:|%s' % '|'.join([str(i*float(self.max)/4) for i in range(5)])
        encs = [self.encode(i,m) for i in args]
        encs = ','.join(encs)
        self.data += encs
        self.params['chd'] = self.data

    def add_line(self, label, values):
        self._labels.append(label)
        self._lines.append(values)

    def get_url(self):
        self._set_data(*self._lines)
        self._set_data_labels(*self._labels)
        self._set_axis_labels()

        params = []
        params = urllib.urlencode(self.params)

        return self.url + params

    def encode(self, data, max_value):
        SE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        enc = ''
        for i in data:
            enc += SE[int(round((len(SE)-1)*i/max_value))]

        return enc


if __name__ == '__main__':
    from bicho.www.metrics import get_user_activity_data
    months, lines = get_user_activity_data(2006)
    print months
    top = []
    for key, value in lines.items():
        top.append((sum(value)/len(value), key))

    top.sort()
    top.reverse()

    g = LineGraph()
    g.set_x_labels(months)

    for avg, user in top[:5]:
        name = user.split('@')[0]
        print "%10s" % name, lines[user]
        g.add_line(name, lines[user])
    print g.get_url()


    #months, lines = get_bug_status_data(2007)
    #g.add_line('Open bugs', lines['open_bugs'])
    #g.add_line('Fixed bugs', lines['fixed_bugs'])
    #g.add_line('Invalid bugs', lines['invalid_bugs'])
