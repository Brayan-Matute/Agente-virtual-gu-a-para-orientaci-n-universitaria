# Agente Virtual — Orientación Universitaria (UTH)
### Proyecto Final — Tercer Parcial

Chatbot de orientación para estudiantes con **45 preguntas frecuentes en 5
categorías**, clasificación de intención por palabras clave (PLN básico +
sistema experto), **respuestas explicativas paso a paso**, **preguntas
relacionadas**, **retroalimentación del estudiante (👍/👎)** y **módulo de
métricas de desempeño**. Tres vías de acceso: **interfaz web (navegador)**,
**Telegram** y **n8n + MySQL** (orquestación).

## Estructura del proyecto

```
agente_uth/
├── src/
│   ├── nlp_utils.py            # Normalización, tokenización y stop words
│   ├── chatbot_engine.py       # Motor: clasificación + explicaciones + feedback + logs
│   ├── app_web.py              # Interfaz web (Flask) + panel /metricas
│   ├── bot.py                  # Integración con Telegram (mismo motor)
│   ├── pruebas_piloto.py       # Batería de validación (30 casos simulados)
│   ├── demo_sesiones.py        # Demostración: sesiones de estudiantes nuevos
│   ├── metricas.py             # Métricas de desempeño + gráficas
│   └── exportar_kb_mysql.py    # Sincroniza la base con el canal n8n/MySQL
├── data/
│   ├── knowledge_base.json     # Base de conocimiento v3.0 (45 FAQs, 5 categorías)
│   └── knowledge_base_mysql.sql# Script de importación para MySQL (n8n)
├── logs/
│   ├── auditoria_consultas.csv # Auditoría de consultas (se genera en ejecución)
│   └── feedback_respuestas.csv # Valoraciones 👍/👎 (se genera en ejecución)
├── docs/
│   ├── Proyecto_Final_Agente_Virtual_UTH.docx       # Informe del tercer avance
│   ├── Manual_Actualizacion_Preguntas_Respuestas.docx
│   ├── Presentacion_Defensa_Final.pptx
│   ├── reporte_metricas.txt    # Última corrida de métricas
│   └── img_metricas/           # Gráficas para el informe
├── Agente Virtual UTH - Orientacion Universitaria2.0.json  # Workflow n8n
└── README.md
```

## Instalación

1. Clonar o descomprimir el proyecto (requiere Python 3.10+).
2. Instalar dependencias:
   ```
   pip install flask
   pip install matplotlib                # gráficas de métricas (opcional)
   pip install python-telegram-bot       # solo si se usará Telegram
   ```

## Ejecución — Interfaz web (recomendada para la demostración)

```
cd src
python app_web.py
```

Abrir en el navegador:

- **Chat:** http://127.0.0.1:5000
- **Panel de métricas en vivo:** http://127.0.0.1:5000/metricas

Por defecto el chat usa el motor local (`/api/chat`), sin dependencias
externas. Para usar la orquestación con n8n del segundo avance, poner
`USAR_N8N = true` en `app_web.py` y actualizar la URL del túnel ngrok.

## Ejecución — Telegram (opcional)

1. Crear un bot con [@BotFather](https://t.me/BotFather) y obtener el token.
2. Configurar la variable de entorno:
   ```
   export TELEGRAM_BOT_TOKEN="tu_token_aqui"      # Windows: set TELEGRAM_BOT_TOKEN=...
   ```
3. Ejecutar:
   ```
   cd src
   python bot.py
   ```

## Validación, demostración y métricas

```
cd src
python pruebas_piloto.py   # 30 consultas simuladas -> % de aciertos (actual: 100%)
python demo_sesiones.py    # 6 sesiones de estudiantes nuevos + feedback
python metricas.py         # métricas + gráficas en docs/img_metricas/
```

Métricas de la última corrida completa: **100% de exactitud** en la batería
de pruebas, **91.7% de resolución automática** y **88.9% de satisfacción**
(ver `docs/reporte_metricas.txt`).

## Actualizar preguntas y respuestas

La base de conocimiento vive en `data/knowledge_base.json` (única fuente de
verdad para web y Telegram). El procedimiento completo — agregar, editar o
retirar FAQs, convenciones de IDs y palabras clave, validación y
sincronización con MySQL/n8n — está documentado en
`docs/Manual_Actualizacion_Preguntas_Respuestas.docx`. En resumen:

1. Editar `data/knowledge_base.json` (copiar un registro existente como plantilla).
2. Validar: `python src/pruebas_piloto.py` (agregar un caso de prueba de la FAQ nueva).
3. Sincronizar el canal n8n: `python src/exportar_kb_mysql.py` e importar el `.sql`.

## Notas técnicas

- El motor (`chatbot_engine.py`) es compartido por todos los canales; los
  menús de la web y de Telegram se construyen **dinámicamente** desde la
  base de conocimiento, por lo que una categoría o pregunta nueva aparece
  sin modificar el código de las interfaces.
- Derivación a agente humano: automática tras 3 intentos fallidos
  consecutivos (bucle de error, registrado como `transferencia_bucle`) o
  ante petición explícita ("hablar con un asesor", "humano", "soporte").
- Auditoría: cada consulta queda en `logs/auditoria_consultas.csv` con
  fecha/hora, sesión, consulta, tokens, FAQ asignada, categoría, puntaje y
  resultado. Las valoraciones 👍/👎 quedan en `logs/feedback_respuestas.csv`.
- Librerías utilizadas: Flask (interfaz web), python-telegram-bot (canal
  Telegram), matplotlib (gráficas), n8n + MySQL (orquestación alterna).
  No se utilizan datasets externos: la base de conocimiento fue elaborada
  por el equipo.
