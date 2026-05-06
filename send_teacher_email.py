"""
Envío automático de correos motivacionales diarios a profesores de Básica.
Ejecutar de lunes a viernes a las 6:00 AM (Chile).
"""

import smtplib
import json
import os
import random
import hashlib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "jmoya@colegiocabodehornos.cl")
SENDER_NAME  = os.environ.get("SENDER_NAME",  "Colegio Cabo de Hornos")
SMTP_HOST    = os.environ.get("SMTP_HOST",    "smtp.office365.com")
SMTP_PORT    = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER    = os.environ.get("SMTP_USER",    SENDER_EMAIL)
SMTP_PASS    = os.environ.get("SMTP_PASS",    "")  # App password / contraseña de aplicación

# ── Banco de mensajes motivacionales ──────────────────────────────────────────

MESSAGES = [
    {
        "titulo": "Hoy es un gran día para inspirar",
        "cuerpo": (
            "Cada mañana es una nueva oportunidad para encender la chispa del "
            "aprendizaje en sus estudiantes. Su dedicación y entrega hacen la "
            "diferencia en la vida de cada niño y niña que pasa por su aula. "
            "¡Hoy será un día extraordinario!"
        ),
        "frase": "«La educación es el arma más poderosa que puedes usar para cambiar el mundo.» — Nelson Mandela",
    },
    {
        "titulo": "Su trabajo transforma vidas",
        "cuerpo": (
            "Detrás de cada estudiante que triunfa hay un profesor que creyó en él "
            "cuando nadie más lo hacía. Su presencia, su paciencia y su corazón son "
            "el motor que mueve el futuro de nuestra comunidad. "
            "¡Gracias por ser esa luz todos los días!"
        ),
        "frase": "«Un buen maestro puede inspirar esperanza, despertar la imaginación y despertar el amor por el aprendizaje.» — Brad Henry",
    },
    {
        "titulo": "¡Adelante, con energía y propósito!",
        "cuerpo": (
            "La constancia y el amor con que ejercen su vocación son un regalo "
            "invaluable para nuestros alumnos. Cada lección que preparan con cariño "
            "deja una huella profunda que durará toda la vida. "
            "¡Hoy empieza un día lleno de posibilidades!"
        ),
        "frase": "«Enseñar es tocar una vida para siempre.» — Proverbio anónimo",
    },
    {
        "titulo": "Juntos construimos un mejor mañana",
        "cuerpo": (
            "El trabajo en equipo de nuestros docentes es la base más sólida sobre "
            "la que crecen nuestros estudiantes. Cada sonrisa en el aula, cada "
            "pregunta respondida con paciencia, suma para construir ciudadanos "
            "íntegros. ¡Sigamos adelante con orgullo!"
        ),
        "frase": "«Educar a un niño no es hacerle aprender algo que no sabía, sino hacer de él alguien que no existía.» — John Ruskin",
    },
    {
        "titulo": "Su vocación hace historia",
        "cuerpo": (
            "Ser educador es uno de los roles más nobles que existen. Cada día "
            "escriben, junto a sus estudiantes, páginas de historia que el tiempo "
            "no borrará. Confíen en su talento, en su preparación y en el impacto "
            "positivo que generan. ¡Este día es suyo!"
        ),
        "frase": "«El maestro que intenta enseñar sin inspirar al alumno con el deseo de aprender está tratando de forjar el hierro frío.» — Horace Mann",
    },
    {
        "titulo": "Cada estudiante es un mundo por descubrir",
        "cuerpo": (
            "Con sensibilidad y creatividad logran llegar al corazón de cada "
            "estudiante. Su mirada atenta descubre talentos y potenciales que "
            "muchas veces el propio alumno aún no ve. Eso los hace únicos e "
            "irremplazables. ¡Que este día esté colmado de descubrimientos!"
        ),
        "frase": "«La tarea del maestro es enseñar a sus alumnos a ver la vida en toda su amplitud.» — Enrique Tierno Galván",
    },
    {
        "titulo": "¡Bienvenidos a un nuevo día de aprendizaje!",
        "cuerpo": (
            "Cada amanecer trae consigo la posibilidad de mejorar, de crecer y de "
            "conectar con los estudiantes de una manera nueva. Su entusiasmo es "
            "contagioso y su ejemplo, el mejor libro de texto. "
            "¡Que tengan un día maravilloso!"
        ),
        "frase": "«Dime y lo olvido, enséñame y lo recuerdo, involúcrame y lo aprendo.» — Benjamin Franklin",
    },
    {
        "titulo": "Con pasión se mueven montañas",
        "cuerpo": (
            "La pasión con la que enfrentan su labor es el ingrediente secreto que "
            "transforma una clase ordinaria en una experiencia memorable. Sus "
            "estudiantes los observan y aprenden no solo de lo que dicen, sino de "
            "todo lo que son. ¡Hoy brillarán con fuerza!"
        ),
        "frase": "«La educación es el pasaporte hacia el futuro, el mañana pertenece a aquellos que se preparan para él hoy.» — Malcolm X",
    },
    {
        "titulo": "El esfuerzo de hoy es el logro de mañana",
        "cuerpo": (
            "Cada tarea revisada, cada explicación repetida con paciencia, cada "
            "palabra de aliento dicha en el momento justo, son semillas que florecen "
            "en el futuro de sus estudiantes. ¡Sigan sembrando con amor y convicción!"
        ),
        "frase": "«El arte de enseñar es el arte de ayudar a descubrir.» — Mark van Doren",
    },
    {
        "titulo": "Hoy están haciendo historia",
        "cuerpo": (
            "Muchos años después, cuando sus alumnos recuerden su infancia escolar, "
            "recordarán a esos profesores que los marcaron positivamente. Ustedes "
            "son esos maestros que dejan huella. "
            "¡Que este día esté lleno de momentos que valgan la pena!"
        ),
        "frase": "«Un maestro afecta a la eternidad; nunca puede decir dónde termina su influencia.» — Henry Adams",
     },
    {
        "titulo": "La paciencia es su mayor virtud",
        "cuerpo": "Sabemos que hay días desafiantes, pero es precisamente en esos momentos donde su templanza guía a los más pequeños. Su calma es el refugio donde sus alumnos aprenden a crecer.",
        "frase": "«La paciencia es amarga, pero su fruto es dulce.» — Jean-Jacques Rousseau",
    },
    {
        "titulo": "Pequeños gestos, grandes cambios",
        "cuerpo": "Una palabra de aliento a tiempo puede cambiar el rumbo de la semana de un niño. Ustedes tienen el don de ver el potencial donde otros ven dificultades. Gracias por estar presentes.",
        "frase": "«La enseñanza es más que impartir conocimiento, es inspirar el cambio.» — William Arthur Ward",
    },
    {
        "titulo": "Ustedes son el corazón del colegio",
        "cuerpo": "Más allá de los contenidos, lo que nuestros estudiantes recordarán es cómo los hicieron sentir. Su calidez humana es lo que transforma nuestra institución en un segundo hogar.",
        "frase": "«El objeto de la educación es preparar a los jóvenes para que se eduquen a sí mismos durante toda su vida.» — Robert M. Hutchins",
    },
    {
        "titulo": "Creatividad que abre puertas",
        "cuerpo": "Cada vez que adaptan una lección para que todos entiendan, están haciendo magia pedagógica. Su creatividad es la llave que abre las puertas del conocimiento para cada niño.",
        "frase": "«La creatividad es la inteligencia divirtiéndose.» — Albert Einstein",
    },
    {
        "titulo": "Sembrando curiosidad",
        "cuerpo": "Un gran docente no da las respuestas, sino que enseña a hacerse las preguntas correctas. Que hoy sea un día de mucha curiosidad y descubrimientos en sus aulas.",
        "frase": "«No tengo talentos especiales, solo soy apasionadamente curioso.» — Albert Einstein",
    },
    {
        "titulo": "El valor del ejemplo",
        "cuerpo": "Los niños no siempre escuchan lo que decimos, pero siempre observan lo que hacemos. Su ética y compromiso son el mejor currículum que pueden entregar.",
        "frase": "«La enseñanza que deja huella no es la que se hace de cabeza a cabeza, sino de corazón a corazón.» — Howard G. Hendricks",
    },
    {
        "titulo": "Resiliencia en el aula",
        "cuerpo": "Enseñar requiere una fuerza especial. Gracias por levantarse cada día con la convicción de que cada estudiante merece una oportunidad de brillar.",
        "frase": "«El éxito no es el final, el fracaso no es fatal: es el coraje de continuar lo que cuenta.» — Winston Churchill",
    },
    {
        "titulo": "Arquitectos del pensamiento",
        "cuerpo": "Hoy ayudan a estructurar ideas, a cuestionar realidades y a soñar mundos mejores. Su labor intelectual es el cimiento de nuestra sociedad.",
        "frase": "«Educar la mente sin educar el corazón no es educación en absoluto.» — Aristóteles",
    },
    {
        "titulo": "La alegría de aprender",
        "cuerpo": "Que el entusiasmo que sienten por su profesión se contagie hoy en cada rincón del segundo ciclo. ¡Hagamos que aprender sea una aventura hoy!",
        "frase": "«El aprendizaje nunca agota la mente.» — Leonardo da Vinci",
    },
    {
        "titulo": "Puntales de esperanza",
        "cuerpo": "Incluso en los días nublados, su labor es un rayo de sol para aquellos estudiantes que enfrentan dificultades. Gracias por ser ese apoyo constante.",
        "frase": "«La educación es la esperanza del futuro.» — Proverbio",
    },
]

