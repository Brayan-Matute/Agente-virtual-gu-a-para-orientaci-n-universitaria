# -*- coding: utf-8 -*-
"""
chatbot_engine.py
Motor principal del Agente Virtual de Orientacion Universitaria (UTH).

Implementa:
  - Carga de la base de conocimiento (knowledge_base.json)
  - Clasificacion de intencion por palabras clave (motor de inferencia
    determinista / sistema experto basado en reglas)
  - Respuestas explicativas (paso a paso) y preguntas relacionadas
  - Respuesta directa por navegacion de menu (responder_faq_por_id)
  - Conteo de intentos fallidos consecutivos -> derivacion por "bucle de error"
  - Deteccion de peticion explicita de transferencia a humano
  - Registro de auditoria (logs) de cada consulta realizada
  - Registro de retroalimentacion del usuario (¿te fue util la respuesta?)

Proyecto Final - Agente Virtual Guia para Orientacion Universitaria (UTH)
"""

import json
import os
import csv
from datetime import datetime

from nlp_utils import tokenizar, calcular_puntaje, es_comando_transferencia

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")
LOG_PATH = os.path.join(BASE_DIR, "logs", "auditoria_consultas.csv")
FEEDBACK_PATH = os.path.join(BASE_DIR, "logs", "feedback_respuestas.csv")

UMBRAL_MINIMO = 3          # puntaje minimo para considerar una respuesta valida
INTENTOS_MAX_FALLO = 3     # bucle de error: 3 intentos fallidos consecutivos

MENSAJE_TRANSFERENCIA = (
    "Te comunico con un agente humano. Canales de atencion presencial: "
    "Edificio Principal, Oficina de Registro. Horario: Lun-Vie 8:00 AM - "
    "7:00 PM, Sab 8:00 AM - 12:00 PM. Correo: soporte@universidad.edu"
)

MENSAJE_BUCLE = (
    "No logre identificar tu consulta tras varios intentos. Te transfiero "
    "con un agente humano. Correo: soporte@universidad.edu | Oficina de "
    "Registro, Lun-Vie 8:00 AM - 7:00 PM."
)

MENSAJE_SIN_RESULTADO = (
    "No logre entender tu consulta. ¿Podrias reformularla? Tambien puedes "
    "escribir 'menu' para ver las categorias disponibles, o 'asesor' para "
    "hablar con una persona."
)


