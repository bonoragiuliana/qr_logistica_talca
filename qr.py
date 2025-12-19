import mysql.connector
import qrcode
from PIL import Image
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import os
from datetime import datetime
import win32api
import win32print
from dotenv import load_dotenv
import os
# ---------- CONEXIÓN A BASE DE DATOS

load_dotenv()

conexion = mysql.connector.connect(
    host= os.getenv('MYSQL_HOST'),
    user= os.getenv('MYSQL_USER'),
    password= os.getenv('MYSQL_DATABASE'),
    database= os.getenv('MYSQL_PASSWORD')
)
cursor = conexion.cursor()

# ---------- FUNCIONES PRINCIPALES ----------

def obtener_productos():
    cursor.execute("SELECT id_producto, descripcion FROM productos")
    return cursor.fetchall()

def generar_y_imprimir_qrs(id_producto, descripcion, cantidad):
    cursor.execute("SELECT ultimo_nro_serie FROM productos WHERE id_producto = %s", (id_producto,))
    resultado = cursor.fetchone()
    if not resultado:
        messagebox.showerror("Error", "Producto no encontrado.")
        return

    nro_serie = resultado[0]
    hoy = datetime.now()
    fecha_str = hoy.strftime("%d/%m/%y")
    lote_str = hoy.strftime("%y%m%d")
    etiquetas = []

    # Cada hoja tendrá 4 QR (2 pares idénticos)
    for _ in range(cantidad):
        nro_serie += 1
        contenido = f"N° de Serie: {nro_serie}\nCódigo: {id_producto}\nDescripción: {descripcion}"
        qr_img = qrcode.make(contenido)

        etiquetas.append({
            "qr": qr_img,
            "texto": f"Artículo: {id_producto} - {descripcion}\nNúmero de lote: {lote_str}\nFecha: {fecha_str}"
        })
        etiquetas.append({  # Agregar el segundo QR idéntico
            "qr": qr_img,
            "texto": f"Artículo: {id_producto} - {descripcion}\nNúmero de lote: {lote_str}\nFecha: {fecha_str}"
        })

    # Crear PDF temporal con etiquetas
    temp_pdf = os.path.join(tempfile.gettempdir(), "etiquetas_qr.pdf")
    c = canvas.Canvas(temp_pdf, pagesize=landscape(A4))
    ancho, alto = landscape(A4)

    for i in range(0, len(etiquetas), 4):
        c.setFont("Helvetica", 10)
        posiciones = [
            (20 * mm, alto - 60 * mm),
            (150 * mm, alto - 60 * mm),
            (20 * mm, alto - 160 * mm),
            (150 * mm, alto - 160 * mm),
        ]
        for j in range(4):
            if i + j < len(etiquetas):
                x, y = posiciones[j]
                etiqueta = etiquetas[i + j]
                qr_path = os.path.join(tempfile.gettempdir(), f"temp_qr_{i+j}.png")
                etiqueta["qr"].save(qr_path)

                c.drawImage(qr_path, x, y, width=40 * mm, height=40 * mm)
                c.drawString(x + 45 * mm, y + 35 * mm, etiqueta["texto"].split("\n")[0])
                c.drawString(x + 45 * mm, y + 22 * mm, etiqueta["texto"].split("\n")[1])
                c.drawString(x + 45 * mm, y + 10 * mm, etiqueta["texto"].split("\n")[2])

        c.showPage()
    c.save()

    # Imprimir el PDF
    if os.name == 'nt':
        win32api.ShellExecute(0, "print", temp_pdf, None, ".", 0)

    # Actualizar el último número de serie en la base
    cursor.execute("UPDATE productos SET ultimo_nro_serie = %s WHERE id_producto = %s", (nro_serie, id_producto))
    conexion.commit()

    messagebox.showinfo("¡Listo!", f"Se imprimieron {cantidad} pares de QR para:\n{descripcion}")

# ---------- INTERFAZ GRÁFICA ----------

root = tk.Tk()
root.title("Generador de QR para Logística - Talca")
root.geometry("500x300")

ttk.Label(root, text="Seleccioná un producto:", font=("Arial", 12)).pack(pady=10)

productos = obtener_productos()
producto_dict = {f"{desc} (ID: {pid})": (pid, desc) for pid, desc in productos}
combo = ttk.Combobox(root, values=list(producto_dict.keys()), state="readonly", width=60)
combo.pack()

ttk.Label(root, text="Cantidad de pares de QR a imprimir:", font=("Arial", 12)).pack(pady=10)
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

# Cierre de conexión
cursor.close()
conexion.close()






