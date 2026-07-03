
from flask import Flask, request, render_template, redirect, url_for, flash
#flask_limiter para limitar la cantidad de envíos de formularios y prevenir spam
from flask_limiter import Limiter
#flask_limiter.util.get_remote_address para obtener la dirección IP del cliente
from flask_limiter.util import get_remote_address
#flask_wtf.csrf.CSRFProtect para proteger contra ataques CSRF (Cross-Site Request Forgery)
from flask_wtf.csrf import CSRFProtect
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os
import requests
import json
import re
#secrets para generar claves seguras y warnings para mostrar advertencias
import secrets
import warnings
#dotenv para cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv
from email_validator import validate_email, EmailNotValidError



# Cargar la configuración local sin incluir secretos en el código.
load_dotenv()

# Bloque para configurar pestaña Contacto y guardar datos en Excel
app = Flask(__name__)

secret_key = os.getenv("FLASK_SECRET_KEY")
if not secret_key:
    secret_key = secrets.token_hex(32)
    warnings.warn(
        "FLASK_SECRET_KEY no está configurada. Se usará una clave temporal; "
        "copia .env.example como .env para mantener las sesiones entre reinicios."
    )

app.config.update(
    SECRET_KEY=secret_key,
    MAX_CONTENT_LENGTH=1024 * 1024,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
)

csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri=os.getenv("RATELIMIT_STORAGE_URI", "memory://"),
)

EXCEL_FILE = 'contactos.xlsx'


def proteger_celda_excel(valor):
    """Evita que Excel interprete texto proporcionado por usuarios como fórmulas."""
    if isinstance(valor, str) and valor.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + valor
    return valor

# CREAR EXCEL SI NO EXISTE
def crear_excel():
    if not os.path.exists(EXCEL_FILE):

        wb = Workbook()
        ws = wb.active

        ws.title = "Contactos"

        ws.append([
            "ID",
            "Fecha",
            "Nombre",
            "Email",
            "Telefono",
            "Asunto",
            "Mensaje",
            "Contactado"
        ])

        wb.save(EXCEL_FILE)


# GENERAR NUEVO ID
def generar_id(ws):

    ultima_fila = ws.max_row

    if ultima_fila == 1:
        return 1

    ultimo_id = ws.cell(row=ultima_fila, column=1).value

    return ultimo_id + 1



@app.route("/guardar_contacto", methods=["POST"])
@limiter.limit("5 per minute")
def guardar_contacto():

    crear_excel()

    nombre = request.form.get("nombre", "").strip()
    email = request.form.get("email", "").strip()
    telefono = request.form.get("telefono", "").strip()
    asunto = request.form.get("asunto", "").strip()
    mensaje = request.form.get("mensaje", "").strip()

    if not all((nombre, email, asunto, mensaje)):
        flash("Completa todos los campos obligatorios.", "error")
        return redirect(url_for("contacto"))

    limites = ((nombre, 100), (email, 254), (telefono, 20), (asunto, 150), (mensaje, 2000))
    if any(len(valor) > maximo for valor, maximo in limites):
        flash("Uno de los campos supera la longitud permitida.", "error")
        return redirect(url_for("contacto"))
    
    # Validación del correo electrónico
    try:
        email_info = validate_email(email, check_deliverability=True)
        email = email_info.normalized
    except EmailNotValidError as e:
        flash(f"Error en el correo: {str(e)}")
        return redirect("/contacto")
        
    # Validación estricta de teléfono (España: 9 dígitos empezando por 6, 7, 8 o 9)
    telefono_limpio = telefono.replace(" ", "").replace("-", "")
    if telefono_limpio and not re.fullmatch(r"[6789]\d{8}", telefono_limpio):
        flash("Error en el teléfono: Introduce un número válido de 9 dígitos.")
        return redirect("/contacto")

    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    nuevo_id = generar_id(ws)

    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")

    ws.append([
        nuevo_id,
        fecha_actual,
        proteger_celda_excel(nombre),
        proteger_celda_excel(email),
        proteger_celda_excel(telefono_limpio),
        proteger_celda_excel(asunto),
        proteger_celda_excel(mensaje),
        "No"
    ])

    wb.save(EXCEL_FILE)

    flash("🌸 Mensaje enviado correctamente. ¡Te responderemos pronto!")

    return redirect("/contacto")


# Configuración opcional de Google Places mediante variables de entorno.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PLACE_ID = os.getenv("GOOGLE_PLACE_ID")

