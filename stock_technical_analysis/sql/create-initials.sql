create table if not exists {stock} (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    open float not null,
    high float not null,
    low float not null,
    volume float not null
);

create table if not exists {stock}_rsi (
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

create table if not exists {stock}_macd (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    ema12 float,
    ema26 float,
    macd float,
    signal float,
    hist float
);

create table if not exists {stock}_stoch (
    index serial not null primary key,
    timestamp timestamp without time zone not null,
    close float not null,
    high float not null,
    low float not null,
    high_high float,
    low_low float,
    cl_ll float,
    hh_ll float,
    per_k float
)