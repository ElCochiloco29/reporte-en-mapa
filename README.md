# Reporte en Mapa

App web para hacer reportes fotográficos georreferenciados. Subes fotos tomadas con la ubicación activada, agregas título, tipo de daño y notas, y descargas un archivo KMZ que abre en Google Earth (celular y escritorio) con cada foto en su ubicación.

- Todo se procesa en el dispositivo; las fotos no se suben a ningún servidor.
- Fotos sin GPS se pueden ubicar a mano tocando el mapa.
- Cada punto del KMZ incluye enlaces para abrir la ubicación en Google Maps y Apple Maps.

## Uso

Abre la página publicada con GitHub Pages, o abre `index.html` en Chrome desde tu computadora.

`tools/make_kmz.py` genera el mismo KMZ desde la línea de comandos: `python3 tools/make_kmz.py salida.kmz fotos/*.jpg` (requiere Pillow).

También genera un PDF del reporte (portada con resumen por tipo de daño y dos fotos por página).

Bibliotecas incluidas en `lib/`: Leaflet 1.9.4, JSZip 3.10.1, exifr 7.1.3, jsPDF 2.5.2.
