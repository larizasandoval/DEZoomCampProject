WITH base AS (
    SELECT 
        doi,
        -- Extraemos autores y sus afiliaciones del JSON
        --SAFE.PARSE_JSON(autores_raw) AS json_data
        SAFE.PARSE_JSON(REGEXP_REPLACE(TRIM(autores_raw, '"'), r'\\"', '"')) AS json_data
    FROM {{ source('science_production_raw_data', 'raw_science_production') }}
),

-- "Aplanamos" el JSON para tener una fila por cada afiliación de cada autor
extraer_afiliaciones AS (
    SELECT 
        doi,
        LOWER(JSON_VALUE(afi.name)) AS nombre_institucion_raw
    FROM base,
    UNNEST(JSON_QUERY_ARRAY(json_data)) AS autor,
    UNNEST(JSON_QUERY_ARRAY(autor.affiliation)) AS afi
)

-- Filtramos SOLO tus universidades de interés
SELECT *
FROM (
    SELECT DISTINCT
        doi,
        CASE 
            WHEN nombre_institucion_raw LIKE LOWER('%nacional autonoma de honduras%') 
                OR nombre_institucion_raw LIKE LOWER('%nacional autónoma de honduras%') 
                OR nombre_institucion_raw LIKE LOWER('%unah%') THEN 'UNAH'
            WHEN nombre_institucion_raw LIKE LOWER('%zamorano%') THEN 'Zamorano'
            WHEN nombre_institucion_raw LIKE LOWER('%Pedagógica Nacional Francisco Morazán%') 
                OR nombre_institucion_raw LIKE LOWER('%Pedagogica Nacional Francisco Morazan%') THEN 'UPNFM'
            WHEN nombre_institucion_raw LIKE LOWER('%Universidad tecnológica centroamericana%') 
                OR nombre_institucion_raw LIKE LOWER('%Universidad Tecnologica Centroamericana%') THEN 'UNITEC'
            WHEN nombre_institucion_raw LIKE LOWER('%Honduras%') 
                AND nombre_institucion_raw  NOT LIKE LOWER('%nacional autonoma de honduras%')
                AND nombre_institucion_raw NOT LIKE LOWER('%nacional autónoma de honduras%')
            THEN 'OTRO-Honduras'
            ELSE 'OTRA'
        END AS institution, nombre_institucion_raw
    FROM extraer_afiliaciones
) T
WHERE institution != 'OTRA'
   --nombre_institucion_raw LIKE LOWER('%UNIVERSIDAD NACIONAL AUTONOMA DE HONDURAS%') OR
   --nombre_institucion_raw LIKE LOWER('Zamorano') OR
   --nombre_institucion_raw LIKE LOWER('%Universidad Pedagógica Nacional Francisco Morazán%') 