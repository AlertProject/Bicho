import time, sys

try:
    from progressbar import Bar, Percentage, ETA, ProgressBarWidget, \
                            ProgressBar, SimpleProgress
    has_progress = True
except ImportError:
    has_progress = False

from bicho.utils import last_messages

if has_progress:
    class ProgressBugMessage(ProgressBarWidget):
        message = ''

        def update(self, pbar):
            return self.message

    class MyProgressBar(ProgressBar):

        def set_message(self, message):
            self.message = message

        def set_max_value(self, value):
            self.maxval = value

        def __init__(self, maxval=100, widgets=None, fd=sys.stderr):
            assert maxval > 0
            self.maxval = maxval

            bar = Bar(marker='=', left='[', right=']')
            self.message = ''
            widgets = ['Bicho: ', Percentage(), ' ', bar, ' ', ETA(), ' ',
                       ' (', SimpleProgress(), ') ']

            self.widgets = widgets
            self.fd = fd
            self.signal_set = False
            try:
                self.handle_resize(None,None)
                self.signal_set = True
            except:
                self.term_width = 79

            self.currval = 0
            self.finished = True
            self.prev_percentage = -1
            self.start_time = None
            self.seconds_elapsed = 0

        def write_line(self, line):
            self.fd.write(line[:self.term_width-2])
            self.fd.write(' ' * (self.term_width - len(line)-2))
            self.fd.write('\n')

        def update(self, value=None):
            self.handle_resize(None, None)
            if value is None:
                value = self.currval

            assert 0 <= value <= self.maxval
            self.currval = value
            #if self.finished:
            #    return
            if not self.start_time:
                self.start_time = time.time()

            self.seconds_elapsed = time.time() - self.start_time

            line = self._format_line()
            self.fd.write(chr(27) + '[u' + line)
            self.fd.write('\n')
            self.write_line(self.message)
            self.write_line('-' * self.term_width)

            for line in last_messages:
                self.write_line(line)

            if value == self.maxval:
                self.finished = True
                self.fd.write('\n')

        def start(self):
            self.finished = False
            self.fd.write(chr(27) + '[s')
            return ProgressBar.start(self)

else:
    class MyProgressBar(object):
        finished = False
        def set_message(self, message):
            print message

        def set_max_value(self, value):
            pass

        def __init__(self, maxval=100, widgets=None, fd=sys.stderr):
            pass

        def write_line(self, line):
            pass

        def update(self, value=None):
            pass

        def start(self):
            pass

        def finish(self):
            self.finished = True



progress = MyProgressBar()

if __name__ == '__main__':
    i = 0

    bar = Bar(marker='-', left='[', right=']')
    prog_bug = ProgressBugMessage()
    widgets = ['Bicho: ', Percentage(), ' ', bar, ' ', ETA(), ' ', prog_bug,
               ' (', SimpleProgress(), ') '
               ]

    pbar = MyProgressBar(widgets=widgets, maxval=100).start()

    for i in xrange(100):
        pbar.update(i)
        time.sleep(1)

    pbar.finish()
