import calendar
from datetime import (
    datetime,
    timedelta,
    tzinfo
)
from typing import Union

from dateutil.relativedelta import relativedelta
from pytz import timezone

from utils.altcollections import ExtDict


class DatetimeResponse(datetime):
    def __eq__(self, other):
        if isinstance(other, str):
            try:
                other = datetime.fromisoformat(
                    other)  # '%Y-%m-%dT%H:%M:%S.%f%z'
            except ValueError:
                pass
        return datetime.__eq__(self, other)

    def __add__(self, other):
        if isinstance(other, dict):
            return self.calculate(**other)
        return datetime.__add__(self, other)

    def __sub__(self, other):
        if isinstance(other, dict):
            return self.calculate(**{x: -y for x, y in other.items()})
        return datetime.__sub__(self, other)

    def calculate(self, year=0, month=0, hours=0, minutes=0, days=0):
        date = self
        date += relativedelta(years=year, months=month, days=days,
                              hours=hours, minutes=minutes)
        return date


class MSK(tzinfo):

    def tzname(self, dt):
        return 'GMT +3'

    def utcoffset(self, dt):
        return timedelta(hours=3)

    def dst(self, dt):
        return timedelta(0)


class UTC(tzinfo):

    def tzname(self, dt):
        return 'UTC'

    def utcoffset(self, dt):
        return timedelta(hours=0)

    def dst(self, dt):
        return timedelta(0)