# ── Días de la semana en español ───────────────────────────────────────────────

DIAS = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}

MESES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}

# ── Funciones ──────────────────────────────────────────────────────────────────

def seleccionar_mensaje() -> dict:
    """Selecciona un mensaje determinístico según la fecha para no repetir en la semana."""
    hoy = date.today()
    seed = int(hashlib.md5(hoy.isoformat().encode()).hexdigest(), 16)
    return MESSAGES[seed % len(MESSAGES)]


def fecha_bonita() -> str:
    hoy = date.today()
    dia_semana = DIAS[hoy.weekday()]
    return f"{dia_semana}, {hoy.day} de {MESES[hoy.month]} de {hoy.year}"


def construir_html(mensaje: dict, fecha: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mensaje del Día</title>
  <style>
    body {{
      margin: 0; padding: 0;
      background-color: #f0f4f8;
      font-family: 'Segoe UI', Arial, sans-serif;
    }}
    .wrapper {{
      max-width: 620px;
      margin: 30px auto;
      background: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }}
    .header {{
      background: linear-gradient(135deg, #1a5276 0%, #2e86c1 100%);
      padding: 36px 32px 28px;
      text-align: center;
    }}
    .header .school {{
      color: #aed6f1;
      font-size: 13px;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}
    .header h1 {{
      color: #ffffff;
      font-size: 26px;
      margin: 0 0 6px;
      line-height: 1.3;
    }}
    .header .fecha {{
      color: #d6eaf8;
      font-size: 14px;
      margin: 0;
    }}
    .sun-icon {{
      font-size: 48px;
      margin-bottom: 12px;
      display: block;
    }}
    .body {{
      padding: 32px;
    }}
    .saludo {{
      font-size: 16px;
      color: #2c3e50;
      margin-bottom: 18px;
    }}
    .cuerpo {{
      font-size: 16px;
      color: #444;
      line-height: 1.8;
      margin-bottom: 28px;
    }}
    .frase-bloque {{
      background: #eaf4fc;
      border-left: 4px solid #2e86c1;
      border-radius: 4px;
      padding: 16px 20px;
      margin-bottom: 28px;
    }}
    .frase-bloque p {{
      margin: 0;
      font-style: italic;
      color: #1a5276;
      font-size: 15px;
      line-height: 1.7;
    }}
    .cierre {{
      font-size: 15px;
      color: #555;
      line-height: 1.7;
      margin-bottom: 24px;
    }}
    .firma {{
      font-size: 14px;
      color: #888;
      border-top: 1px solid #e0e0e0;
      padding-top: 20px;
      margin-top: 10px;
    }}
    .footer {{
      background: #f7f9fc;
      text-align: center;
      padding: 18px;
      font-size: 12px;
      color: #aaa;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <span class="sun-icon">☀️</span>
      <p class="school">Colegio Cabo de Hornos - Segundo ciclo básico</p>
      <h1>{mensaje["titulo"]}</h1>
      <p class="fecha">{fecha}</p>
    </div>
    <div class="body">
      <p class="saludo">Estimados y estimadas profesores y profesoras,</p>
      <p class="cuerpo">{mensaje["cuerpo"]}</p>
      <div class="frase-bloque">
        <p>{mensaje["frase"]}</p>
      </div>
      <p class="cierre">
        Les deseamos un día lleno de energía, entusiasmo y gratificantes momentos
        junto a sus estudiantes. ¡Que tengan un <strong>excelente día</strong>!
      </p>
      <div class="firma">
        Con aprecio,<br />
        <strong>John Moya - Director de estudio</strong><br />
        <a href="mailto:jmoya@colegiocabodehornos.cl" style="color:#2e86c1;">
          jmoya@colegiocabodehornos.cl
        </a>
      </div>
    </div>
    <div class="footer">
      Este mensaje es enviado automáticamente cada día hábil a las 08:00 h.<br />
      Colegio Cabo de Hornos - Segundo ciclo básico
    </div>
  </div>
</body>
</html>"""


def construir_texto_plano(mensaje: dict, fecha: str) -> str:
    return (
        f"Colegio Cabo de Hornos - Segundo ciclo básico\n"
        f"{fecha}\n\n"
        f"{mensaje['titulo']}\n"
        f"{'─' * len(mensaje['titulo'])}\n\n"
        f"Estimados y estimadas profesores y profesoras,\n\n"
        f"{mensaje['cuerpo']}\n\n"
        f"{mensaje['frase']}\n\n"
        f"Les deseamos un día lleno de energía, entusiasmo y gratificantes momentos "
        f"junto a sus estudiantes. ¡Que tengan un excelente día!\n\n"
        f"Con aprecio,\n"
        f"John Moya - Director de estudio\n"
        f"jmoya@colegiocabodehornos.cl\n"
    )


def cargar_destinatarios() -> list[str]:
    # Intenta cargar desde archivo, si falla usa una lista por defecto o env var
    ruta = Path(__file__).parent / "config" / "recipients.json"
    try:
        with open(ruta, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("basica", [])
    except FileNotFoundError:
        # Si el archivo no está en GitHub, intenta leer una variable de entorno
        # Esto es más seguro para evitar que el script se detenga
        env_recipients = os.environ.get("RECIPIENTS_LIST")
        if env_recipients:
            return [email.strip() for email in env_recipients.split(",")]
        return ["jmoya@colegiocabodehornos.cl"] # Fallback de seguridad


def enviar_correo(destinatarios: list[str]) -> None:
    if not destinatarios:
        raise ValueError("La lista de destinatarios está vacía.")
    if not SMTP_PASS:
        raise EnvironmentError("La variable de entorno SMTP_PASS no está definida.")

    mensaje = seleccionar_mensaje()
    fecha   = fecha_bonita()
    asunto  = f"☀️ ¡Buenos días! {mensaje['titulo']} — {fecha}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = asunto
    msg["From"]    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    msg["To"]      = ", ".join(destinatarios)

    msg.attach(MIMEText(construir_texto_plano(mensaje, fecha), "plain", "utf-8"))
    msg.attach(MIMEText(construir_html(mensaje, fecha),        "html",  "utf-8"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SENDER_EMAIL, destinatarios, msg.as_string())

    print(f"✅ Correo enviado a {len(destinatarios)} destinatario(s): {asunto}")


# ── Punto de entrada ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        destinatarios = cargar_destinatarios()
        enviar_correo(destinatarios)
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
        raise SystemExit(1)
