from bicho.backends.dwh import BugFacts, SQLite
from storm.locals import Select, SQL
from storm.expr import And
import datetime

class Metrics(object):

    def __init__(self, dir=''):
        options = dict(db_driver='sqlite', db_database='%sbicho_dwh_stoq' % dir)
        db = SQLite(options)
        self.store = db.store

    @classmethod
    def get_bug_status_data(cls, year=2008, dir=''):
        options = dict(db_driver='sqlite', db_database='%sbicho_dwh_stoq' % dir)
        db = SQLite(options)
        store = db.store

        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        store.find(BugFacts,
                    BugFacts.timestamp >= start,
                    BugFacts.timestamp <= end)

        query = Select(BugFacts.timestamp, And(BugFacts.timestamp >= start,
                                               BugFacts.timestamp <= end)
        )

        sql = """SELECT strftime('%m', timestamp ) AS month, SUM(open_bugs),
                SUM(fixed_bugs), SUM(dup_bugs), SUM(invalid_bugs),
                SUM(reopenen_bugs), SUM(comments), SUM(attachments)
                FROM user_facts
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY month
                ORDER BY timestamp"""

        result = list(store.execute(SQL(sql, (start, end))))

        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                  '11', '12']

        lines = {
            'open_bugs': [],
            'fixed_bugs': [],
            'dup_bugs': [],
            'invalid_bugs': [],
            'reopenen_bugs': [],
            'comments': [],
            'attachments': [],
        }

        i = 0
        for month in months:
            if i < len(result) and result[i][0] == month:
                lines['open_bugs'].append(result[i][1])
                lines['fixed_bugs'].append(result[i][2])
                lines['dup_bugs'].append(result[i][3])
                lines['invalid_bugs'].append(result[i][4])
                lines['reopenen_bugs'].append(result[i][5])
                lines['comments'].append(result[i][6])
                lines['attachments'].append(result[i][7])
            else:
                lines['open_bugs'].append(0)
                lines['fixed_bugs'].append(0)
                lines['dup_bugs'].append(0)
                lines['invalid_bugs'].append(0)
                lines['reopenen_bugs'].append(0)
                lines['comments'].append(0)
                lines['attachments'].append(0)
            i+=1

        return months, lines


    @classmethod
    def get_user_activity_data(cls, year=2008, dir=''):
        options = dict(db_driver='sqlite', db_database='%sbicho_dwh_stoq' % dir)
        db = SQLite(options)
        store = db.store

        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)

        sql = """SELECT strftime('%m', timestamp ) AS month, user, SUM(comments)
                FROM user_facts
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY month, user
                ORDER BY timestamp"""

        result = list(store.execute(SQL(sql, (start, end))))

        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                  '11', '12']

        # We will have one line per user.
        lines = {
        }

        i = 0
        m = 0
        for month in months:
            while i < len(result) and result[i][0] == month:
                # [user] = comments
                lines.setdefault(result[i][1], [0]*12)
                lines[result[i][1]][m] = result[i][2]
                i+=1
            m += 1

        return months, lines

    def get_bug_life_time(self):
        sql = """SELECT avg(strftime('%s',closed_date) - strftime('%s',open_date))
                    FROM bugs"""
        result = list(self.store.execute(SQL(sql)))
        return result[0][0]/60/60/24

    def get_total_users(self):
        sql = """SELECT count(distinct(user)) FROM user_facts;"""

        result = list(self.store.execute(SQL(sql)))
        return result[0][0]

    def get_comment_activity(self):
        sql = """SELECT sum(comments) FROM user_facts;"""

        result = list(self.store.execute(SQL(sql)))
        return result[0][0]


    def get_total_bugs(self):
        sql = """SELECT sum(open_bugs) FROM user_facts;"""

        result = list(self.store.execute(SQL(sql)))
        return result[0][0]


    def get_open_bugs(self):
        sql = """SELECT sum(open_bugs)+sum(reopenen_bugs) -
                        (sum(fixed_bugs) + sum(dup_bugs) +
                         sum(invalid_bugs))
                FROM user_facts;"""

        result = list(self.store.execute(SQL(sql)))
        return result[0][0]

    def get_percentage_resolved_bugs(self):
        sql = """SELECT (sum(fixed_bugs) + sum(dup_bugs) +
                         sum(invalid_bugs) - sum(reopenen_bugs)) /
                         CAST(sum(open_bugs) as real)
                FROM user_facts;"""

        result = list(self.store.execute(SQL(sql)))
        return result[0][0]


