SELECT 
    doi,
    titulo as title,
    revista as magazine,
    fecha_raw AS year,
    enlace as url
FROM {{ source('science_production_raw_data', 'raw_science_production') }}
-- Solo incluimos las que tienen al menos un autor de nuestras universidades
WHERE doi IN (SELECT doi FROM {{ ref('stg_afiliations') }})