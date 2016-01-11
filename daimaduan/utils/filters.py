# coding: utf-8
import time


def datetimeformat(value):
    """filter for Jinja2"""
    return value.strftime("%Y-%m-%d %H:%M:%S")


MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY
YEAR = 12 * MONTH


def time_passed(value):
    """filter for Jinjia2"""
    time_diff = int(time.time() - time.mktime(value.timetuple()))
    if time_diff < MINUTE:
        quantity = time_diff
        unit = u'秒'
    if time_diff >= MINUTE and time_diff < HOUR:
        quantity = time_diff / MINUTE
        unit = u'分钟'
    if time_diff >= HOUR and time_diff < DAY:
        quantity = time_diff / HOUR
        unit = u'小时'
    if time_diff >= DAY and time_diff < MONTH:
        quantity = time_diff / DAY
        unit = u'天'
    if time_diff >= MONTH and time_diff < YEAR:
        quantity = time_diff / MONTH
        unit = u'月'
    if time_diff >= YEAR:
        quantity = time_diff / YEAR
        unit = u'年'

    return u'%s %s前' % (quantity, unit)


def ternary(value, x, y):
    """Ternary operator simulator

    This filter

        {{ is_worked | ternary('Yes', 'No') }}

    works as the following code in other language

        is_worked ? 'Yes' : 'No'
    """

    if value:
        return x
    else:
        return y
