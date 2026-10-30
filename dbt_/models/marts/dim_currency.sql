{{ config(
    materialized='external',
    location='s3://mlbvncs-valuemetrics-dev/gold/mercadolivre/celulares-e-telefones/dim_currency.parquet',
    format='parquet'
) }}

WITH currency_stg AS (
    SELECT *
    FROM {{ ref('stg_currency') }}
),

SELECT
    {{ dbt_utils.generate_surrogate_key(['currency', 'currency_raw']) }} AS currency_key,
    *
FROM currency_stg