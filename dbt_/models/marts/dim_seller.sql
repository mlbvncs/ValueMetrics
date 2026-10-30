{{ config(
    materialized='external',
    location='s3://mlbvncs-valuemetrics-dev/gold/mercadolivre/celulares-e-telefones/dim_seller.parquet',
    format='parquet'
) }}

WITH seller_stg AS (
    SELECT *
    FROM {{ ref('stg_seller') }}
),

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'seller_id', 'seller_name', 'seller_city', 'seller_state', 
        'seller_country', 'is_best_seller', 'is_power_seller', 'power_seller_status_title'
    ]) }} AS seller_key,
    *
FROM seller_stg