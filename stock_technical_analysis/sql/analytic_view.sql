create or replace view analytic_vw as (
    select d.stock, d.timestamp, d.close, d.macd, d.signal, d.hist, d.rsi, d.per_k from (
        {queries}
    ) d
);