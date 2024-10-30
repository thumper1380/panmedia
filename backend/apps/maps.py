from datetime import datetime
from datetime import timedelta

_1_day = timedelta(days=1)
_3_days = timedelta(days=3)
_1_week = timedelta(weeks=1)
_1_month = timedelta(days=30)
_1_year = timedelta(days=365)


def today():
    return datetime.now()


yesterday = today() - _1_day
last3Days = today() - _1_day * 2
last7Days = today() - _1_week
last30Days = today() - _1_month
last60Days = today() - _1_month * 2
lastYear = today() - _1_year
last10years = today() - (_1_year * 10)


def getRange(date, source):
    switch = {
        "rvc": getRVCRange(date),
        "trv": getThriveRange(date),
        "zpk": getZPKRange(date),
        "mgd": getMGDRange(date),
    }
    try:
        return switch[source]
    except BaseException:
        return switch['mgd']


def getCustomRange(startDate, endDate, source):
    start_date_unix = datetime.fromtimestamp(int(startDate))
    end_date_unix = datetime.fromtimestamp(int(endDate))
    switch = {
        "mgd": {
            "startDate": getMGDFormat(start_date_unix),
            "endDate": getMGDFormat(end_date_unix),
        },
        "zpk": {
            "startDate": getZPKFormat(start_date_unix),
            "endDate": getZPKFormat(end_date_unix),
        },
        "trv": {
            "startDate": getThriveFormat(start_date_unix),
            "endDate": getThriveFormat(end_date_unix),
        },
        "rvc": {
            "startDate": getRVCFormat(start_date_unix),
            "endDate": getRVCFormat(end_date_unix),
        },
        "dgtl7": {
            "startDate": getDGTL7Format(start_date_unix),
            "endDate": getDGTL7Format(end_date_unix),
        },
    }
    try:
        return switch[source]
    except BaseException:
        return switch['mgd']


def fix_num(n):
    if(n < 10):
        return '{}{}'.format(0, n)
    return n


def getThriveFormat(date):
    return '{month}/{day}/{year}'.format(
        month=fix_num(
            date.month), day=fix_num(
            date.day), year=fix_num(
                date.year))


def getThriveRange(key):
    switch = {
        "today": {
            "from": getThriveFormat(today()),
            "to": getThriveFormat(today())
        },
        "yesterday": {
            "from": getThriveFormat(yesterday),
            "to": getThriveFormat(yesterday)
        },
        "last3Days": {
            "from": getThriveFormat(last3Days),
            "to": getThriveFormat(today())
        },
        "lastSeven": {
            "from": getThriveFormat(last7Days),
            "to": getThriveFormat(today())
        },
        "last30Days": {
            "from": getThriveFormat(last30Days),
            "to": getThriveFormat(today())
        },
        "last60Days": {
            "from": getThriveFormat(last60Days),
            "to": getThriveFormat(today())
        },
        "all": {
            "from": getThriveFormat(last10years),
            "to": getThriveFormat(today())
        },
    }
    try:
        return switch[key]
    except BaseException:
        return switch['today']


def getRVCFormat(date):
    return '{year}-{month}-{day}'.format(
        month=fix_num(
            date.month), day=fix_num(
            date.day), year=fix_num(
                date.year))


def getRVCRange(key):
    siwtch = {
        "today": {
            "from": getRVCFormat(today()),
            "to": getRVCFormat(today())
        },
        "yesterday": {
            "from": getRVCFormat(yesterday),
            "to": getRVCFormat(yesterday)
        },
        "last3Days": {
            "from": getRVCFormat(last3Days),
            "to": getRVCFormat(today())
        },
        "lastSeven": {
            "from": getRVCFormat(last7Days),
            "to": getRVCFormat(today())
        },
        "last30Days": {
            "from": getRVCFormat(last30Days),
            "to": getRVCFormat(today())
        },
        "last60Days": {
            "from": getRVCFormat(last60Days),
            "to": getRVCFormat(today())
        },
        "all": {
            "from": getRVCFormat(last10years),
            "to": getRVCFormat(today())
        },
    }
    try:

        return siwtch[key]
    except BaseException:
        return siwtch['today']


def getZPKFormat(date):
    return '{day}/{month}/{year}'.format(
        month=fix_num(
            date.month), day=fix_num(
            date.day), year=fix_num(
                date.year))


def getZPKRange(key):
    siwtch = {
        "today": {
            "from": getZPKFormat(today()),
            "to": getZPKFormat(today())
        },
        "yesterday": {
            "from": getZPKFormat(yesterday),
            "to": getZPKFormat(yesterday)
        },
        "last3Days": {
            "from": getZPKFormat(last3Days),
            "to": getZPKFormat(today())
        },
        "lastSeven": {
            "from": getZPKFormat(last7Days),
            "to": getZPKFormat(today())
        },
        "last30Days": {
            "from": getZPKFormat(last30Days),
            "to": getZPKFormat(today())
        },
        "last60Days": {
            "from": getZPKFormat(last60Days),
            "to": getZPKFormat(today())
        },
        "all": {
            "from": getZPKFormat(last60Days),
            "to": getZPKFormat(today())
        },
    }
    try:

        return siwtch[key]
    except BaseException:
        return siwtch['today']


def getMGDFormat(date):
    return '{year}-{month}-{day}'.format(
        month=fix_num(
            date.month), day=fix_num(
            date.day), year=fix_num(
                date.year))


def getMGDRange(key):
    siwtch = {
        "today": {
            "from": getMGDFormat(today()),
            "to": getMGDFormat(today())
        },
        "yesterday": {
            "from": getMGDFormat(yesterday),
            "to": getMGDFormat(yesterday)
        },
        "last3Days": {
            "from": getMGDFormat(last3Days),
            "to": getMGDFormat(today())
        },
        "lastSeven": {
            "from": getMGDFormat(last7Days),
            "to": getMGDFormat(today())
        },
        "last30Days": {
            "from": getMGDFormat(last30Days),
            "to": getMGDFormat(today())
        },
        "last60Days": {
            "from": getMGDFormat(last60Days),
            "to": getMGDFormat(today())
        },
        "all": {
            "from": getMGDFormat(last60Days),
            "to": getMGDFormat(today())
        },
    }
    try:

        return siwtch[key]
    except BaseException:
        return siwtch['today']


def getDGTL7Format(date):
    return '{year}-{month}-{day}'.format(
        month=fix_num(
            date.month), day=fix_num(
            date.day), year=fix_num(
                date.year))
