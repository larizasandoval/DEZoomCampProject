--{{ config(materialized='table') }}

SELECT 
    p.doi,
    p.title,
    p.magazine,
    p.year,
    p.url,
    a.institution
FROM {{ ref('stg_afiliations') }} a
JOIN {{ ref('stg_works') }} p
  ON p.doi = a.doi