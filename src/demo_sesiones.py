# -*- coding: utf-8 -*-
"""
demo_sesiones.py
Demostracion de atencion a estudiantes de nuevo ingreso.

Simula sesiones completas y realistas de estudiantes nuevos interactuando
con el agente por sus dos vias de uso:
  (a) texto libre (clasificacion de intencion), y
  (b) navegacion por menu de opciones (respuesta directa por FAQ).
Cada sesion registra ademas la retroalimentacion del estudiante
(¿te fue util la respuesta?), alimentando las metricas del proyecto final.

Puede usarse como guion de la demostracion en vivo: cada sesion imprime
la conversacion completa tal como la veria el estudiante.

Ejecucion:
    python demo_sesiones.py
Luego ejecutar: python metricas.py  (para ver las metricas actualizadas)
"""

from chatbot_engine import ChatbotEngine

# Cada paso: ("texto", mensaje_libre)  |  ("menu", faq_id)  |  ("feedback", util)
# El feedback aplica a la ultima FAQ respondida en la sesion.
SESIONES = [
    ("est-nuevo-01", "Estudiante de primer ingreso: día de matrícula", [
        ("texto", "hola, soy nuevo, ¿dónde pago la matrícula?"),
        ("feedback", True),
        ("texto", "y cuales son las formas de pago o bancos autorizados"),
        ("feedback", True),
        ("texto", "donde queda el aula B-204"),
        ("feedback", True),
    ]),
    ("est-nuevo-02", "Estudiante nuevo: primer día de clases", [
        ("texto", "a que hora empiezan las clases en la jornada nocturna"),
        ("feedback", True),
        ("texto", "como me conecto al wifi del campus"),
        ("feedback", True),
        ("menu", "INF06"),          # ¿Dónde están las áreas de comida?
        ("feedback", True),
    ]),
    ("est-nuevo-03", "Estudiante nuevo: trámites y cuenta", [
        ("texto", "olvide mi clave del campus virtual"),
        ("feedback", True),
        ("texto", "como entro a mis clases virtuales"),
        ("feedback", True),
        ("texto", "necesito una constancia de pago"),
        ("feedback", False),        # respuesta correcta pero no lo que buscaba
        ("texto", "quiero hablar con un asesor"),
    ]),
    ("est-nuevo-04", "Estudiante nuevo: vida universitaria", [
        ("menu", "VID01"),          # deportes
        ("feedback", True),
        ("texto", "y como me uno a un voluntariado"),
        ("feedback", True),
        ("texto", "donde veo los eventos de la universidad"),
        ("feedback", True),
    ]),
    ("est-nuevo-05", "Estudiante nuevo: consulta ambigua y reformulación", [
        ("texto", "lo de la cosa esa del sistema"),      # ambigua -> no reconocida
        ("texto", "me refiero a ver mis calificaciones"),
        ("feedback", True),
        ("texto", "y como calculo mi indice academico"),
        ("feedback", True),
    ]),
    ("est-nuevo-06", "Estudiante nuevo: navegación completa por menú", [
        ("menu", "HOR07"),          # horario de biblioteca
        ("feedback", True),
        ("menu", "INF10"),          # fotocopiado
        ("feedback", True),
        ("menu", "ACA02"),          # cómo matricular
        ("feedback", True),
        ("menu", "SOP03"),          # becas
        ("feedback", False),
    ]),
]


def imprimir_bot(resultado):
    print(f"   🤖 {resultado['texto']}")
    if resultado.get("explicacion"):
        print("      Paso a paso:")
        for i, paso in enumerate(resultado["explicacion"], 1):
            print(f"        {i}. {paso}")
    if resultado.get("relacionadas"):
        sugeridas = " | ".join(r["pregunta"] for r in resultado["relacionadas"])
        print(f"      También te puede interesar: {sugeridas}")


def ejecutar_demo():
    engine = ChatbotEngine()
    print("=" * 72)
    print(" DEMOSTRACIÓN: ATENCIÓN A ESTUDIANTES DE NUEVO INGRESO")
    print(f" Base de conocimiento v{engine.version_kb()} · {engine.total_faqs()} FAQs · "
          f"{len(engine.listar_categorias())} categorías")
    print("=" * 72)

    for session_id, titulo, pasos in SESIONES:
        print(f"\n──── Sesión {session_id} · {titulo} ────")
        ultima_faq = None
        for accion, dato in pasos:
            if accion == "texto":
                print(f"   👤 {dato}")
                resultado = engine.procesar_mensaje(dato, session_id)
                imprimir_bot(resultado)
                if resultado["tipo"] == "respuesta":
                    ultima_faq = resultado["faq_id"]
            elif accion == "menu":
                faq = engine.obtener_faq(dato)
                print(f"   👤 [Selecciona en el menú] {faq['pregunta']}")
                resultado = engine.responder_faq_por_id(dato, session_id)
                imprimir_bot(resultado)
                ultima_faq = dato
            elif accion == "feedback" and ultima_faq:
                engine.registrar_feedback(session_id, ultima_faq, dato)
                print(f"   👤 [{'👍 Útil' if dato else '👎 No útil'}]")

    print("\n" + "=" * 72)
    print(" Demostración finalizada. Consultas y feedback registrados en logs/.")
    print(" Ejecuta ahora:  python metricas.py")
    print("=" * 72)


if __name__ == "__main__":
    ejecutar_demo()
