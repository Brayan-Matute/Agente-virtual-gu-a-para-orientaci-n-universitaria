# -*- coding: utf-8 -*-
"""
metricas.py
Modulo de metricas de desempeño del Agente Virtual.

Lee los registros de auditoria (logs/auditoria_consultas.csv) y de
retroalimentacion (logs/feedback_respuestas.csv) y calcula:

  - Porcentaje de consultas resueltas automaticamente (metrica principal
    del Proyecto Final).
  - Distribucion de resultados: respondidas por texto libre, respondidas
    por menu, no reconocidas, transferencias explicitas y por bucle.
  - Consultas respondidas por categoria de la base de conocimiento.
  - Porcentaje de exactitud de la bateria de pruebas piloto (si se corre
    pruebas_piloto.py antes, sus casos quedan en el mismo log).
  - Satisfaccion del estudiante: % de respuestas marcadas como utiles.

Genera:
  - Reporte en consola y en docs/reporte_metricas.txt
  - Graficas PNG en docs/img_metricas/ (para el informe final)

Ejecucion:
    python metricas.py
"""

import csv
import os
from collections import Counter
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs", "auditoria_consultas.csv")
FEEDBACK_PATH = os.path.join(BASE_DIR, "logs", "feedback_respuestas.csv")
DOCS_DIR = os.path.join(BASE_DIR, "docs")
IMG_DIR = os.path.join(DOCS_DIR, "img_metricas")

AZUL = "#163d6b"
AZUL_CLARO = "#2e75b6"
GRIS = "#8a8f98"
VERDE = "#2e8b57"
ROJO = "#c0504d"
NARANJA = "#e08a2e"


def leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def calcular_metricas():
    filas = leer_csv(LOG_PATH)
    feedback = leer_csv(FEEDBACK_PATH)

    resultados = Counter(r["resultado"] for r in filas)
    respondidas_texto = resultados.get("respondida", 0)
    respondidas_menu = resultados.get("respondida_menu", 0)
    sin_resultado = resultados.get("sin_resultado", 0)
    transf_explicita = resultados.get("transferencia_explicita", 0)
    transf_bucle = resultados.get("transferencia_bucle", 0)

    respondidas = respondidas_texto + respondidas_menu
    total = len(filas)

    # Consultas "de contenido": todas menos las transferencias explicitas
    # (pedir un asesor no es un fallo del agente, es una funcion prevista).
    contenido = respondidas + sin_resultado + transf_bucle
    tasa_resolucion = (respondidas / contenido * 100) if contenido else 0.0
    tasa_derivacion_total = ((transf_explicita + transf_bucle) / total * 100) if total else 0.0

    por_categoria = Counter(
        r["categoria"] for r in filas
        if r["resultado"] in ("respondida", "respondida_menu") and r["categoria"] != "N/A"
    )

    total_fb = len(feedback)
    utiles = sum(1 for r in feedback if r["util"] == "1")
    tasa_util = (utiles / total_fb * 100) if total_fb else 0.0

    return {
        "total": total,
        "respondidas": respondidas,
        "respondidas_texto": respondidas_texto,
        "respondidas_menu": respondidas_menu,
        "sin_resultado": sin_resultado,
        "transf_explicita": transf_explicita,
        "transf_bucle": transf_bucle,
        "contenido": contenido,
        "tasa_resolucion": tasa_resolucion,
        "tasa_derivacion_total": tasa_derivacion_total,
        "por_categoria": dict(por_categoria),
        "total_feedback": total_fb,
        "feedback_utiles": utiles,
        "feedback_no_utiles": total_fb - utiles,
        "tasa_util": tasa_util,
    }


