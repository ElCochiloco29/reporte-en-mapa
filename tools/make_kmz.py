"""Genera un KMZ (Google Earth) a partir de fotos JPG con GPS en EXIF.

Uso: python3 make_kmz.py salida.kmz foto1.jpg foto2.jpg ...
Las fotos con la misma coordenada se agrupan en un solo punto.
"""
import io
import sys
import zipfile
from collections import OrderedDict
from datetime import datetime
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

MAX_SIDE = 1600


def dms_to_deg(dms, ref):
    d, m, s = (float(x) for x in dms)
    deg = d + m / 60 + s / 3600
    return -deg if ref in ("S", "W") else deg


def read_photo(path):
    im = Image.open(path)
    exif = im.getexif()
    gps = exif.get_ifd(0x8825)
    taken = exif.get_ifd(0x8769).get(36867) or exif.get(306)
    when = datetime.strptime(taken, "%Y:%m:%d %H:%M:%S") if taken else None
    if not gps or 2 not in gps or 4 not in gps:
        return None, when, im
    lat = dms_to_deg(gps[2], gps.get(1, "N"))
    lon = dms_to_deg(gps[4], gps.get(3, "E"))
    return (round(lat, 6), round(lon, 6)), when, im


def resized_jpeg(im):
    im = ImageOps.exif_transpose(im).convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return buf.getvalue()


def main(out, paths):
    points = OrderedDict()
    skipped = []
    photos = []
    for p in paths:
        coord, when, im = read_photo(p)
        if coord is None:
            skipped.append(p)
            continue
        photos.append((when or datetime.min, p, coord, im))
    photos.sort(key=lambda x: x[0])

    files = {}
    for i, (when, p, coord, im) in enumerate(photos, 1):
        name = f"files/foto_{i:03d}.jpg"
        files[name] = resized_jpeg(im)
        points.setdefault(coord, []).append((name, when))

    placemarks = []
    for n, ((lat, lon), items) in enumerate(points.items(), 1):
        first = items[0][1]
        imgs = "".join(
            f'<p><img src="{name}" width="480"/><br/>{when:%d/%m/%Y %H:%M:%S}</p>'
            for name, when in items
        )
        gmaps = f"https://www.google.com/maps/search/?api=1&amp;query={lat},{lon}"
        amaps = f"https://maps.apple.com/?ll={lat},{lon}&amp;q=Punto%20{n}"
        desc = (
            f"{imgs}<p>Coordenadas: {lat}, {lon}</p>"
            f'<p><a href="{gmaps}">Abrir en Google Maps</a> · '
            f'<a href="{amaps}">Abrir en Apple Maps</a></p>'
        )
        title = f"Punto {n}" + (f" ({len(items)} fotos)" if len(items) > 1 else "")
        placemarks.append(
            f"""  <Placemark>
    <name>{escape(title)}</name>
    <TimeStamp><when>{first:%Y-%m-%dT%H:%M:%S}</when></TimeStamp>
    <styleUrl>#foto</styleUrl>
    <description><![CDATA[{desc}]]></description>
    <Point><coordinates>{lon},{lat},0</coordinates></Point>
  </Placemark>"""
        )

    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
  <name>Reporte fotográfico</name>
  <Style id="foto">
    <IconStyle><scale>1.1</scale>
      <Icon><href>http://maps.google.com/mapfiles/kml/shapes/camera.png</href></Icon>
    </IconStyle>
  </Style>
{chr(10).join(placemarks)}
</Document>
</kml>
"""
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("doc.kml", kml)
        for name, data in files.items():
            z.writestr(name, data)
    print(f"{len(photos)} fotos, {len(points)} puntos, {len(skipped)} sin GPS: {skipped}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
