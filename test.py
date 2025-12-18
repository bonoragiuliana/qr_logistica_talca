import mysql.connector

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="talca2025",
    database="productos_db",
    auth_plugin="mysql_native_password"
)

print("✅ Conexión OK")
conexion.close()
