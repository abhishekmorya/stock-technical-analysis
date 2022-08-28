INSERT INTO {rsitable}(timestamp, close)
    SELECT
    timestamp,
    close
    FROM {stocktable}
    WHERE 
    timestamp > '{timestamp_rsi}';

INSERT INTO {macdtable}(timestamp, close)
    SELECT
    timestamp,
    close
    FROM {stocktable}
    WHERE 
    timestamp > '{timestamp_macd}';