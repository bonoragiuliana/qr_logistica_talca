import mysql.connector
import qrcode
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile
from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# ---------- CONEXIÓN A BASE DE DATOS ----------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="talca2025",
    database="productos_db"
)
cursor = conexion.cursor()

# ---------- FUNCIONES ----------

def obtener_productos():
    cursor.execute("SELECT id_producto, descripcion FROM productos")
    return cursor.fetchall()


def generar_pdf_e_imprimir(id_producto, descripcion, cantidad):
    cursor.execute(
        "SELECT ultimo_nro_serie FROM productos WHERE id_producto = %s",
        (id_producto,)
    )
    ultimo = cursor.fetchone()[0]

    pdf_path = os.path.join(
        tempfile.gettempdir(),
        f"QR_{id_producto}.pdf"
    )

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elementos = []

    nro_serie = ultimo

    for _ in range(cantidad):
        nro_serie += 1

        texto_qr = (
            f"N° de Serie: {nro_serie}\n"
            f"Código: {id_producto}\n"
            f"Descripción: {descripcion}"
        )

        # Crear QR
        qr_img = qrcode.make(texto_qr)
        qr_temp = os.path.join(
            tempfile.gettempdir(),
            f"qr_{id_producto}_{nro_serie}.png"
        )
        qr_img.save(qr_temp)

        # QR superior
        elementos.append(RLImage(qr_temp, width=6*cm, height=6*cm))
        elementos.append(Spacer(1, 6*cm))

        # QR inferior (idéntico)
        elementos.append(RLImage(qr_temp, width=6*cm, height=6*cm))
        elementos.append(Spacer(1, 1*cm))

    # Construir PDF
    doc.build(elementos)

    # Actualizar serie en BD
    cursor.execute(
        "UPDATE productos SET ultimo_nro_serie = %s WHERE id_producto = %s",
        (nro_serie, id_producto)
    )
    conexion.commit()

    # Imprimir TODO el PDF junto
    if os.name == "nt":
        os.startfile(pdf_path, "print")

    messagebox.showinfo(
        "Impresión completa",
        f"Se imprimieron {cantidad} hojas\nProducto: {descripcion}"
    )

# ---------- INTERFAZ ----------

root = tk.Tk()
root.title("Generador de QR – Logística Talca")
root.geometry("520x320")

ttk.Label(root, text="Producto", font=("Arial", 12)).pack(pady=8)

productos = obtener_productos()
producto_dict = {
    f"{desc} (ID: {pid})": (pid, desc)
    for pid, desc in productos
}

combo = ttk.Combobox(
    root,
    values=list(producto_dict.keys()),
    state="readonly",
    width=65
)
combo.pack()

ttk.Label(root, text="Cantidad de QR", font=("Arial", 12)).pack(pady=10)
cantidad_entry = ttk.Entry(root, width=10)
cantidad_entry.pack()

def imprimir():
    if not combo.get():
        messagebox.showwarning("Error", "Seleccioná un producto")
        return

    try:
        cantidad = int(cantidad_entry.get())
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Error", "Cantidad inválida")
        return

    id_producto, descripcion = producto_dict[combo.get()]
    generar_pdf_e_imprimir(id_producto, descripcion, cantidad)

ttk.Button(
    root,
    text="IMPRIMIR",
    command=imprimir,
    width=20
).pack(pady=25)

root.mainloop()

cursor.close()
conexion.close()




