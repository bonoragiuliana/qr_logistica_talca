import mysql.connector
import qrcode
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from PIL import Image
from datetime import datetime
import tempfile
import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import win32api
import win32print
from dotenv import load_dotenv
import os
# ---------- CONEXIÓN A BASE DE DATOS ----------

load_dotenv()

conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE"),
)

cursor = conexion.cursor()

# ---------- OBTENER PRODUCTOS ----------
def obtener_productos():
    cursor.execute("SELECT id_producto, descripcion FROM productos")
    return cursor.fetchall()

# ---------- GENERAR E IMPRIMIR QRs ----------
def generar_y_imprimir_qrs(id_producto, descripcion, cantidad):
    cursor.execute("SELECT ultimo_nro_serie FROM productos WHERE id_producto = %s", (id_producto,))
    resultado = cursor.fetchone()
    if not resultado:
        messagebox.showerror("Error", "Producto no encontrado.")
        return

    nro_serie = resultado[0]
    fecha_actual = datetime.now().strftime("%d/%m/%y")
    numero_lote = fecha_actual.replace("/", "")

    # Crear PDF temporal
    pdf_path = os.path.join(tempfile.gettempdir(), f"qr_lote_{numero_lote}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=landscape(A4))

    ancho, alto = landscape(A4)
    x_offsets = [40, ancho / 2 + 20]
    y_offsets = [alto - 180, alto - 360]
    pair_index = 0

    for i in range(cantidad):
        nro_serie += 1
        contenido = f"N° de Serie: {nro_serie}\nCódigo: {id_producto}\nDescripción: {descripcion}"
        qr = qrcode.make(contenido)

        temp_qr_path = os.path.join(tempfile.gettempdir(), f"temp_qr_{nro_serie}.png")
        qr.save(temp_qr_path)

        for col in range(2):  # dos QR por hoja
            x = x_offsets[col]
            y = y_offsets[pair_index % 2]

            # Imagen QR
            c.drawImage(temp_qr_path, x, y, width=120, height=120)

            # Texto al lado del QR
            texto = f"""Artículo: {id_producto} - {descripcion}
Número de lote: {numero_lote}
Fecha: {fecha_actual}"""

            c.setFont("Helvetica-Bold", 10)
            c.drawString(x + 130, y + 100, f"Artículo: {id_producto} - {descripcion}")
            c.setFont("Helvetica", 10)
            c.drawString(x + 130, y + 85, f"Número de lote: {numero_lote}")
            c.drawString(x + 130, y + 70, f"Fecha: {fecha_actual}")

        pair_index += 1

        # Si ya colocamos dos pares en la hoja (4 QRs), pasamos a la siguiente hoja
        if pair_index % 2 == 0:
            c.showPage()

    c.save()

    # Actualizar número de serie
    cursor.execute("UPDATE productos SET ultimo_nro_serie = %s WHERE id_producto = %s", (nro_serie, id_producto))
    conexion.commit()

    # Imprimir PDF
    if os.name == 'nt':  # Solo Windows
        os.startfile(pdf_path, "print")

    messagebox.showinfo("¡Listo!", f"Se imprimieron {cantidad} QR(s) para:\n{descripcion}")

# ---------- INTERFAZ GRÁFICA ----------
root = tk.Tk()
root.title("Generador de QR para Logística - Talca")
root.geometry("500x300")

ttk.Label(root, text="Seleccioná un producto:", font=("Arial", 12)).pack(pady=10)
productos = obtener_productos()
producto_dict = {f"{desc} (ID: {pid})": (pid, desc) for pid, desc in productos}
combo = ttk.Combobox(root, values=list(producto_dict.keys()), state="readonly", width=60)
combo.pack()

ttk.Label(root, text="Cantidad de QR a imprimir:", font=("Arial", 12)).pack(pady=10)
cantidad_entry = ttk.Entry(root)
cantidad_entry.pack()

def al_hacer_click():
    seleccion = combo.get()
    if not seleccion:
        messagebox.showwarning("Aviso", "Por favor seleccioná un producto.")
        return
    try:
        cantidad = int(cantidad_entry.get())
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Aviso", "Ingresá una cantidad válida.")
        return

    id_producto, descripcion = producto_dict[seleccion]
    generar_y_imprimir_qrs(id_producto, descripcion, cantidad)

ttk.Button(root, text="Imprimir QR", command=al_hacer_click).pack(pady=20)

root.mainloop()

# ---------- CIERRE ----------
cursor.close()
conexion.close()







