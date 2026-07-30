# -*- coding: utf-8 -*-
"""
app_web.py
Interfaz web (widget de chat) del Agente Virtual de Orientacion
Universitaria - version del Proyecto Final.

Novedades de esta version:
  - Menu de navegacion DINAMICO: categorias y preguntas se construyen
    desde la base de conocimiento (una sola fuente de verdad).
  - Respuestas explicativas: boton "Ver paso a paso" con la explicacion
    detallada de cada respuesta.
  - Preguntas relacionadas sugeridas despues de cada respuesta.
  - Retroalimentacion del estudiante (¿Te fue util? Si/No), registrada
    para la metrica de satisfaccion.
  - Panel de metricas en vivo: http://127.0.0.1:5000/metricas
  - Backend local por defecto (sin dependencias externas). El modo n8n
    del segundo avance se conserva como opcion (USAR_N8N).

Ejecucion:
    python app_web.py
Luego abrir en el navegador: http://127.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template_string

from chatbot_engine import ChatbotEngine
from metricas import calcular_metricas

app = Flask(__name__)
app.json.sort_keys = False   # conservar el orden de categorias del menu
engine = ChatbotEngine()

PAGINA_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Asistente Universitario Virtual - UTH</title>
<style>
  :root {
    --azul: #163d6b;
    --azul-claro: #2e75b6;
    --gris-fondo: #f2f4f7;
    --burbuja-bot: #eef3f9;
    --burbuja-user: #2e75b6;
    --verde: #2e8b57;
    --rojo: #c0504d;
  }
  * { box-sizing: border-box; }
  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: var(--gris-fondo);
    margin: 0;
    display: flex;
    justify-content: center;
    padding: 30px 12px;
  }
  .chat-container {
    width: 100%;
    max-width: 520px;
    background: #fff;
    border-radius: 14px;
    box-shadow: 0 6px 24px rgba(0,0,0,0.12);
    display: flex;
    flex-direction: column;
    height: 680px;
    overflow: hidden;
  }
  .chat-header {
    background: var(--azul);
    color: #fff;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .chat-header .avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: var(--azul-claro);
    display: flex; align-items: center; justify-content: center;
    font-weight: bold;
  }
  .chat-header .info b { display: block; font-size: 15px; }
  .chat-header .info span { font-size: 12px; opacity: 0.85; }
  .chat-header a.metricas {
    margin-left: auto;
    color: #fff; opacity: .85;
    font-size: 12px; text-decoration: none;
    border: 1px solid rgba(255,255,255,.5);
    border-radius: 12px; padding: 4px 10px;
  }
  .chat-header a.metricas:hover { opacity: 1; background: var(--azul-claro); }
  .chat-messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .msg {
    max-width: 84%;
    padding: 10px 14px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.45;
    white-space: pre-wrap;
  }
  .msg.bot {
    background: var(--burbuja-bot);
    color: #1a1a1a;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }
  .msg.user {
    background: var(--burbuja-user);
    color: #fff;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }
  .acciones {
    align-self: flex-start;
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    max-width: 90%;
  }
  .acciones button {
    background: #fff;
    border: 1px solid var(--azul-claro);
    color: var(--azul-claro);
    border-radius: 14px;
    padding: 5px 11px;
    font-size: 12px;
    cursor: pointer;
  }
  .acciones button:hover { background: var(--azul-claro); color: #fff; }
  .acciones button.fb-si { border-color: var(--verde); color: var(--verde); }
  .acciones button.fb-si:hover { background: var(--verde); color: #fff; }
  .acciones button.fb-no { border-color: var(--rojo); color: var(--rojo); }
  .acciones button.fb-no:hover { background: var(--rojo); color: #fff; }
  .pasos {
    align-self: flex-start;
    background: #fff;
    border: 1px solid #dfe6ee;
    border-left: 4px solid var(--azul-claro);
    border-radius: 10px;
    padding: 10px 14px 10px 10px;
    font-size: 13px;
    max-width: 84%;
  }
  .pasos ol { margin: 4px 0 2px 18px; padding: 0; }
  .pasos li { margin-bottom: 4px; }
  .etiqueta {
    align-self: flex-start;
    font-size: 11.5px;
    color: #5a6270;
    margin: 2px 0 -4px 4px;
  }
  .quick-replies {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 0 16px 10px 16px;
    max-height: 170px;
    overflow-y: auto;
  }
  .quick-replies button {
    background: #fff;
    border: 1px solid var(--azul-claro);
    color: var(--azul-claro);
    border-radius: 16px;
    padding: 6px 12px;
    font-size: 12.5px;
    cursor: pointer;
    text-align: left;
    max-width: 100%;
  }
  .quick-replies button:hover { background: var(--azul-claro); color: #fff; }
  .chat-input {
    display: flex;
    border-top: 1px solid #e3e6ea;
    padding: 10px;
    gap: 8px;
  }
  .chat-input input {
    flex: 1;
    border: 1px solid #d7dbe0;
    border-radius: 20px;
    padding: 10px 16px;
    font-size: 14px;
    outline: none;
  }
  .chat-input button {
    background: var(--azul-claro);
    color: #fff;
    border: none;
    border-radius: 20px;
    padding: 0 18px;
    font-size: 14px;
    cursor: pointer;
  }
  .chat-input button:hover { background: var(--azul); }
  .footer-note {
    text-align: center;
    font-size: 11px;
    color: #8a8f98;
    margin-top: 10px;
  }
</style>
</head>
<body>

<div>
  <div class="chat-container">
    <div class="chat-header">
      <div class="avatar">UV</div>
      <div class="info">
        <b>Asistente Universitario Virtual</b>
        <span>Orientación para estudiantes - UTH</span>
      </div>
      <a class="metricas" href="/metricas" target="_blank">📊 Métricas</a>
    </div>
    <div class="chat-messages" id="chatMessages"></div>
    <div class="quick-replies" id="quickReplies"></div>
    <div class="chat-input">
      <input type="text" id="userInput" placeholder="Escribe tu consulta..." autocomplete="off">
      <button onclick="enviarMensaje()">Enviar</button>
    </div>
  </div>
  <div class="footer-note">Proyecto Final | Sesión: <span id="sessionLabel"></span></div>
</div>

<script>
// ============================================================
// BACKEND: por defecto se usa el motor LOCAL (/api/chat), sin
// dependencias externas — recomendado para la demostración en vivo.
// El modo n8n del segundo avance se conserva: poner USAR_N8N = true
// y actualizar la URL del túnel ngrok cuando se reinicie.
// ============================================================
const USAR_N8N = false;
const N8N_WEBHOOK_URL = "https://TU-TUNEL.ngrok-free.dev/webhook/agente-uth-chat";
const CHAT_URL = USAR_N8N ? N8N_WEBHOOK_URL : "/api/chat";

let MENU = {};   // se carga dinámicamente desde la base de conocimiento

const sessionId = "web-" + Math.random().toString(36).substring(2, 10);
document.getElementById("sessionLabel").textContent = sessionId;

const chatMessages = document.getElementById("chatMessages");
const quickReplies = document.getElementById("quickReplies");
const userInput = document.getElementById("userInput");

function agregarMensaje(texto, tipo) {
  const div = document.createElement("div");
  div.className = "msg " + tipo;
  div.textContent = texto;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function agregarEtiqueta(texto) {
  const div = document.createElement("div");
  div.className = "etiqueta";
  div.textContent = texto;
  chatMessages.appendChild(div);
}

// -------- Respuesta enriquecida del bot --------
function mostrarRespuestaBot(data) {
  agregarMensaje(data.texto, "bot");

  const acciones = document.createElement("div");
  acciones.className = "acciones";

  // Botón "Ver paso a paso" (respuesta explicativa)
  if (data.explicacion && data.explicacion.length > 0) {
    const btnPasos = document.createElement("button");
    btnPasos.textContent = "🧭 Ver paso a paso";
    btnPasos.onclick = () => {
      const caja = document.createElement("div");
      caja.className = "pasos";
      const titulo = document.createElement("b");
      titulo.textContent = "Explicación paso a paso:";
      caja.appendChild(titulo);
      const ol = document.createElement("ol");
      data.explicacion.forEach(p => {
        const li = document.createElement("li");
        li.textContent = p;
        ol.appendChild(li);
      });
      caja.appendChild(ol);
      chatMessages.appendChild(caja);
      chatMessages.scrollTop = chatMessages.scrollHeight;
      btnPasos.remove();
    };
    acciones.appendChild(btnPasos);
  }

  // Botones de retroalimentación
  if (data.faq_id) {
    const btnSi = document.createElement("button");
    btnSi.className = "fb-si";
    btnSi.textContent = "👍 Me fue útil";
    const btnNo = document.createElement("button");
    btnNo.className = "fb-no";
    btnNo.textContent = "👎 No me sirvió";
    const enviarFb = async (util) => {
      btnSi.remove(); btnNo.remove();
      try {
        await fetch("/api/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId, faq_id: data.faq_id, util: util })
        });
      } catch (e) { /* el feedback no debe interrumpir el chat */ }
      agregarEtiqueta(util ? "¡Gracias por tu valoración! ✔"
                          : "Gracias, tu comentario nos ayuda a mejorar. ✔");
      chatMessages.scrollTop = chatMessages.scrollHeight;
    };
    btnSi.onclick = () => enviarFb(true);
    btnNo.onclick = () => enviarFb(false);
    acciones.appendChild(btnSi);
    acciones.appendChild(btnNo);
  }

  if (acciones.children.length > 0) chatMessages.appendChild(acciones);

  // Preguntas relacionadas sugeridas
  if (data.relacionadas && data.relacionadas.length > 0) {
    agregarEtiqueta("También te puede interesar:");
    const rel = document.createElement("div");
    rel.className = "acciones";
    data.relacionadas.forEach(r => {
      const b = document.createElement("button");
      b.textContent = r.pregunta;
      b.onclick = () => seleccionarFaq(r.id, r.pregunta);
      rel.appendChild(b);
    });
    chatMessages.appendChild(rel);
  }
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// -------- Menú dinámico (navegación de opciones) --------
async function cargarMenu() {
  try {
    const resp = await fetch("/api/menu");
    MENU = await resp.json();
  } catch (e) { MENU = {}; }
}

function mostrarMenuCategorias() {
  quickReplies.innerHTML = "";
  Object.keys(MENU).forEach(cat => {
    const btn = document.createElement("button");
    btn.textContent = cat;
    btn.onclick = () => mostrarSubmenu(cat);
    quickReplies.appendChild(btn);
  });
  const btnAsesor = document.createElement("button");
  btnAsesor.textContent = "🙋 Hablar con un asesor";
  btnAsesor.onclick = () => enviarMensaje("hablar con un asesor");
  quickReplies.appendChild(btnAsesor);
}

function mostrarSubmenu(categoria) {
  agregarMensaje(categoria, "user");
  agregarMensaje("Estas son las preguntas frecuentes de " + categoria + ":", "bot");
  quickReplies.innerHTML = "";

  (MENU[categoria] || []).forEach(item => {
    const btn = document.createElement("button");
    btn.textContent = item.pregunta;
    btn.onclick = () => seleccionarFaq(item.id, item.pregunta);
    quickReplies.appendChild(btn);
  });

  const btnVolver = document.createElement("button");
  btnVolver.textContent = "⬅️ Volver al menú";
  btnVolver.onclick = () => mostrarMenuCategorias();
  quickReplies.appendChild(btnVolver);
}

// Selección de una pregunta del menú o de las relacionadas:
// responde directo por ID (se registra como 'respondida_menu').
async function seleccionarFaq(faqId, pregunta) {
  agregarMensaje(pregunta, "user");
  quickReplies.innerHTML = "";
  try {
    const resp = await fetch("/api/faq", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ faq_id: faqId, session_id: sessionId })
    });
    const data = await resp.json();
    mostrarRespuestaBot(data);
  } catch (e) {
    agregarMensaje("Ocurrió un error de conexión con el servidor.", "bot");
  }
  mostrarMenuCategorias();
}

// -------- Texto libre --------
async function enviarMensaje(textoForzado) {
  const texto = textoForzado || userInput.value.trim();
  if (!texto) return;
  agregarMensaje(texto, "user");
  userInput.value = "";
  quickReplies.innerHTML = "";

  if (texto.trim().toLowerCase() === "menu") {
    agregarMensaje("Estas son las categorías disponibles:", "bot");
    mostrarMenuCategorias();
    return;
  }

  try {
    const resp = await fetch(CHAT_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: texto, session_id: sessionId })
    });
    const data = await resp.json();
    mostrarRespuestaBot(data);
  } catch (e) {
    agregarMensaje(USAR_N8N
      ? "Error de conexión: verifica que n8n y ngrok estén corriendo."
      : "Ocurrió un error de conexión con el servidor local.", "bot");
  }
  mostrarMenuCategorias();
}

userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") enviarMensaje();
});

// Mensaje de bienvenida inicial
window.onload = async () => {
  await cargarMenu();
  agregarMensaje("¡Hola! Soy tu Asistente Universitario Virtual 🎓 " +
                 "Puedo ayudarte con información sobre el campus, horarios, " +
                 "trámites, soporte y vida estudiantil. Elige una categoría " +
                 "o escríbeme tu consulta.", "bot");
  mostrarMenuCategorias();
};
</script>

</body>
</html>
"""

