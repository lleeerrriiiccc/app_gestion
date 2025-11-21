from fpdf import FPDF
import database as db
import os
def generate_invoice(pedido):
    pedido_data = db.get_pedido(pedido)
    pedido_lines = db.get_pedido_lines(pedido)
    factura_num = db.last_invoice_number() + 1
    storage = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'files', 'bills'))
    filename = pedido_data["cliente_nombre"].replace(" ", "_") + f"_factura_{factura_num}.pdf"
    path = os.path.join(storage, filename)
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("arial", "", ".\\python\\ARIAL.TTF", uni=True)
    pdf.set_font("arial", size=16)

    pdf.cell(200, 10, txt=f"Factura #{factura_num}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {pedido_data['cliente_nombre']}", ln=True)
    pdf.cell(200, 10, txt=f"Fecha: {pedido_data['fecha_taller']}", ln=True)
    pdf.ln(10)

    # Tabla de productos
    pdf.cell(80, 10, "Producto", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(40, 10, "Precio Unitario", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    

    for line in pedido_lines:
        pdf.cell(80, 10, line["producto_nombre"], 1)
        pdf.cell(30, 10, str(line["cantidad"]), 1)
        pdf.cell(40, 10, str(line["producto_precio"]) + "€", 1)
        pdf.cell(40, 10, str((str(line["cantidad"] * line["producto_precio"]))) + "€", 1)
        pdf.ln()

    total_amount = sum(line["cantidad"] * line["producto_precio"] for line in pedido_lines)
    pdf.cell(0, 10, f"Total: {total_amount}€", ln=True, align="R")
    pdf.output(path)

    return path

