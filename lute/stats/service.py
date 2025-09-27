"""
Calculating stats.
"""

from datetime import datetime, timedelta
from sqlalchemy import text
from lute.models.repositories import UserSettingRepository


def get_streaks_data(session):
    "Get daily goal and streaks data."
    us_repo = UserSettingRepository(session)
    goal_minutes = int(us_repo.get_value("daily_reading_goal") or 15)
    goal_seconds = goal_minutes * 60

    sql = """
    SELECT date(read_date, 'localtime') as d, SUM(duration_seconds) as total_seconds
    FROM reading_tracking
    GROUP BY d
    ORDER BY d DESC
    """
    result = session.execute(text(sql)).all()
    
    read_days = {datetime.strptime(row[0], '%Y-%m-%d').date(): row[1] for row in result}

    today = datetime.now().date()
    
    todays_seconds = read_days.get(today, 0)

    streak = 0
    check_day = today
    if read_days.get(check_day, 0) < goal_seconds:
        check_day = today - timedelta(days=1)

    while read_days.get(check_day, 0) >= goal_seconds:
        streak += 1
        check_day -= timedelta(days=1)

    return {
        "goal": goal_minutes,
        "todays_progress_percent": min(100, (todays_seconds / goal_seconds) * 100) if goal_seconds > 0 else 0,
        "current_streak": streak,
        "goal_met_today": todays_seconds >= goal_seconds
    }


def _get_data_per_lang(session):
    "Return dict of lang name to dict[date_yyyymmdd}: count"
    ret = {}
    sql = """
    select lang, dt, sum(WrWordCount) as count
    from (
      select LgName as lang, strftime('%Y-%m-%d', WrReadDate) as dt, WrWordCount
      from wordsread
      inner join languages on LgID = WrLgID
    ) raw
    group by lang, dt
    """
    result = session.execute(text(sql)).all()
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


def get_chart_data(session):
    "Get data for chart for each language."
    raw_data = _get_data_per_lang(session)
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


def get_table_data(session):
    "Wordcounts by lang in time intervals."
    raw_data = _get_data_per_lang(session)

    ret = []
    for langname, readbydate in raw_data.items():
        ret.append({"name": langname, "counts": _readcount_by_date(readbydate)})
    return ret

def get_time_tracking_data(session):
    "Get time tracking data for each book."
    sql = """
    SELECT b.BkID, b.BkTitle, rt.id, rt.read_date, rt.duration_seconds
    FROM reading_tracking rt
    JOIN books b ON b.BkID = rt.book_id
    ORDER BY b.BkTitle, rt.read_date DESC
    """
    result = session.execute(text(sql)).all()
    
    from collections import defaultdict
    import pandas as pd
    books_data = defaultdict(lambda: {'total_seconds': 0, 'entries': []})
    
    for row in result:
        book_id = row[0]
        book_title = row[1]
        entry_id = row[2]
        read_date = row[3]
        duration_seconds = row[4]
        
        books_data[book_title]['total_seconds'] += duration_seconds
        books_data[book_title]['entries'].append({
            'id': entry_id,
            'date': pd.to_datetime(read_date, format='mixed'),
            'duration': f"{duration_seconds // 60} min, {duration_seconds % 60} sec"
        })
        
    ret = []
    for title, data in books_data.items():
        total_minutes = data['total_seconds'] / 60
        ret.append({
            'book': title,
            'total_minutes': total_minutes,
            'entries': data['entries']
        })
        
    return ret