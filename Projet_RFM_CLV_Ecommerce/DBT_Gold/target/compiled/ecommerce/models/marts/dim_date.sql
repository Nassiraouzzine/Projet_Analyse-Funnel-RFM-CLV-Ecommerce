with spine as (
    select unnest(
        generate_series(
            date '2010-12-01',
            date '2011-12-31',
            interval '1 day'
        )
    ) as date_day
)
select
    date_day,
    year(date_day)                      as year,
    month(date_day)                     as month,
    week(date_day)                      as week_num,
    dayofweek(date_day)                 as weekday_num,
    dayname(date_day)                   as weekday_name,
    monthname(date_day)                 as month_name,
    month(date_day) in (11, 12)         as is_peak_season,
    case
        when strftime(date_day, '%m-%d') between '02-10' and '02-16'
            then 'Valentines'
        when strftime(date_day, '%m-%d') between '12-15' and '12-31'
            then 'Christmas'
        when strftime(date_day, '%m-%d') between '10-25' and '10-31'
            then 'Halloween'
        else null
    end                                 as commercial_event
from spine