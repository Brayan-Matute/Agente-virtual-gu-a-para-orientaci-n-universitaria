-- ------------------------------------------------------------
-- Base de conocimiento del Agente Virtual UTH (canal n8n/MySQL)
-- Generado desde data/knowledge_base.json v3.0 (45 FAQs)
-- Importar con: mysql -u usuario -p base_de_datos < knowledge_base_mysql.sql
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS knowledge_base (
  id VARCHAR(10) PRIMARY KEY,
  categoria VARCHAR(60) NOT NULL,
  palabras_clave TEXT NOT NULL,   -- arreglo JSON en texto
  pregunta TEXT NOT NULL,
  respuesta TEXT NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sesiones (
  session_id VARCHAR(80) PRIMARY KEY,
  fallos_consecutivos INT NOT NULL DEFAULT 0
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auditoria_consultas (
  id INT AUTO_INCREMENT PRIMARY KEY,
  fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  session_id VARCHAR(80),
  canal VARCHAR(20),
  consulta_original TEXT,
  tokens_detectados TEXT,
  faq_id_asignada VARCHAR(10),
  categoria VARCHAR(60),
  puntaje INT,
  resultado VARCHAR(40),
  intentos_fallidos_sesion INT
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Se reemplaza el contenido completo para mantener la tabla
-- identica a knowledge_base.json (unica fuente de verdad).
TRUNCATE TABLE knowledge_base;

INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF01', 'Infraestructura', '["pagar", "pago", "matricula", "mensualidad", "caja", "donde pago"]',
   '¿Dónde pago la matrícula o mensualidad?',
   'Puedes realizar tus pagos en el área de Caja ubicada en el edificio principal, o en línea a través del portal estudiantil con tu tarjeta de crédito/débito.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF02', 'Infraestructura', '["aula", "salon", "edificio", "ubicacion", "salon de clases"]',
   '¿Dónde queda el aula o el edificio de mi clase?',
   'La distribución de aulas se publica en el mapa del campus disponible en recepción y en el portal estudiantil. Indícame el código del aula (ej. B-204) y te oriento al edificio correspondiente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF03', 'Infraestructura', '["registro", "admisiones", "oficina", "donde esta registro"]',
   '¿Dónde están ubicadas las oficinas de Registro y Admisiones?',
   'Las oficinas de Registro y Admisiones se encuentran en el edificio principal, planta baja, junto al área de Caja.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF04', 'Infraestructura', '["biblioteca", "libros", "sala de estudio", "ubicacion biblioteca", "queda biblioteca"]',
   '¿Dónde se encuentra la biblioteca?',
   'La biblioteca está ubicada en el edificio central, segundo nivel. Su horario regular es de lunes a viernes de 7:00 AM a 8:00 PM y sábados de 8:00 AM a 12:00 PM.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF05', 'Infraestructura', '["laboratorio", "computo", "computadoras", "lab", "laboratorios de computo", "laboratorios"]',
   '¿Dónde están los laboratorios de cómputo?',
   'Los laboratorios de cómputo están distribuidos en el edificio de Ingeniería, niveles 1 y 2. El acceso requiere carnet estudiantil vigente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF06', 'Infraestructura', '["comida", "cafeteria", "comer", "almorzar"]',
   '¿Dónde se encuentran las áreas de comida?',
   'La cafetería principal está en la plaza central del campus, y existen kioscos adicionales cerca del edificio de Ingeniería y el edificio de Negocios.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF07', 'Infraestructura', '["parqueo", "estacionamiento", "carro", "moto"]',
   '¿Dónde puedo estacionar mi vehículo?',
   'El campus cuenta con parqueo vehicular en la entrada principal y un área específica para motocicletas junto al edificio de Ingeniería. El acceso requiere el carnet vehicular institucional.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF08', 'Infraestructura', '["enfermeria", "clinica", "primeros auxilios"]',
   '¿Dónde está la clínica o enfermería del campus?',
   'La clínica estudiantil se encuentra en el edificio de Bienestar Universitario, planta baja, frente a la cancha deportiva.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF09', 'Infraestructura', '["auditorio", "usos multiples", "salon de eventos", "sala de conferencias", "queda auditorio", "auditorio principal"]',
   '¿Dónde queda el auditorio o los salones de usos múltiples?',
   'El auditorio principal está en el edificio central, primer nivel. Los salones de usos múltiples se encuentran en el edificio de Bienestar Universitario y se reservan a través de la administración del campus.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('INF10', 'Infraestructura', '["libreria", "fotocopias", "fotocopiado", "impresiones", "imprimir"]',
   '¿Dónde está la librería o el centro de fotocopiado?',
   'La librería y el centro de fotocopiado e impresiones están en la plaza central, junto a la cafetería principal. Ofrecen impresión, escaneo, empastados y venta de útiles.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR01', 'Horarios', '["horario registro", "atencion registro", "cuando atiende registro"]',
   '¿Cuál es el horario de atención de Registro?',
   'La oficina de Registro atiende de lunes a viernes de 8:00 AM a 7:00 PM, y los sábados de 8:00 AM a 12:00 PM.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR02', 'Horarios', '["jornada", "matutina", "vespertina", "nocturna", "hora inicio clases"]',
   '¿A qué hora inician y terminan las clases en las diferentes jornadas?',
   'Jornada matutina: 6:00 AM a 12:00 PM. Jornada vespertina: 12:30 PM a 6:00 PM. Jornada nocturna: 6:15 PM a 10:00 PM.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR03', 'Horarios', '["periodo academico", "inicio periodo", "fin periodo", "fechas importantes"]',
   '¿Cuáles son las fechas de inicio y fin del período académico actual?',
   'El período académico vigente inicia la primera semana de cada cuatrimestre. Puedes consultar las fechas exactas en el calendario académico publicado en el portal estudiantil.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR04', 'Horarios', '["adicion", "cancelacion", "agregar clase", "quitar clase"]',
   '¿Cuándo es el período para adiciones y cancelaciones de asignaturas?',
   'El período de adiciones y cancelaciones se habilita durante las dos primeras semanas posteriores al inicio de clases, según el calendario académico vigente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR05', 'Horarios', '["examen", "parcial", "fecha examen", "calendario examenes"]',
   '¿Cuándo son los exámenes parciales?',
   'Las fechas de exámenes parciales se publican en el calendario académico oficial al inicio de cada cuatrimestre y pueden variar según la sección.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR06', 'Horarios', '["vacaciones", "receso", "dias feriados"]',
   '¿Cuándo son los períodos de vacaciones o receso académico?',
   'Los períodos de receso académico se establecen en el calendario institucional anual, disponible en el portal estudiantil y en Registro.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR07', 'Horarios', '["horario biblioteca", "hora abre biblioteca", "hora cierra biblioteca"]',
   '¿Cuál es el horario de la biblioteca?',
   'La biblioteca atiende de lunes a viernes de 7:00 AM a 8:00 PM y sábados de 8:00 AM a 12:00 PM. En semanas de exámenes el horario se amplía; revisa los avisos del portal estudiantil.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('HOR08', 'Horarios', '["horario laboratorio", "hora laboratorios", "laboratorios abiertos"]',
   '¿Cuál es el horario de los laboratorios de cómputo?',
   'Los laboratorios de cómputo abren de lunes a sábado de 7:00 AM a 9:00 PM. Fuera de las clases programadas puedes usarlos libremente presentando tu carnet estudiantil.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA01', 'Procesos Academicos', '["matricular", "matricula", "clases por periodo", "limite clases"]',
   '¿Cuántas clases puedo matricular por período?',
   'El límite estándar es de 4 asignaturas, pero depende de tu índice académico del período anterior y la aprobación de tu coordinador de carrera.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA02', 'Procesos Academicos', '["prematricula", "como matricular", "proceso matricula"]',
   '¿Cómo puedo realizar la prematrícula o matrícula de mis clases?',
   'Ingresa al portal estudiantil con tu usuario y contraseña, selecciona la opción ''Matrícula'', elige tus asignaturas disponibles según tu pensum y confirma el pago correspondiente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA03', 'Procesos Academicos', '["certificacion", "historial academico", "documentos requeridos", "certificacion de notas", "certificacion estudios", "constancia de estudios"]',
   '¿Qué documentación requiero para solicitar una certificación de estudios?',
   'Debes presentar tu carnet estudiantil vigente, completar el formulario de solicitud en Registro y realizar el pago del arancel correspondiente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA04', 'Procesos Academicos', '["retiro", "retirar periodo", "abandonar clases"]',
   '¿Cómo se realiza el proceso formal para el retiro de un período académico?',
   'Debes presentar una solicitud formal por escrito en Registro dentro del plazo establecido en el calendario académico, adjuntando la justificación correspondiente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA05', 'Procesos Academicos', '["cambio carrera", "cambiar carrera"]',
   '¿Cómo puedo solicitar un cambio de carrera?',
   'El cambio de carrera se solicita en la oficina de Registro mediante un formulario específico, sujeto a la disponibilidad de cupos y aprobación de la dirección académica.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA06', 'Procesos Academicos', '["equivalencia", "convalidacion", "materias aprobadas otra institucion"]',
   '¿Cómo solicito equivalencias de materias de otra universidad?',
   'Debes presentar tu certificación de notas original y el programa analítico de las asignaturas en la oficina de Registro para su evaluación y convalidación.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA07', 'Procesos Academicos', '["pensum", "plan de estudios", "malla curricular"]',
   '¿Dónde puedo consultar el pensum de mi carrera?',
   'El pensum académico de tu carrera está disponible en el portal estudiantil, en la sección ''Plan de Estudios'', y también puede ser consultado con tu coordinador de carrera.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA08', 'Procesos Academicos', '["graduacion", "requisitos graduarme", "tramite de grado"]',
   '¿Cuáles son los requisitos para solicitar mi graduación?',
   'Debes haber aprobado el 100% de tu pensum, estar solvente económicamente y presentar la solicitud de graduación en Registro dentro de las fechas establecidas.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA09', 'Procesos Academicos', '["practica profesional", "pps", "horas practica"]',
   '¿Cómo gestiono mi práctica profesional supervisada?',
   'Debes acercarte a la coordinación de prácticas profesionales de tu facultad para conocer los convenios disponibles y los requisitos de inscripción.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA10', 'Procesos Academicos', '["reposicion", "reponer examen", "no presente examen", "examen reposicion"]',
   '¿Cómo solicito la reposición de un examen?',
   'Debes presentar la solicitud de reposición en Registro dentro de los 3 días hábiles siguientes al examen, adjuntando la justificación (médica o laboral) y pagando el arancel correspondiente. El docente programa la nueva fecha.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA11', 'Procesos Academicos', '["calificaciones", "calificacion", "ver notas", "mis notas parciales", "cuanto saque"]',
   '¿Cómo consulto mis calificaciones o notas parciales?',
   'Ingresa al portal estudiantil, sección ''Calificaciones'', y selecciona el período. Ahí verás las notas de cada parcial por asignatura. Si detectas un error, repórtalo a tu docente dentro del plazo de revisión.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('ACA12', 'Procesos Academicos', '["indice academico", "promedio", "indice", "calcular promedio"]',
   '¿Qué es el índice académico y cómo lo calculo?',
   'El índice académico es el promedio ponderado de tus calificaciones finales. Se calcula sumando (nota final × unidades valorativas) de cada asignatura y dividiendo entre el total de unidades cursadas. Puedes verlo en el portal estudiantil, sección Historial.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP01', 'Soporte y Cuentas', '["clave", "contrasena", "olvide contrasena", "campus virtual", "restablecer"]',
   'Olvidé mi clave del campus virtual, ¿qué hago?',
   'Ingresa al enlace ''Soportes / Olvidé mi contraseña'' en la página de inicio del campus, o envía un correo con tu número de cuenta a soporte@universidad.edu.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP02', 'Soporte y Cuentas', '["correo institucional", "email institucional", "recuperar correo"]',
   '¿Cómo restablezco mi contraseña del correo institucional?',
   'Accede al portal de soporte técnico institucional con tu número de cuenta y responde las preguntas de seguridad, o contacta a soporte@universidad.edu.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP03', 'Soporte y Cuentas', '["beca", "becas", "ayuda financiera"]',
   '¿Qué becas ofrece la institución?',
   'La universidad ofrece becas académicas, deportivas y socioeconómicas. Puedes solicitar información detallada en la oficina de Bienestar Estudiantil.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP04', 'Soporte y Cuentas', '["psicologia", "orientacion psicologica", "salud mental"]',
   '¿La institución ofrece orientación psicológica?',
   'Sí, el departamento de Bienestar Universitario ofrece atención psicológica gratuita para estudiantes. Puedes agendar tu cita en el edificio de Bienestar Universitario.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP05', 'Soporte y Cuentas', '["bancos", "formas de pago", "modalidades pago", "pagar en linea"]',
   '¿Cuáles son las modalidades y bancos autorizados para el pago de matrícula?',
   'Puedes pagar en los bancos autorizados (consulta la lista vigente en el portal estudiantil), en línea con tarjeta de crédito/débito, o presencialmente en Caja.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP06', 'Soporte y Cuentas', '["carnet", "carnet estudiantil", "identificacion"]',
   '¿Cómo obtengo o renuevo mi carnet estudiantil?',
   'El carnet estudiantil se solicita en la oficina de Bienestar Universitario presentando tu recibo de matrícula vigente y una fotografía reciente.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP07', 'Soporte y Cuentas', '["wifi", "internet", "red campus", "conexion"]',
   '¿Cómo me conecto al wifi del campus?',
   'Selecciona la red institucional en tu dispositivo e ingresa tus credenciales de campus virtual (usuario y contraseña) para autenticarte.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP08', 'Soporte y Cuentas', '["asesor", "hablar con humano", "soporte humano", "agente real"]',
   'Quiero hablar con un asesor humano',
   'Entendido. Te voy a transferir con un agente humano. Por favor espera mientras te compartimos los canales y horarios de atención presencial disponibles.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP09', 'Soporte y Cuentas', '["clases virtuales", "videoconferencia", "zoom", "teams", "clase en linea"]',
   '¿Cómo accedo a mis clases virtuales o videoconferencias?',
   'Los enlaces de videoconferencia se publican dentro de cada asignatura en el campus virtual. Ingresa con tus credenciales, abre la asignatura y usa el enlace de la sesión programada. Necesitas tu cuenta institucional activa.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('SOP10', 'Soporte y Cuentas', '["factura", "recibo", "comprobante de pago", "constancia de pago", "estado de cuenta"]',
   '¿Cómo obtengo una factura o constancia de mis pagos?',
   'Puedes descargar tus comprobantes desde el portal estudiantil, sección ''Estado de Cuenta''. Para facturas con datos fiscales o constancias firmadas, solicítalas en el área de Caja presentando tu recibo original.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('VID01', 'Vida Estudiantil', '["deportes", "deporte", "futbol", "equipo deportivo", "seleccion", "entrenamientos"]',
   '¿Qué deportes o equipos representativos tiene la universidad?',
   'La universidad cuenta con equipos de fútbol, baloncesto, voleibol y ajedrez. Las inscripciones y horarios de entrenamiento se gestionan en la oficina de Bienestar Universitario, y los deportistas destacados pueden optar a beca deportiva.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('VID02', 'Vida Estudiantil', '["grupos estudiantiles", "voluntariado", "asociacion de estudiantes", "club"]',
   '¿Cómo me uno a grupos estudiantiles o voluntariado?',
   'Cada facultad tiene una asociación de estudiantes y existen clubes académicos y programas de voluntariado coordinados por Bienestar Universitario. Al inicio de cada período se realiza una feria de grupos donde puedes inscribirte.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('VID03', 'Vida Estudiantil', '["eventos", "actividades culturales", "conciertos", "ferias", "actividades"]',
   '¿Dónde veo los eventos y actividades culturales?',
   'El calendario de eventos, ferias y actividades culturales se publica en el portal estudiantil, en las pantallas informativas del campus y en las redes sociales oficiales de la universidad.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('VID04', 'Vida Estudiantil', '["bolsa de trabajo", "empleo", "pasantia", "pasantias", "vacantes"]',
   '¿La universidad tiene bolsa de trabajo o pasantías?',
   'Sí. La oficina de Vinculación Empresarial publica vacantes de empleo y pasantías con empresas en convenio. Regístrate en la bolsa de trabajo desde el portal estudiantil y sube tu hoja de vida actualizada.');
INSERT INTO knowledge_base (id, categoria, palabras_clave, pregunta, respuesta) VALUES
  ('VID05', 'Vida Estudiantil', '["intercambio", "movilidad estudiantil", "intercambio academico", "estudiar en el extranjero"]',
   '¿Existen programas de intercambio académico?',
   'La universidad mantiene convenios de movilidad estudiantil con universidades de la región. Los requisitos generales son índice académico mínimo de 80%, haber aprobado el 50% del pensum y aplicar en la convocatoria anual de la oficina de Relaciones Internacionales.');
