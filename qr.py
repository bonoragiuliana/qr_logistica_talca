import mysql.connector
import qrcode
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox
import os
import tempfile

# ---------- CONEXIÓN A BASE DE DATOS ----------
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="talca2025",
    database="productos_db",
    #auth_plugin="mysql_native_password"
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
    for _ in range(cantidad):
        nro_serie += 1
        contenido = f"N° de Serie: {nro_serie}\nCódigo: {id_producto}\nDescripción: {descripcion}"
        qr_img = qrcode.make(contenido)

        # Guardar temporal
        qr_path = os.path.join(tempfile.gettempdir(), f"qr_{id_producto}_{nro_serie}.png")
        qr_img.save(qr_path)

        # Imprimir (solo en Windows)
        if os.name == 'nt':
            os.startfile(qr_path, "print")

    # Actualizar número de serie
    cursor.execute("UPDATE productos SET ultimo_nro_serie = %s WHERE id_producto = %s", (nro_serie, id_producto))
    conexion.commit()

    messagebox.showinfo("¡Listo!", f"Se imprimieron {cantidad} QR(s) para:\n{descripcion}")

# ---------- INTERFAZ GRÁFICA ----------

root = tk.Tk()
root.title("Generador de QR para Logística - Talca")
root.geometry("500x300")

# Etiqueta
ttk.Label(root, text="Seleccioná un producto:", font=("Arial", 12)).pack(pady=10)

# Desplegable
productos = obtener_productos()
producto_dict = {f"{desc} (ID: {pid})": (pid, desc) for pid, desc in productos}
combo = ttk.Combobox(root, values=list(producto_dict.keys()), state="readonly", width=60)
combo.pack()

# Campo de cantidad
ttk.Label(root, text="Cantidad de QR a imprimir:", font=("Arial", 12)).pack(pady=10)
cantidad_entry = ttk.Entry(root)
cantidad_entry.pack()

# Botón
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

# Ejecutar
root.mainloop()

# Cierre de conexión
cursor.close()
conexion.close()



