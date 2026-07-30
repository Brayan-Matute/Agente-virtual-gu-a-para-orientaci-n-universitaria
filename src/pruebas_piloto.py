# -*- coding: utf-8 -*-
"""
pruebas_piloto.py
Bateria de validacion con usuarios simulados para el motor del chatbot:
clasificacion de intencion, base de conocimiento ampliada (45 FAQs),
manejo de consultas ambiguas, derivacion por bucle de error y feedback.

Proyecto Final - Agente Virtual Guia para Orientacion Universitaria (UTH)

Ejecucion:
    python pruebas_piloto.py
Genera un reporte en consola y guarda logs en logs/auditoria_consultas.csv
"""

from chatbot_engine import ChatbotEngine

# Conjunto de consultas simuladas (casos normales de las 5 categorias +
# variaciones de redaccion + casos ambiguos + casos de transferencia).
# El "esperado" es referencial para el calculo del porcentaje de aciertos.
CASOS_DE_PRUEBA = [
    # --- Casos del Segundo Avance (regresion: no deben romperse) ---
    ("¿Dónde pago la matrícula?", "user1", "INF01"),
    ("a que hora son las clases en la jornada matutina", "user2", "HOR02"),
    ("como hago la prematricula", "user3", "ACA02"),
    ("se me olvido mi clave del campus virtual", "user4", "SOP01"),
    ("donde estan los laboratorios de computo", "user5", "INF05"),
    ("cuantas materias puedo matricular", "user6", "ACA01"),
    ("ofrecen becas en la universidad", "user7", "SOP03"),
    ("necesito hablar con un asesor", "user8", "TRANSFERENCIA"),
    ("xkjasldjk asdkj", "user9", "SIN_RESULTADO"),     # consulta sin sentido
    ("blablabla", "user9", "SIN_RESULTADO"),           # 2do intento fallido (misma sesion)
    ("no entiendo nada", "user9", "TRANSFERENCIA"),    # 3er intento -> bucle de error
    ("cual es el horario de registro", "user10", "HOR01"),
    ("donde queda la biblioteca", "user11", "INF04"),
    ("como solicito mi certificacion de notas", "user12", "ACA03"),
    # --- FAQs nuevas del Proyecto Final ---
    ("donde queda el auditorio", "user13", "INF09"),
    ("donde puedo sacar fotocopias e imprimir", "user14", "INF10"),
    ("cual es el horario de la biblioteca", "user15", "HOR07"),
    ("hasta que hora estan abiertos los laboratorios", "user16", "HOR08"),
    ("no presente el examen, como pido reposicion", "user17", "ACA10"),
    ("donde veo mis calificaciones", "user18", "ACA11"),
    ("como calculo mi indice academico", "user19", "ACA12"),
    ("como entro a mis clases virtuales por zoom", "user20", "SOP09"),
    ("necesito una constancia de pago", "user21", "SOP10"),
    ("que deportes tiene la universidad", "user22", "VID01"),
    ("como me uno a un grupo de voluntariado", "user23", "VID02"),
    ("donde veo los eventos y actividades", "user24", "VID03"),
    ("tienen bolsa de trabajo o pasantias", "user25", "VID04"),
    ("hay programas de intercambio academico", "user26", "VID05"),
    # --- Casos de desambiguacion (colisiones potenciales) ---
    ("necesito una constancia de estudios", "user27", "ACA03"),
    ("cuando son los examenes parciales", "user28", "HOR05"),
]


def ejecutar_pruebas():
    engine = ChatbotEngine()
    print("=" * 70)
    print(" PRUEBAS PILOTO CON USUARIOS SIMULADOS - PROYECTO FINAL")
    print(f" Base de conocimiento v{engine.version_kb()} | "
          f"FAQs activas: {engine.total_faqs()} | "
          f"Categorias: {len(engine.listar_categorias())}")
    print("=" * 70)

    aciertos = 0
    total = len(CASOS_DE_PRUEBA)
    fallidos = []

    for consulta, session_id, esperado in CASOS_DE_PRUEBA:
        resultado = engine.procesar_mensaje(consulta, session_id)
        faq_id = resultado.get("faq_id")
        tipo = resultado["tipo"]

        if tipo == "transferencia":
            obtenido = "TRANSFERENCIA"
        elif tipo == "sin_resultado":
            obtenido = "SIN_RESULTADO"
        else:
            obtenido = faq_id

        ok = "OK" if obtenido == esperado else "REVISAR"
        if ok == "OK":
            aciertos += 1
        else:
            fallidos.append((consulta, esperado, obtenido))

        extras = ""
        if tipo == "respuesta":
            extras = (f" | pasos: {len(resultado['explicacion'])}"
                      f" | relacionadas: {len(resultado['relacionadas'])}")

        print(f"[{ok:7}] Sesion={session_id:6} | Consulta: '{consulta}'")
        print(f"          Esperado={esperado} | Obtenido={obtenido}{extras}")
        print("-" * 70)

    porcentaje = (aciertos / total) * 100
    print("=" * 70)
    print(f" RESULTADO FINAL: {aciertos}/{total} aciertos ({porcentaje:.1f}%)")
    if fallidos:
        print(" Casos a revisar:")
        for c, e, o in fallidos:
            print(f"   - '{c}': esperado {e}, obtenido {o}")
    print(" Los logs detallados se guardaron en logs/auditoria_consultas.csv")
    print("=" * 70)
    return porcentaje


if __name__ == "__main__":
    ejecutar_pruebas()
