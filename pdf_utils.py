from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from datetime import datetime

# Registrar fuente compatible con acentos
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

def generar_factura_pdf(factura, cliente, logo_path, output_path):
    doc = SimpleDocTemplate(output_path, pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", fontName="HeiseiMin-W3", fontSize=18, leading=22, spaceAfter=10, alignment=1))
    styles.add(ParagraphStyle(name="Subtitulo", fontName="HeiseiMin-W3", fontSize=12, leading=16, spaceAfter=6, alignment=0))
    styles.add(ParagraphStyle(name="Normal", fontName="HeiseiMin-W3", fontSize=10, leading=14))

    # Logo y encabezado
    header_data = []
    if logo_path:
        try:
            logo = Image(logo_path, width=100, height=60)
            header_data.append([logo, Paragraph("<b>Luzured</b><br/>CUIT: 30-12345678-9<br/>Fecha: {}<br/>Número: {}".format(
                factura.get("fecha_emision", datetime.now().strftime("%Y-%m-%d")),
                factura.get("id", "-")
            ), styles["Normal"])])
        except Exception:
            header_data.append(["", Paragraph("Luzured<br/>CUIT: 30-12345678-9", styles["Normal"])])
    else:
        header_data.append(["", Paragraph("Luzured<br/>CUIT: 30-12345678-9", styles["Normal"])])

    header = Table(header_data, colWidths=[120, 400])
    elements.append(header)
    elements.append(Spacer(1, 20))

    # Título
    tipo = factura.get("tipo", "X")
    titulo = "Factura {}".format(tipo) if tipo in ["A", "B", "C"] else "Presupuesto (X)"
    elements.append(Paragraph(titulo, styles["Titulo"]))
    elements.append(Spacer(1, 15))

    # Datos cliente
    datos_cliente = [
        ["Cliente:", cliente.get("nombre", "")],
        ["N° Cliente:", cliente.get("numero_cliente", "")],
        ["Descripción:", factura.get("descripcion", "")]
    ]
    tabla_cliente = Table(datos_cliente, colWidths=[100, 400])
    tabla_cliente.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.black),
        ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONTNAME", (0,0), (-1,-1), "HeiseiMin-W3"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
    ]))
    elements.append(tabla_cliente)
    elements.append(Spacer(1, 20))

    # Tabla detalle (ejemplo con una sola línea porque no tenemos items separados)
    detalle = [
        ["Descripción", "Cantidad", "Precio Unitario", "Subtotal"],
        [factura.get("descripcion", "Servicio contratado"), "1",
         "${:,.2f}".format(float(factura.get("monto", 0))),
         "${:,.2f}".format(float(factura.get("monto", 0)))]
    ]
    tabla_detalle = Table(detalle, colWidths=[250, 80, 100, 100])
    tabla_detalle.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,-1), "HeiseiMin-W3"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
    ]))
    elements.append(tabla_detalle)
    elements.append(Spacer(1, 20))

    # Totales
    subtotal = float(factura.get("monto", 0))
    iva = subtotal * 0.21 if tipo in ["A", "B", "C"] else 0
    total = subtotal + iva

    totales = [
        ["Subtotal", "${:,.2f}".format(subtotal)],
        ["IVA 21%", "${:,.2f}".format(iva)],
        ["Total", "${:,.2f}".format(total)]
    ]
    tabla_totales = Table(totales, colWidths=[430, 100])
    tabla_totales.setStyle(TableStyle([
        ("ALIGN", (1,0), (-1,-1), "RIGHT"),
        ("FONTNAME", (0,0), (-1,-1), "HeiseiMin-W3"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("LINEABOVE", (0,2), (-1,2), 1, colors.black),
        ("TEXTCOLOR", (0,2), (-1,2), colors.black),
        ("FONTNAME", (0,2), (-1,2), "HeiseiMin-W3"),
        ("FONTSIZE", (0,2), (-1,2), 12),
    ]))
    elements.append(tabla_totales)
    elements.append(Spacer(1, 30))

    # Footer
    if tipo == "X":
        footer = Paragraph("Este comprobante no es válido como factura oficial.", styles["Normal"])
    else:
        footer = Paragraph("Gracias por su compra. Este comprobante cumple con las normas de AFIP (Argentina).", styles["Normal"])
    elements.append(footer)

    # Construir PDF
    doc.build(elements)