def obtener_resenas_google():
    if not GOOGLE_API_KEY or not PLACE_ID:
        # Reseñas reales de prueba hasta que configures tu API Key de Google
        enlace_resenas = "https://www.google.com/maps/place/Tina+plena+de+flors/@41.2810903,1.5470103,17z/data=!4m12!1m3!3m2!9m1!1b1!3m7!1s0x12a475877f0b2879:0xcdccdbfc0d3fc3c4!8m2!3d41.2810903!4d1.5495852!9m1!1b1!16s%2Fg%2F11ptlspzm4?entry=ttu"
        return [
            {"author_name": "Elena", "author_url": enlace_resenas, "relative_time_description": "Hace 7 meses", "text": "Contar con Alba e Isabel para las flores de nuestra boda fue todo un acierto. Supieron interpretar a la perfección todo lo que les propusimos...", "rating": 5},
            {"author_name": "Natalia", "author_url": enlace_resenas, "relative_time_description": "Hace 10 meses", "text": "Isabel y Alba hacen arte, convirtieron un jardín normalito en un paisaje de cuento de hadas. Mi boda sin ellas no hubiera sido lo mismo.", "rating": 5},
            {"author_name": "Laia", "author_url": enlace_resenas, "relative_time_description": "Hace 11 meses", "text": "La decoración floral para las mesas fue espectacular. Supo captar exactamente lo que estábamos buscando. Quedó súper cuidada, elegante y silvestre.", "rating": 5}
        ]

    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={PLACE_ID}&fields=reviews&key={GOOGLE_API_KEY}&language=es"
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        if 'result' in datos and 'reviews' in datos['result']:
            # Filtramos para mostrar solo reseñas buenas (de 4 o 5 estrellas)
            buenas_resenas = [r for r in datos['result']['reviews'] if r['rating'] >= 4]
            return buenas_resenas[:3] # Enviamos las 3 más recientes
    except Exception as e:
        print(f"Error obteniendo reseñas de Google: {e}")
    
    return []

# Ruta para la portada
@app.route('/')
@app.route('/portada')
@app.route('/index.html')
def inicio():
    return render_template('mainDeIndex.html')

# Ruta para la página sobre nosotros
@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/bodas')
def bodas():
    resenas_google = obtener_resenas_google()
    return render_template('bodas.html', resenas=resenas_google)

@app.route('/eventos')
def eventos():
    return render_template('eventos.html')

@app.route('/flores')
def flores():
    # Leer el archivo JSON de productos
    ruta_json = os.path.join(app.root_path, 'productos.json')
    with open(ruta_json, 'r', encoding='utf-8') as archivo:
        datos = json.load(archivo)
        todos_los_productos = datos.get('productos', [])
        
    # --- FILTROS DESDE EL SERVIDOR (SIN JAVASCRIPT) ---
    categoria_rapida = request.args.get('categoria')
    precio_desde = request.args.get('precio_desde', type=float)
    precio_hasta = request.args.get('precio_hasta', type=float)
    flores_sel = request.args.getlist('flor')
    env_sel = request.args.getlist('envoltorio')
    
    productos_filtrados = []
    for p in todos_los_productos:
        mostrar = True
        
        # 1. Filtros de Categorías Rápidas
        if categoria_rapida == 'ramos-baratos':
            if p.get('categoria') != 'Ramos' or not (15 <= float(p.get('precio', 0)) <= 50): mostrar = False
        elif categoria_rapida == 'peonias':
            if 'Peonías' not in p.get('tipo_flor', []): mostrar = False
        elif categoria_rapida == 'rosas':
            if 'Rosas' not in p.get('tipo_flor', []): mostrar = False
        elif categoria_rapida == 'caja':
            if 'Caja' not in p.get('envoltorio', ''): mostrar = False
        elif categoria_rapida == 'maceta':
            if p.get('categoria') != 'Plantas de casa' and 'Maceta' not in p.get('envoltorio', ''): mostrar = False
        elif categoria_rapida == 'preservadas':
            if p.get('categoria') != 'Preservados': mostrar = False
            
        # 2. Filtros de Barra Lateral
        precio_prod = float(p.get('precio', 0))
        if precio_desde is not None and precio_prod < precio_desde: mostrar = False
        if precio_hasta is not None and precio_prod > precio_hasta: mostrar = False
        if flores_sel and not any(f in p.get('tipo_flor', []) for f in flores_sel): mostrar = False
        if env_sel and not any(e in p.get('envoltorio', '') for e in env_sel): mostrar = False
            
        if mostrar:
            productos_filtrados.append(p)
            
    return render_template('flores.html', productos=productos_filtrados, total_mostrados=len(productos_filtrados))

@app.route('/pedidos', methods=['GET', 'POST'])
@app.route('/encargos', methods=['GET', 'POST'])
@limiter.limit("5 per minute", methods=["POST"])
def pedidos():
    # Valores por defecto para cuando se carga la página (GET)
    datos = {
        "email": "",
        "tipo_evento": "",
        "mensaje": "",
        "nota": ""
    }
    opciones_select = ["Boda", "Evento Corporativo", "Bautizo/Cumpleaños", "Ramo de Regalo", "Otro"]
    tipo_solicitud = "presupuesto"
    incluye_nota = False

    if request.method == 'POST':
        # Cuando se envía el formulario (POST)
        email = request.form.get("email", "").strip()

        if len(email) > 254:
            flash("El correo electrónico es demasiado largo.", "error")
            return redirect(url_for('pedidos'))
        
        # Validación del correo electrónico
        try:
            email_info = validate_email(email, check_deliverability=True)
            email = email_info.normalized
        except EmailNotValidError as e:
            flash(f"Error en el correo: {str(e)}", "error")
            return redirect(url_for('pedidos'))
            
        # Aquí en el futuro puedes guardar estos datos en un Excel igual que en contactos
        flash("🌸 Solicitud enviada correctamente. ¡Te responderemos pronto!", "success")
        return redirect(url_for('pedidos'))

    return render_template('encargos.html', 
                           datos=datos,
                           opciones_select=opciones_select,
                           tipo_solicitud=tipo_solicitud,
                           incluye_nota=incluye_nota)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


if __name__ == '__main__':
    debug = os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
    app.run(debug=debug, port=5001)
