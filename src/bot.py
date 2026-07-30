# -*- coding: utf-8 -*-
"""
bot.py
Integracion del Agente Virtual con la API de Telegram (python-telegram-bot).
Utiliza el mismo motor (chatbot_engine.py) que la interfaz web, garantizando
una unica fuente de verdad para la base de conocimiento y la logica.

Novedades del Proyecto Final:
  - Menu de categorias DINAMICO: se construye desde la base de conocimiento
    (las categorias nuevas aparecen sin tocar el codigo del bot).
  - Boton "🧭 Paso a paso" con la respuesta explicativa de cada FAQ.
  - Preguntas relacionadas sugeridas como botones tras cada respuesta.
  - Botones de retroalimentacion 👍/👎 (alimentan la metrica de satisfaccion).

Requisitos:
    pip install python-telegram-bot==21.*

Configuracion:
    Establecer la variable de entorno TELEGRAM_BOT_TOKEN con el token
    obtenido desde @BotFather en Telegram.

Ejecucion:
    python bot.py
"""

import os
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

from chatbot_engine import ChatbotEngine

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

engine = ChatbotEngine()

EMOJIS_CATEGORIA = {
    "Infraestructura": "🏢",
    "Horarios": "🕒",
    "Procesos Academicos": "📄",
    "Soporte y Cuentas": "💬",
    "Vida Estudiantil": "🎭",
}


def menu_principal() -> InlineKeyboardMarkup:
    """Menu de categorias construido dinamicamente desde la base de
    conocimiento: una categoria nueva aparece sin modificar este modulo."""
    botones = []
    for categoria in engine.listar_categorias():
        emoji = EMOJIS_CATEGORIA.get(categoria, "📌")
        botones.append([InlineKeyboardButton(f"{emoji} {categoria}",
                                             callback_data=f"cat_{categoria}")])
    botones.append([InlineKeyboardButton("🙋 Hablar con un asesor",
                                          callback_data="transferir")])
    return InlineKeyboardMarkup(botones)


def teclado_respuesta(resultado: dict) -> InlineKeyboardMarkup | None:
    """Teclado adjunto a cada respuesta: paso a paso, feedback,
    preguntas relacionadas y regreso al menu."""
    if resultado.get("tipo") != "respuesta" or not resultado.get("faq_id"):
        return None
    faq_id = resultado["faq_id"]
    filas = []
    if resultado.get("explicacion"):
        filas.append([InlineKeyboardButton("🧭 Ver paso a paso",
                                            callback_data=f"exp|{faq_id}")])
    filas.append([
        InlineKeyboardButton("👍 Me fue útil", callback_data=f"fb|{faq_id}|1"),
        InlineKeyboardButton("👎 No me sirvió", callback_data=f"fb|{faq_id}|0"),
    ])
    for rel in resultado.get("relacionadas", [])[:3]:
        etiqueta = rel["pregunta"]
        if len(etiqueta) > 55:
            etiqueta = etiqueta[:52] + "..."
        filas.append([InlineKeyboardButton(f"➕ {etiqueta}",
                                            callback_data=f"faq_{rel['id']}")])
    filas.append([InlineKeyboardButton("⬅️ Volver al menú",
                                        callback_data="volver_menu")])
    return InlineKeyboardMarkup(filas)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu Asistente Universitario Virtual 🎓\n"
        "Puedo orientarte sobre el campus, horarios, trámites, soporte y "
        "vida estudiantil. Elige una categoría o escríbeme tu consulta.",
        reply_markup=menu_principal()
    )


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Estas son las categorías disponibles:",
                                     reply_markup=menu_principal())


async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session_id = f"tg-{update.effective_chat.id}"
    texto_usuario = update.message.text

    resultado = engine.procesar_mensaje(texto_usuario, session_id)
    teclado = teclado_respuesta(resultado) or menu_principal()
    await update.message.reply_text(resultado["texto"], reply_markup=teclado)


async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Categorias del menu principal y transferencia a asesor."""
    query = update.callback_query
    await query.answer()
    data = query.data
    session_id = f"tg-{query.message.chat_id}"

    if data == "transferir":
        resultado = engine.procesar_mensaje("hablar con un asesor", session_id)
        await query.edit_message_text(resultado["texto"])
        return

    categoria = data.replace("cat_", "")
    faqs = engine.listar_faqs_por_categoria(categoria)
    if not faqs:
        await query.edit_message_text("No encontré preguntas para esa categoría.")
        return

    botones = [
        [InlineKeyboardButton(f["pregunta"][:60], callback_data=f"faq_{f['id']}")]
        for f in faqs
    ]
    botones.append([InlineKeyboardButton("⬅️ Volver al menú",
                                          callback_data="volver_menu")])
    await query.edit_message_text(
        f"Preguntas frecuentes - {categoria}:",
        reply_markup=InlineKeyboardMarkup(botones)
    )


async def manejar_faq_directa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Seleccion de una FAQ por menu o por pregunta relacionada."""
    query = update.callback_query
    await query.answer()
    data = query.data
    session_id = f"tg-{query.message.chat_id}"

    if data == "volver_menu":
        await query.message.reply_text("Menú principal:",
                                        reply_markup=menu_principal())
        return

    faq_id = data.replace("faq_", "")
    resultado = engine.responder_faq_por_id(faq_id, session_id)
    teclado = teclado_respuesta(resultado)
    await query.message.reply_text(resultado["texto"], reply_markup=teclado)


async def manejar_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botones 👍/👎: registra la valoracion del estudiante."""
    query = update.callback_query
    _, faq_id, valor = query.data.split("|")
    session_id = f"tg-{query.message.chat_id}"
    engine.registrar_feedback(session_id, faq_id, valor == "1")
    await query.answer("¡Gracias por tu valoración! ✔", show_alert=False)


async def manejar_explicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Boton 'Ver paso a paso': envia la respuesta explicativa de la FAQ."""
    query = update.callback_query
    await query.answer()
    _, faq_id = query.data.split("|")
    faq = engine.obtener_faq(faq_id)
    if not faq or not faq.get("explicacion"):
        await query.message.reply_text("Esta respuesta no tiene explicación detallada.")
        return
    pasos = "\n".join(f"{i}. {p}" for i, p in enumerate(faq["explicacion"], 1))
    await query.message.reply_text(f"🧭 Paso a paso — {faq['pregunta']}\n\n{pasos}")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Debes establecer la variable de entorno TELEGRAM_BOT_TOKEN "
            "con el token de tu bot (obtenido desde @BotFather)."
        )

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CallbackQueryHandler(manejar_boton, pattern="^cat_|^transferir$"))
    app.add_handler(CallbackQueryHandler(manejar_feedback, pattern=r"^fb\|"))
    app.add_handler(CallbackQueryHandler(manejar_explicacion, pattern=r"^exp\|"))
    app.add_handler(CallbackQueryHandler(manejar_faq_directa, pattern="^faq_|^volver_menu$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje))

    logger.info("Bot de Telegram (Proyecto Final) iniciado. Esperando mensajes...")
    app.run_polling()


if __name__ == "__main__":
    main()
