import os
import mysql.connector

# 🔧 Configura tu conexión
config = {
    "database": "suimco",
    "username": "python",
    "password": "P@ssw0rd",
    "host": "localhost",
    "collation": "utf8mb4_unicode_ci"
} 

output_file = "./database/db_structure.md"

def export_structure():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# Database Structure: {config['database']}\n\n")

        for table in tables:
            f.write(f"## Tabla: {table}\n")
            cursor.execute(f"SHOW COLUMNS FROM {table};")
            columns = cursor.fetchall()

            f.write("| Columna | Tipo | Nulo | Clave | Valor por defecto | Extra |\n")
            f.write("|----------|------|------|-------|------------------|--------|\n")

            for col in columns:
                f.write(f"| {col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]} |\n")

            f.write("\n")

            cursor.execute(f"""
                SELECT
                    COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = '{config['database']}' AND TABLE_NAME = '{table}'
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """)
            fks = cursor.fetchall()

            if fks:
                f.write("### Relaciones:\n")
                for fk in fks:
                    f.write(f"- {fk[0]} → {fk[1]}.{fk[2]}\n")
                f.write("\n")

    cursor.close()
    conn.close()
    print(f"✅ Estructura exportada a {output_file}")

if __name__ == "__main__":
    export_structure()