def generar_graficas(m):
    """Genera las graficas PNG para el informe final (requiere matplotlib)."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("[Aviso] matplotlib no esta instalado; se omiten las graficas.")
        return []

    os.makedirs(IMG_DIR, exist_ok=True)
    generadas = []

    # ---- 1. Distribucion de resultados -------------------------------- #
    etiquetas = ["Respondidas\n(texto libre)", "Respondidas\n(menú)",
                 "No\nreconocidas", "Transferencia\nexplícita",
                 "Transferencia\npor bucle"]
    valores = [m["respondidas_texto"], m["respondidas_menu"],
               m["sin_resultado"], m["transf_explicita"], m["transf_bucle"]]
    colores = [AZUL, AZUL_CLARO, NARANJA, GRIS, ROJO]

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=150)
    barras = ax.bar(etiquetas, valores, color=colores)
    ax.bar_label(barras, padding=2, fontsize=9, fontweight="bold")
    ax.set_title("Distribución de resultados de las consultas", fontsize=12,
                 fontweight="bold", color=AZUL)
    ax.set_ylabel("Consultas")
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8.5)
    fig.tight_layout()
    ruta = os.path.join(IMG_DIR, "distribucion_resultados.png")
    fig.savefig(ruta)
    plt.close(fig)
    generadas.append(ruta)

    # ---- 2. Consultas respondidas por categoria ----------------------- #
    if m["por_categoria"]:
        cats = sorted(m["por_categoria"].items(), key=lambda x: x[1])
        nombres = [c for c, _ in cats]
        vals = [v for _, v in cats]
        fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=150)
        barras = ax.barh(nombres, vals, color=AZUL_CLARO)
        ax.bar_label(barras, padding=3, fontsize=9, fontweight="bold")
        ax.set_title("Consultas respondidas por categoría", fontsize=12,
                     fontweight="bold", color=AZUL)
        ax.set_xlabel("Consultas resueltas")
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        ruta = os.path.join(IMG_DIR, "consultas_por_categoria.png")
        fig.savefig(ruta)
        plt.close(fig)
        generadas.append(ruta)

    # ---- 3. Tasa de resolucion + satisfaccion ------------------------- #
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), dpi=150)

    ax = axes[0]
    ax.pie([m["respondidas"], m["contenido"] - m["respondidas"]],
           labels=["Resueltas", "No resueltas"],
           colors=[AZUL, NARANJA], autopct="%1.1f%%",
           startangle=90, textprops={"fontsize": 9},
           wedgeprops={"width": 0.42})
    ax.set_title(f"Tasa de resolución automática\n({m['respondidas']}/{m['contenido']} consultas)",
                 fontsize=10.5, fontweight="bold", color=AZUL)

    ax = axes[1]
    if m["total_feedback"]:
        ax.pie([m["feedback_utiles"], m["feedback_no_utiles"]],
               labels=["Útil", "No útil"],
               colors=[VERDE, ROJO], autopct="%1.1f%%",
               startangle=90, textprops={"fontsize": 9},
               wedgeprops={"width": 0.42})
        ax.set_title(f"Satisfacción del estudiante\n({m['total_feedback']} valoraciones)",
                     fontsize=10.5, fontweight="bold", color=AZUL)
    else:
        ax.axis("off")
        ax.text(0.5, 0.5, "Sin feedback registrado", ha="center", va="center")
    fig.tight_layout()
    ruta = os.path.join(IMG_DIR, "resolucion_y_satisfaccion.png")
    fig.savefig(ruta)
    plt.close(fig)
    generadas.append(ruta)

    return generadas


def formatear_reporte(m):
    lineas = []
    a = lineas.append
    a("=" * 66)
    a(" MÉTRICAS DE DESEMPEÑO - AGENTE VIRTUAL DE ORIENTACIÓN (UTH)")
    a(f" Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    a("=" * 66)
    a(f" Total de consultas registradas:            {m['total']}")
    a(f"   · Respondidas por texto libre:           {m['respondidas_texto']}")
    a(f"   · Respondidas por navegación de menú:    {m['respondidas_menu']}")
    a(f"   · No reconocidas (reformulación pedida): {m['sin_resultado']}")
    a(f"   · Transferencias explícitas (asesor):    {m['transf_explicita']}")
    a(f"   · Transferencias por bucle de error:     {m['transf_bucle']}")
    a("-" * 66)
    a(f" >> TASA DE RESOLUCIÓN AUTOMÁTICA: {m['tasa_resolucion']:.1f}%"
      f"  ({m['respondidas']}/{m['contenido']} consultas de contenido)")
    a(f" >> Tasa de derivación a humano:   {m['tasa_derivacion_total']:.1f}%"
      f"  (explícitas + bucle, sobre el total)")
    a("-" * 66)
    a(" Consultas resueltas por categoría:")
    for cat, n in sorted(m["por_categoria"].items(), key=lambda x: -x[1]):
        a(f"   · {cat:<22} {n}")
    a("-" * 66)
    if m["total_feedback"]:
        a(f" Retroalimentación del estudiante ({m['total_feedback']} valoraciones):")
        a(f"   · Útiles:    {m['feedback_utiles']}  |  No útiles: {m['feedback_no_utiles']}")
        a(f" >> ÍNDICE DE SATISFACCIÓN: {m['tasa_util']:.1f}%")
    else:
        a(" Sin retroalimentación registrada todavía.")
    a("=" * 66)
    return "\n".join(lineas)


def main():
    m = calcular_metricas()
    reporte = formatear_reporte(m)
    print(reporte)

    os.makedirs(DOCS_DIR, exist_ok=True)
    ruta_txt = os.path.join(DOCS_DIR, "reporte_metricas.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(reporte + "\n")
    print(f"\nReporte guardado en: {ruta_txt}")

    generadas = generar_graficas(m)
    for g in generadas:
        print(f"Gráfica generada:   {g}")


if __name__ == "__main__":
    main()