class ChatbotEngine:
    def __init__(self, kb_path: str = KB_PATH, log_path: str = LOG_PATH,
                 feedback_path: str = FEEDBACK_PATH):
        self.kb_path = kb_path
        self.log_path = log_path
        self.feedback_path = feedback_path
        self.faqs = self._cargar_base_conocimiento()
        self.faqs_por_id = {f["id"]: f for f in self.faqs}
        self._asegurar_log()
        self._asegurar_feedback()
        # Contador de intentos fallidos consecutivos, por sesion
        self.fallos_consecutivos = {}

    # ------------------------------------------------------------------ #
    # Carga de datos
    # ------------------------------------------------------------------ #
    def _cargar_base_conocimiento(self) -> list:
        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.metadata = data.get("metadata", {})
        return data.get("faqs", [])

    def _asegurar_log(self):
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "session_id", "consulta_original",
                    "tokens_detectados", "faq_id_asignada", "categoria",
                    "puntaje", "resultado", "intentos_fallidos_sesion"
                ])

    def _asegurar_feedback(self):
        os.makedirs(os.path.dirname(self.feedback_path), exist_ok=True)
        if not os.path.exists(self.feedback_path):
            with open(self.feedback_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "session_id", "faq_id", "categoria", "util"
                ])

    def _registrar_log(self, session_id, consulta, tokens, faq_id,
                        categoria, puntaje, resultado, fallos):
        with open(self.log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                session_id,
                consulta,
                " ".join(tokens),
                faq_id or "N/A",
                categoria or "N/A",
                puntaje,
                resultado,
                fallos
            ])

    # ------------------------------------------------------------------ #
    # Clasificacion de intencion (sistema experto basado en reglas)
    # ------------------------------------------------------------------ #
    def _buscar_mejor_faq(self, tokens: list):
        mejor_faq = None
        mejor_puntaje = 0
        for faq in self.faqs:
            puntaje = calcular_puntaje(tokens, faq["palabras_clave"])
            if puntaje > mejor_puntaje:
                mejor_puntaje = puntaje
                mejor_faq = faq
        return mejor_faq, mejor_puntaje

    def _empaquetar_respuesta(self, faq: dict) -> dict:
        """Construye la respuesta enriquecida: texto + explicacion + relacionadas."""
        relacionadas = []
        for rid in faq.get("relacionadas", []):
            rel = self.faqs_por_id.get(rid)
            if rel:
                relacionadas.append({"id": rel["id"], "pregunta": rel["pregunta"]})
        return {
            "tipo": "respuesta",
            "texto": faq["respuesta"],
            "faq_id": faq["id"],
            "categoria": faq["categoria"],
            "pregunta": faq["pregunta"],
            "explicacion": faq.get("explicacion", []),
            "relacionadas": relacionadas
        }

    # ------------------------------------------------------------------ #
    # API publica
    # ------------------------------------------------------------------ #
    def procesar_mensaje(self, mensaje: str, session_id: str = "default") -> dict:
        """
        Procesa un mensaje de texto libre y devuelve un diccionario con:
          - tipo: 'respuesta' | 'transferencia' | 'sin_resultado'
          - texto: respuesta a mostrar
          - faq_id, categoria, pregunta (si aplica)
          - explicacion: lista de pasos (respuesta explicativa)
          - relacionadas: [{id, pregunta}] preguntas sugeridas
        """
        self.fallos_consecutivos.setdefault(session_id, 0)

        # 1. Peticion explicita de transferencia
        if es_comando_transferencia(mensaje):
            self.fallos_consecutivos[session_id] = 0
            self._registrar_log(session_id, mensaje, tokenizar(mensaje),
                                 None, None, 0, "transferencia_explicita", 0)
            return {
                "tipo": "transferencia",
                "texto": MENSAJE_TRANSFERENCIA,
                "faq_id": None,
                "categoria": None,
                "explicacion": [],
                "relacionadas": []
            }

        # 2. Clasificacion por palabras clave
        tokens = tokenizar(mensaje)
        faq, puntaje = self._buscar_mejor_faq(tokens)

        if faq and puntaje >= UMBRAL_MINIMO:
            self.fallos_consecutivos[session_id] = 0
            self._registrar_log(session_id, mensaje, tokens, faq["id"],
                                 faq["categoria"], puntaje, "respondida", 0)
            return self._empaquetar_respuesta(faq)

        # 3. No se encontro una intencion valida -> contar fallo
        self.fallos_consecutivos[session_id] += 1
        fallos = self.fallos_consecutivos[session_id]

        if fallos >= INTENTOS_MAX_FALLO:
            # Bucle de error: se registra explicitamente como derivacion
            self.fallos_consecutivos[session_id] = 0
            self._registrar_log(session_id, mensaje, tokens, None, None,
                                 puntaje, "transferencia_bucle", fallos)
            return {
                "tipo": "transferencia",
                "texto": MENSAJE_BUCLE,
                "faq_id": None,
                "categoria": None,
                "explicacion": [],
                "relacionadas": []
            }

        self._registrar_log(session_id, mensaje, tokens, None, None,
                             puntaje, "sin_resultado", fallos)
        return {
            "tipo": "sin_resultado",
            "texto": MENSAJE_SIN_RESULTADO,
            "faq_id": None,
            "categoria": None,
            "explicacion": [],
            "relacionadas": []
        }

    def responder_faq_por_id(self, faq_id: str, session_id: str = "default") -> dict:
        """
        Responde una FAQ seleccionada por navegacion de menu (botones).
        Se registra en auditoria como 'respondida_menu' para diferenciar
        el canal de resolucion en las metricas.
        """
        faq = self.faqs_por_id.get(faq_id)
        if not faq:
            return {
                "tipo": "sin_resultado",
                "texto": "No pude encontrar esa pregunta en la base de conocimiento.",
                "faq_id": None, "categoria": None,
                "explicacion": [], "relacionadas": []
            }
        self.fallos_consecutivos[session_id] = 0
        self._registrar_log(session_id, f"[MENU] {faq['pregunta']}",
                             tokenizar(faq["pregunta"]), faq["id"],
                             faq["categoria"], 0, "respondida_menu", 0)
        return self._empaquetar_respuesta(faq)

    def registrar_feedback(self, session_id: str, faq_id: str, util: bool) -> bool:
        """
        Registra la retroalimentacion del estudiante sobre una respuesta
        (util / no util). Alimenta la metrica de satisfaccion.
        """
        faq = self.faqs_por_id.get(faq_id)
        if not faq:
            return False
        with open(self.feedback_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(timespec="seconds"),
                session_id, faq_id, faq["categoria"], 1 if util else 0
            ])
        return True

    # ------------------------------------------------------------------ #
    # Utilidades de navegacion / consulta
    # ------------------------------------------------------------------ #
    def obtener_faq(self, faq_id: str):
        return self.faqs_por_id.get(faq_id)

    def listar_categorias(self) -> list:
        categorias = []
        for faq in self.faqs:
            if faq["categoria"] not in categorias:
                categorias.append(faq["categoria"])
        return categorias

    def listar_faqs_por_categoria(self, categoria: str) -> list:
        return [f for f in self.faqs if f["categoria"].lower() == categoria.lower()]

    def listar_menu(self) -> dict:
        """Menu dinamico {categoria: [{id, pregunta}, ...]} construido desde
        la base de conocimiento (unica fuente de verdad)."""
        menu = {}
        for faq in self.faqs:
            menu.setdefault(faq["categoria"], []).append(
                {"id": faq["id"], "pregunta": faq["pregunta"]}
            )
        return menu

    def total_faqs(self) -> int:
        return len(self.faqs)

    def version_kb(self) -> str:
        return self.metadata.get("version", "N/D")