PAGINA_METRICAS = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Métricas - Agente Virtual UTH</title>
<style>
  body { font-family: 'Segoe UI', Arial, sans-serif; background:#f2f4f7;
         margin:0; padding:30px 14px; display:flex; justify-content:center; }
  .panel { background:#fff; max-width:640px; width:100%; border-radius:14px;
           box-shadow:0 6px 24px rgba(0,0,0,.12); padding:24px 28px; }
  h1 { color:#163d6b; font-size:20px; margin:0 0 4px 0; }
  .sub { color:#8a8f98; font-size:12.5px; margin-bottom:18px; }
  .kpis { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px; }
  .kpi { flex:1; min-width:150px; background:#eef3f9; border-radius:10px;
         padding:14px; text-align:center; }
  .kpi b { display:block; font-size:26px; color:#163d6b; }
  .kpi span { font-size:12px; color:#5a6270; }
  table { width:100%; border-collapse:collapse; font-size:13.5px; margin-bottom:18px;}
  th, td { text-align:left; padding:7px 8px; border-bottom:1px solid #e3e6ea; }
  th { color:#163d6b; }
  td.num { text-align:right; font-weight:600; }
  .barra { background:#e3e6ea; border-radius:6px; height:10px; overflow:hidden; }
  .barra div { background:#2e75b6; height:100%; }
  a { color:#2e75b6; font-size:13px; text-decoration:none; }
</style>
</head>
<body>
<div class="panel">
  <h1>📊 Métricas de desempeño del agente</h1>
  <div class="sub">Calculadas en vivo a partir de logs/auditoria_consultas.csv
  y logs/feedback_respuestas.csv · Base de conocimiento v{{ version }} ·
  {{ total_faqs }} FAQs</div>

  <div class="kpis">
    <div class="kpi"><b>{{ m.tasa_resolucion|round(1) }}%</b>
      <span>Consultas resueltas automáticamente<br>({{ m.respondidas }}/{{ m.contenido }})</span></div>
    <div class="kpi"><b>{{ m.tasa_util|round(1) }}%</b>
      <span>Respuestas valoradas como útiles<br>({{ m.feedback_utiles }}/{{ m.total_feedback }})</span></div>
    <div class="kpi"><b>{{ m.total }}</b>
      <span>Consultas totales registradas</span></div>
  </div>

  <table>
    <tr><th>Resultado</th><th class="num">Consultas</th></tr>
    <tr><td>Respondidas por texto libre</td><td class="num">{{ m.respondidas_texto }}</td></tr>
    <tr><td>Respondidas por navegación de menú</td><td class="num">{{ m.respondidas_menu }}</td></tr>
    <tr><td>No reconocidas (se pidió reformular)</td><td class="num">{{ m.sin_resultado }}</td></tr>
    <tr><td>Transferencias explícitas a asesor</td><td class="num">{{ m.transf_explicita }}</td></tr>
    <tr><td>Transferencias por bucle de error</td><td class="num">{{ m.transf_bucle }}</td></tr>
  </table>

  <table>
    <tr><th>Categoría</th><th class="num">Resueltas</th><th style="width:45%"></th></tr>
    {% for cat, n in categorias %}
    <tr>
      <td>{{ cat }}</td><td class="num">{{ n }}</td>
      <td><div class="barra"><div style="width: {{ (n / maximo * 100)|round(0) }}%"></div></div></td>
    </tr>
    {% endfor %}
  </table>

  <a href="/">⬅️ Volver al chat</a>
</div>
</body>
</html>
"""


@app.route("/")
def inicio():
    return render_template_string(PAGINA_HTML)


@app.route("/metricas")
def panel_metricas():
    m = calcular_metricas()
    categorias = sorted(m["por_categoria"].items(), key=lambda x: -x[1])
    maximo = max([n for _, n in categorias], default=1)
    return render_template_string(
        PAGINA_METRICAS, m=m, categorias=categorias, maximo=maximo,
        version=engine.version_kb(), total_faqs=engine.total_faqs()
    )


@app.route("/api/chat", methods=["POST"])
def api_chat():
    datos = request.get_json(force=True, silent=True) or {}
    mensaje = datos.get("mensaje", "")
    session_id = datos.get("session_id", "web-anon")
    resultado = engine.procesar_mensaje(mensaje, session_id)
    return jsonify(resultado)


@app.route("/api/faq", methods=["POST"])
def api_faq():
    datos = request.get_json(force=True, silent=True) or {}
    faq_id = datos.get("faq_id", "")
    session_id = datos.get("session_id", "web-anon")
    resultado = engine.responder_faq_por_id(faq_id, session_id)
    return jsonify(resultado)


@app.route("/api/menu", methods=["GET"])
def api_menu():
    return jsonify(engine.listar_menu())


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    datos = request.get_json(force=True, silent=True) or {}
    ok = engine.registrar_feedback(
        datos.get("session_id", "web-anon"),
        datos.get("faq_id", ""),
        bool(datos.get("util", False))
    )
    return jsonify({"registrado": ok})


if __name__ == "__main__":
    print("=" * 60)
    print(" Agente Virtual UTH - Proyecto Final")
    print(f" Base de conocimiento v{engine.version_kb()} | FAQs: {engine.total_faqs()}")
    print(" Chat:     http://127.0.0.1:5000")
    print(" Métricas: http://127.0.0.1:5000/metricas")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
