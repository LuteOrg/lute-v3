"""
Calculating stats.
"""

from datetime import datetime, timedelta
from sqlalchemy import text
from lute.db import db


def _get_data_per_lang():
    "Return dict of lang name to dict[date_yyyymmdd}: count"
    ret = {}
    sql = """
    select lang, dt, sum(TxWordCount) as count
    from (
      select LgName as lang, strftime('%Y-%m-%d', TxReadDate) as dt, TxWordCount
      from texts
      inner join books on BkID = TxBkID
      inner join languages on LgID = BkLgID
      where TxWordCount is not null
      and TxReadDate is not null
    ) raw
    group by lang, dt
    """
    result = db.session.execute(text(sql)).all()
    for row in result:
        langname = row[0]
        if langname not in ret:
            ret[langname] = {}
        ret[langname][row[1]] = int(row[2])
    return ret


def _charting_data(readbydate):
    "Calc data and running total."
    dates = sorted(readbydate.keys())
    if len(dates) == 0:
        return []

    # The line graph needs somewhere to start from for a line
    # to be drawn on the first day.
    first_date = datetime.strptime(dates[0], "%Y-%m-%d")
    day_before_first = first_date - timedelta(days=1)
    dbf = day_before_first.strftime("%Y-%m-%d")
    data = [{"readdate": dbf, "wordcount": 0, "runningTotal": 0}]

    total = 0
    for d in dates:
        dcount = readbydate.get(d)
        total += dcount
        hsh = {"readdate": d, "wordcount": dcount, "runningTotal": total}
        data.append(hsh)
    return data


def get_chart_data():
    "Get data for chart for each language."
    raw_data = _get_data_per_lang()
    chartdata = {}
    for k, v in raw_data.items():
        chartdata[k] = _charting_data(v)
    return chartdata


def _readcount_by_date(readbydate):
    """
    Return data as array: [ today, week, month, year, all time ]

    This may be inefficient, but will do for now.
    """
    today = datetime.now().date()

    def _in_range(i):
        start_date = today - timedelta(days=i)
        dates = [
            start_date + timedelta(days=x) for x in range((today - start_date).days + 1)
        ]
        ret = 0
        for d in dates:
            df = d.strftime("%Y-%m-%d")
            ret += readbydate.get(df, 0)
        return ret

    return {
        "day": _in_range(0),
        "week": _in_range(6),
        "month": _in_range(29),
        "year": _in_range(364),
        "total": _in_range(3650),  # 10 year drop off :-P
    }


def get_table_data():
    "Wordcounts by lang in time intervals."
    raw_data = _get_data_per_lang()

    ret = []
    for langname, readbydate in raw_data.items():
        ret.append({"name": langname, "counts": _readcount_by_date(readbydate)})
    return ret
