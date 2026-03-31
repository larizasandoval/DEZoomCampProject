import requests
import json
import time
import urllib.parse 

def extraer_datos_crossref(query_url, max_total=5000):
    url = "https://api.crossref.org/works"
    cursor = '*'
    resultados_crudos = []
    
    print(f"Iniciando descarga de datos crudos para: {query_url}")

    while len(resultados_crudos) < max_total:
        params = {
            "query.affiliation": urllib.parse.quote(query_url),
            "filter": "type:journal-article",
            "rows": 1000, # Max permitido por página
            "cursor": cursor,
            "select": "title,DOI,URL,published,container-title,author",
            "mailto": "tu_correo@ejemplo.com" # Cambia esto por tu correo real
        }
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
        url_final = (
            f"{url}?query.affiliation={query_url}"
            f"&filter=type:journal-article"
            f"&rows=1000"
            f"&cursor={cursor}"
            f"&select=title,DOI,URL,published,container-title,author"
        )
        #print(params["query.affiliation"],"sooooooooo")
        try:
            response = requests.get(f"{url_final}", headers=headers, timeout=30)
            response.encoding = 'utf-8'  # Aseguramos la codificación correcta
            response.raise_for_status()
            #print(response.url)
            data = response.json()
            
            items = data.get("message", {}).get("items", [])
            if not items:
                break
            
            for item in items:
                # Extraemos la fecha de forma simple
                fecha_parts = item.get("published", {}).get("date-parts", [[None]])[0]
                # Guardamos solo lo esencial para procesar en BigQuery
                resultados_crudos.append({
                    "titulo": item.get("title", ["N/A"])[0],
                    "doi": item.get("DOI"),
                    "revista": item.get("container-title", ["N/A"])[0],
                    "fecha_raw": str(fecha_parts[0]) if fecha_parts[0] else None,
                    "enlace": item.get("URL"),
                    # Guardamos la lista de autores completa para procesar en SQL
                    "autores_raw": json.dumps(item.get("author", [])) 
                })

            cursor = data.get("message", {}).get("next-cursor")
            print(f"Descargados: {len(resultados_crudos)}...")

        except Exception as e:
            print(f"Error en la descarga: {e}")
            break

    return resultados_crudos

# --- EJECUCIÓN ---

mapeo_claves = [
    "Universidad Nacional Autónoma de Honduras",
    "Zamorano",
    "Universidad Pedagógica Nacional Francisco Morazán",
    "Universidad Tecnológica Centroamericana"
]

nombre_archivo = "science_production.jsonl"
total_global = 0

# Limpiamos el archivo al inicio por si vas a ejecutar el script varias veces
with open(nombre_archivo, "w", encoding="utf-8") as f:
    pass 

for institucion in mapeo_claves:
    print(f"\n--- Procesando: {institucion} ---")
    
    # Llamamos a tu función tal cual la tienes
    data_institucion = extraer_datos_crossref(institucion, max_total=5000)
    
    if data_institucion:
        # Guardamos los resultados de ESTA institución en el archivo (modo 'a' de append)
        with open(nombre_archivo, "a", encoding="utf-8") as f:
            for entrada in data_institucion:
                # Agregamos un campo extra para saber de qué búsqueda vino, 
                # útil si luego vas a filtrar en BigQuery
                entrada["query_origen"] = institucion 
                f.write(json.dumps(entrada) + "\n")
        
        total_global += len(data_institucion)
        print(f"Completado {institucion}. Registros añadidos: {len(data_institucion)}")

print(f"\n--- PROCESO FINALIZADO ---")
print(f"Archivo '{nombre_archivo}' generado con un total de {total_global} registros.")
