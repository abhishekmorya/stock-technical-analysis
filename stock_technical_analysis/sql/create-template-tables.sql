create table if not exists rsi_template (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    gain float,
    loss float,
    avg_gain float,
    avg_loss float,
    rs float,
    rsi float
);

create table if not exists macd_template (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    ema12 float,
    ema26 float,
    macd float,
    signal float,
    hist float
);

create table if not exists stock_template (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    open float not null,
    high float not null,
    low float not null,
    volume float not null
);