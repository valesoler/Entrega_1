import xml.etree.ElementTree as ET      # Permite parsear XML, navegar por sus nodos (Element) y obtener textos
import csv                              # Facilita escribir y leer archivos en formato CSV/TSV con control de delimitador.
import re                               # Importa el módulo de expresiones regulares (regex) para manipular texto

input_file = "all_sequence_variants.xml"
output_file = "all_sequence_variants.tsv"

# Carga y parsea el archivo XML desde disco a una estructura ElementTree

with open(input_file, "r", encoding="utf-8") as f:
    contenido = f.read()

# Eliminar cualquier cabecera <?xml ... ?> que pueda aparecer repetida o causar problemas y reemplaza todas las coincidencias por "".

contenido = re.sub(r"<\?xml.*?\?>", "", contenido)
if not contenido.strip().startswith("<root>"):
    contenido = "<root>\n" + contenido + "\n</root>"
root = ET.fromstring(contenido)

lista = []  # cada item: (id_int, id_text, variation, position, external_link, condition, indication)

# Recorre todas las etiquetas <sequence_variant> que existan en cualquier nivel bajo root
for variant in root.findall(".//sequence_variant"):
    id_text = (variant.findtext("id") or "").strip()
    try:
        id_int = int(id_text)
    except Exception:
        id_int = None

    variation = (variant.findtext("variation") or "").strip()
    position = (variant.findtext("position") or "").strip()
    external_link = (variant.findtext("external_link") or "").strip()

    measurements = variant.findall(".//sequence_variant_measurement")
    if not measurements:
        # sin mediciones -> fila vacía en condition/indication
        lista.append((id_int, id_text, variation, position, external_link, "", ""))
    else:
        for m in measurements:
            conds = [ (c.text or "").strip() for c in m.findall("condition") ]
            inds = [ (i.text or "").strip() for i in m.findall("indication_types") ]
            if not conds and not inds:
                lista.append((id_int, id_text, variation, position, external_link, "", ""))
            else:
                maxn = max(len(conds), len(inds))
                for i in range(maxn):
                    condition = conds[i] if i < len(conds) else ""
                    indication = inds[i] if i < len(inds) else ""
                    lista.append((id_int, id_text, variation, position, external_link, condition, indication))

# Ordenar por ID numérico ascendente (los IDs vacíos van al final)
lista.sort(key=lambda x: (x[0] if x[0] is not None else float('inf'), x[1]))

# Escribir TSV con fila encabezados

encabezados = ["id", "variation", "position", "external_link", "condition", "indication"]

with open(output_file, "w", newline="", encoding="utf-8") as out:
    writer = csv.writer(out, delimiter="\t")

    writer.writerow(encabezados)
    for rec in lista:
        # rec = (id_int, id_text, variation, position, external_link, condition, indication)
        writer.writerow([rec[1], rec[2], rec[3], rec[4], rec[5], rec[6]])

# Imprimir tabla en consola (primera la fila encabezados, luego datos ordenados)

print("\t".join(encabezados))
for rec in lista:
    print(f"{rec[1]}\t{rec[2]}\t{rec[3]}\t{rec[4]}\t{rec[5]}\t{rec[6]}")

print(f"\n Archivo TSV generado: {output_file} — {len(lista)} filas de datos (excluyendo la 1 fila de cabecera).")
