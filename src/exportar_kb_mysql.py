# -*- coding: utf-8 -*-
"""
exportar_kb_mysql.py
Sincronizacion de la base de conocimiento con el canal n8n + MySQL.

El flujo de n8n del segundo avance lee las FAQs desde la tabla MySQL
`knowledge_base` (columnas: id, categoria, palabras_clave, pregunta,
respuesta; `palabras_clave` se guarda como arreglo JSON en texto).

Este script genera `data/knowledge_base_mysql.sql` a partir de
`data/knowledge_base.json`, de modo que al editar o ampliar las FAQs
solo haya que volver a ejecutar:

    python exportar_kb_mysql.py
    (y luego importar el .sql en MySQL / phpMyAdmin / HeidiSQL)

Asi las tres vias de acceso (web local, Telegram y n8n) responden
siempre con la misma base de conocimiento.
"""

import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")
SQL_PATH = os.path.join(BASE_DIR, "data", "knowledge_base_mysql.sql")


def esc(texto: str) -> str:
    """Escapa comillas simples para SQL."""
    return texto.replace("\\", "\\\\").replace("'", "''")


def main():
    with open(KB_PATH, encoding="utf-8") as f:
        kb = json.load(f)

    faqs = kb["faqs"]
    version = kb.get("metadata", {}).get("version", "N/D")

    lineas = [
        "-- ------------------------------------------------------------",
        "-- Base de conocimiento del Agente Virtual UTH (canal n8n/MySQL)",
        f"-- Generado desde data/knowledge_base.json v{version} "
        f"({len(faqs)} FAQs)",
        "-- Importar con: mysql -u usuario -p base_de_datos < knowledge_base_mysql.sql",
        "-- ------------------------------------------------------------",
        "",
        "CREATE TABLE IF NOT EXISTS knowledge_base (",
        "  id VARCHAR(10) PRIMARY KEY,",
        "  categoria VARCHAR(60) NOT NULL,",
        "  palabras_clave TEXT NOT NULL,   -- arreglo JSON en texto",
        "  pregunta TEXT NOT NULL,",
        "  respuesta TEXT NOT NULL",
        ") CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "",
        "CREATE TABLE IF NOT EXISTS sesiones (",
        "  session_id VARCHAR(80) PRIMARY KEY,",
        "  fallos_consecutivos INT NOT NULL DEFAULT 0",
        ") CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "",
        "CREATE TABLE IF NOT EXISTS auditoria_consultas (",
        "  id INT AUTO_INCREMENT PRIMARY KEY,",
        "  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "  session_id VARCHAR(80),",
        "  canal VARCHAR(20),",
        "  consulta_original TEXT,",
        "  tokens_detectados TEXT,",
        "  faq_id_asignada VARCHAR(10),",
        "  categoria VARCHAR(60),",
        "  puntaje INT,",
        "  resultado VARCHAR(40),",
        "  intentos_fallidos_sesion INT",
        ") CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "",
        "-- Se reemplaza el contenido completo para mantener la tabla",
        "-- identica a knowledge_base.json (unica fuente de verdad).",
        "TRUNCATE TABLE knowledge_base;",
        "",
    ]

    for faq in faqs:
        palabras = json.dumps(faq["palabras_clave"], ensure_ascii=False)
        lineas.append(
            "INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES\n"
            f"  ('{esc(faq['id'])}', '{esc(faq['categoria'])}', "
            f"'{esc(palabras)}',\n   '{esc(faq['pregunta'])}',\n   '{esc(faq['respuesta'])}');"
        )

    with open(SQL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")

    print(f"Archivo SQL generado: {SQL_PATH}")
    print(f"FAQs exportadas: {len(faqs)} (v{version})")


if __name__ == "__main__":
    main()
