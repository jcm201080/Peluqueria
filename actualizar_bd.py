import sqlite3
import os

# Dependiendo de tu versión de Flask, la BD puede estar en la raíz o en la carpeta /instance
db_path = 'peluqueria.db'
if not os.path.exists(db_path):
    db_path = 'instance/peluqueria.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Inyectamos la nueva columna con un valor por defecto de 1
    cursor.execute("ALTER TABLE peluquero ADD COLUMN prioridad INTEGER DEFAULT 1;")
    conn.commit()
    
    print("✅ ÉXITO: Columna 'prioridad' añadida correctamente. No se ha borrado ninguna cita.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("⚠️ INFO: La columna 'prioridad' ya existía en la base de datos.")
    else:
        print(f"❌ ERROR de SQLite: {e}")
finally:
    conn.close()