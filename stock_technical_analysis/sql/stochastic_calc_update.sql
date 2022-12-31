insert into {stock}_stoch
(timestamp, high, low, close, high_high, low_low, cl_ll, hh_ll, per_k)
select f.timestamp,
    f.high,
    f.low,
    f.close,
    f.high_high,
    f.low_low,
    f.cl_ll,
    f.hh_ll,
    case 
        when f.hh_ll <> 0 then f.cl_ll / f.hh_ll * 100 
        else null 
    end as per_k
from (
        select t1.timestamp,
            t1.high,
            t1.low,
            t1.close,
            t1.high_high,
            t1.low_low,
            t1.close - t1.low_low as cl_ll,
            t1.high_high - t1.low_low as hh_ll
        from (
                select t.timestamp,
                    t.high,
                    t.low,
                    t.close,
                    case
                        when t.row_num >= {period} then (
                            select max(s.high)
                            from (
                                    select a.high
                                    from {stock} a
                                    where a.timestamp <= t.timestamp
                                    order by a.timestamp desc
                                    limit {period}
                                ) as s
                        )
                        else null
                    end as high_high,
                    case
                        when t.row_num >= {period} then (
                            select min(s.low)
                            from (
                                    select a.low
                                    from {stock} a
                                    where a.timestamp <= t.timestamp
                                    order by a.timestamp desc
                                    limit {period}
                                ) as s
                        )
                        else null
                    end as low_low
                from (
                        select row_number() over (
                                order by timestamp
                            ) as row_num,
                            timestamp,
                            high,
                            low,
                            close
                        from {stock} where 
                        timestamp >= (
                            select min(t11.timestamp) 
                            from (select timestamp 
                            from axisbank 
                            where timestamp <= '{timestamp}'
                            order by timestamp desc 
                            limit 14) t11)
                    ) as t
            ) as t1
    ) as f where f.timestamp > '{timestamp}';

-- insert into {stock}_stoch (
--         timestamp,
--         high,
--         low,
--         close,
--         high_high,
--         low_low,
--         cl_ll,
--         hh_ll,
--         per_k
--     )
-- select timestamp,
--     high,
--     low,
--     close,
--     high_high,
--     low_low,
--     cl_ll,
--     hh_ll,
--     per_k
-- from stochastic_vw where timestamp >= '{timestamp}';