# Gestión de Co-hosted Spaces

Este documento describe el proceso para ingerir datos de "Co-hosted Spaces" (episodios históricos o externos) en la base de datos de BandaWeb3 y regenerar el sitio web estático.

## 📄 Archivos de Entrada

Los datos se ingresan en archivos de texto en `website/inputs/`.
Formatos soportados: `co_hosted_spaces.txt`, `co_hosted_spaces_2.txt`, etc.

### Formato de Datos
El script espera bloques de texto copiados directamente de la interfaz de Spaces o listados similares:
```text
Co-hosted Spaces
[Nombre del Host]
[Handle]
[Título del Space]
[Idioma] - Ended: [Fecha] - Speakers: [N] - Duration: [Duración]
[Listeners]
PLAY / REPLAY
```

## 🛠️ Scripts de Procesamiento

### 1. Ingestión de Datos
**Script:** `scripts/import_co_hosted.py`
- Lee los archivos de texto configurados.
- Parsea fechas (incluyendo manejo de años implícitos).
- Genera IDs únicos (e.g., `20230213`, `20230213-2`).
- Actualiza `data/episodes_database.json`.

### 2. Actualización de Listeners
**Script:** `scripts/update_listener_counts.py`
- Escanea los mismos archivos de entrada.
- Extrae el número de oyentes (junto a "PLAY"/"REPLAY").
- Actualiza el campo `listeners` en la base de datos coincidiendo por título.

### 3. Generación del Sitio Web
**Script:** `scripts/generate_website.py`
- Lee `data/episodes_database.json`.
- Usa templates Jinja2 en `website/templates/`.
- Genera páginas estáticas en `website/output/`.
- Maneja formatos de duración complejos (e.g., "1h 27m").

## 🚀 Flujo de Trabajo (Batch Ingestion)

Para agregar un nuevo lote de episodios:

1.  **Guardar datos:** Crea un nuevo archivo (ej. `website/inputs/co_hosted_spaces_5.txt`) con los datos crudos.
2.  **Actualizar scripts:**
    *   Editar `scripts/import_co_hosted.py` para incluir el nuevo archivo en `input_files`.
    *   Editar `scripts/update_listener_counts.py` para incluir el nuevo archivo.
3.  **Ejecutar pipeline:**
    ```bash
    python3 scripts/import_co_hosted.py
    python3 scripts/update_listener_counts.py
    python3 scripts/generate_website.py
    ```
4.  **Verificar:**
    *   Revisar `data/episodes_database.json`.
    *   Verificar sitio generado en `website/output`.

## 🔄 Estado Actual (Batches 1-4)
- **Total Episodios:** 301 (incluyendo co-hosted).
- **Última actualización:** Batch 4 (Ene 2025).
- **Repositorio:** `https://github.com/mexiweb3/BandaWeb3.git`