class MoscowDateTime:
    """
    Московская дата и время
    """
    tz_msk = MSK()
    tz_utc = UTC()

    @classmethod
    def now(cls, *,
            year=0,
            month=0,
            hours=0,
            minutes=0,
            days=0,
            formating: str = None,
            date_string: str = None,
            **kwargs) -> Union[str, datetime]:
        """
        Строковое значение текущее/относительное время

        :param year: (+/-) прибавляет/отнимает от текущего времени Год
        :type year: int
        :param month: (+/-) прибавляет/отнимает от текущего времени Месяц
        :type month: int
        :param hours: (+/-) прибавляет/отнимает от текущего времени Часы
        :type hours: int
        :param minutes: (+/-) прибавляет/отнимает от текущего времени Минуты
        :type minutes: int
        :param days: (+/-) прибавляет/отнимает от текущего времени Дни
        :type days: int
        :param formating: Возможные значения:
        * **iso-python** - пример return'a: "2018-07-20T12:27:59+03:00"
        * **iso-python-utc** - пример return'a: "2018-07-20T12:27:59+03:00"
        * **iso-datetime-with-tz** - пример return'a: "2018-07-20T12:27:59+0300"
        * **iso-datetime** - пример return'a: "2018-07-20T12:27:59"
        * **iso-date-time** - пример return'a: "2018-07-20 12:27:59"
        * **iso-date-time-utc** - пример return'a: "2018-07-20 12:27:59"
        * **iso-date** - пример return'a: "2018-07-20"
        * **iso-date-and-schedule-time** - пример return'a: "2021-06-11 11:20"
        * **schedule-time** - пример return'a: "12:30"
        * **weekday** - пример return'a: "Monday"
        * **weekday_number** - пример return'a: "1"
        * **time** - пример return'a: "12:30:35"
        * **iso8601_utcnow** - пример return'a: "2019-07-31T13:35:14.000001Z"
        * **iso8601_now** - пример return'a: "2019-07-31T16:34:23.000001Z+0300"
        * **event_bus** - пример return'a: "2019-07-31T16:34:23.000001z"
        :type formating: str
        :param date_string: дата и время в формате ISO. Если задана, отсчёт идёт относительно неё.
        :type date_string: str
        :return: Строковое значение текущего/относительного времени
        :rtype: str
        """
        date = None
        if date_string:
            date = datetime.fromisoformat(date_string)

        if formating in {
            'iso8601_utcnow',
            'iso-python-utc',
            'iso-date-time-utc',
            'iso-date-and-schedule-time',
        }:
            if date:
                date = date.replace(microsecond=0)
            else:
                date = datetime.utcnow().replace(microsecond=0)
        elif date:
            date = date.astimezone(tz=cls.tz_msk).replace(microsecond=0)
        else:
            date = datetime.now(tz=cls.tz_msk).replace(microsecond=0)

        date += relativedelta(years=year, months=month, days=days,
                              hours=hours, minutes=minutes)

        date_pattern_matching = {
            'iso-python': date.isoformat(),
            'iso-python-utc': date.isoformat(),
            'iso-datetime-with-tz': date.strftime('%Y-%m-%dT%H:%M:%S%z'),
            'iso-datetime': date.strftime('%Y-%m-%dT%H:%M:%S'),
            'iso-datetime-th-i': date.strftime('%Y-%m-%dT%H.%M'),
            'iso-date-time': date.strftime('%Y-%m-%d %H:%M:%S'),
            'iso-date-time-utc': date.strftime('%Y-%m-%d %H:%M:%S'),
            'iso-date': date.strftime('%Y-%m-%d'),
            'iso-date-and-schedule-time': date.strftime('%Y-%m-%d %H:%M'),
            'time': date.strftime('%H:%M:%S'),
            'schedule-time': date.strftime('%H:%M'),
            'weekday': calendar.day_name[date.weekday()],
            # получаем индекс текущего дня недели:
            'weekday_number': date.weekday(),
            'iso8601_utcnow': date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'iso8601_now': date.strftime('%Y-%m-%dT%H:%M:%S.%fZ%z'),
            'event_bus': date.strftime('%Y-%m-%dT%H:%M:%S.%fz')
        }

        if kwargs.get("dt_obj"):
            return date
        return date_pattern_matching.get(formating,
                                         date_pattern_matching['iso-python'])

    @classmethod
    def date_time(
        cls, *, year=0, month=0, hours=0, minutes=0, days=0, seconds=0
    ) -> datetime:
        date = DatetimeResponse.now(tz=cls.tz_msk).replace(microsecond=0)
        date += relativedelta(years=year, months=month, days=days,
                              hours=hours, minutes=minutes, seconds=seconds)
        return date

    @classmethod
    def formatted_date(cls, date: datetime, isoformat: bool = False) -> str:
        """
        Преобразует datetime object к формату 2018-02-14T15:37:42+0300
        """
        if isoformat:
            return date.replace(tzinfo=cls.tz_msk).isoformat()
        return date.strftime('%Y-%m-%dT%H:%M:%S%z')

    @classmethod
    # получаем дату текущей недели по индексу дня недели (от 0 до 6)
    def get_date_by_weekday(cls, weekday, iso_datetime: bool = False,
                            hour=0, minute=0, second=0, microsecond=0) -> str:
        date = datetime.now(tz=cls.tz_msk)
        date = date.replace(hour=hour, minute=minute,
                            second=second, microsecond=microsecond)
        sunday_date = date + timedelta(days=weekday - date.weekday())
        if iso_datetime:
            return sunday_date.isoformat()
        return datetime.strftime(sunday_date, "%Y.%m.%d %H:%M:%S")

    @classmethod
    def unixtime(cls,
                 *,
                 year=0,
                 month=0,
                 hours=0,
                 minutes=0,
                 days=0,
                 seconds=0):
        return int(
            cls.date_time(**ExtDict(locals()).crop('cls')).timestamp())


class UtcDateTime(MoscowDateTime):
    tz = UTC()


class ParseString:

    @classmethod
    def to_datetime(cls, str_date):
        if str_date[-3] == ':':
            str_date = str_date[:-3] + str_date[-2:]
        return datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S%z')

    @classmethod
    def to_datetime_from_response_header(cls, str_date):
        return datetime.strptime(str_date, '%a, %d %b %Y %H:%M:%S %Z')

    @classmethod
    def to_datetime_from_iso8601_utcnow(cls, str_date):
        return datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%fZ')


class TimeZone:

    @classmethod
    def change_timezone(cls, date, tz):
        format_date = '%Y-%m-%d %H:%M:%S%z'
        str_to_date = datetime.strptime(date.replace('T', ' '), format_date)
        date_utc = str_to_date.astimezone(timezone('UTC'))
        date_tz = date_utc.astimezone(timezone(tz))
        return date_tz.strftime("%Y-%m-%d %H:%M:%S")


def is_time_in_range(start: datetime, end: datetime, now: datetime):
    """Return true if now is in the range [start, end]"""
    if start <= end:
        return start <= now <= end
    return start <= now or now <= end
