# Tina plena de flors 🌸

Sitio web para **Tina plena de flors**, una floristería especializada en arreglos florales, bodas y decoración de eventos. La aplicación presenta sus servicios, permite explorar un catálogo de productos y ofrece formularios para solicitar encargos o ponerse en contacto con el equipo.

> Este es un proyecto académico realizado en grupo. El repositorio reúne el trabajo y las aportaciones conjuntas del equipo durante el diseño y el desarrollo de la aplicación.

## Estado del proyecto

El sitio está preparado para ejecutarse como demostración local. Incluye medidas básicas de seguridad para los formularios, pero el servidor integrado de Flask no está pensado para producción.

## Funcionalidades

- Portada y presentación de la floristería.
- Secciones dedicadas a bodas, eventos y al equipo.
- Catálogo de flores cargado desde un archivo JSON.
- Filtros por categoría, precio, tipo de flor y envoltorio.
- Formulario de encargos y solicitudes de presupuesto.
- Formulario de contacto con validación de correo y teléfono.
- Almacenamiento de contactos en un archivo Excel.
- Integración preparada para mostrar reseñas de Google.
- Diseño adaptable a diferentes tamaños de pantalla.

## Tecnologías utilizadas

- **Python 3** y **Flask** para el servidor y las rutas de la aplicación.
- **HTML5** y plantillas **Jinja** para la estructura de las páginas.
- **CSS3**, Flexbox y Grid para el diseño visual y responsive.
- **JSON** para almacenar la información del catálogo.
- **OpenPyXL** para guardar los contactos en Excel.
- **Requests** para consultar servicios externos.
- **Email Validator** para validar direcciones de correo electrónico.
- **Flask-WTF** para proteger los formularios contra ataques CSRF.
- **Flask-Limiter** para limitar envíos repetidos.
- **Python Dotenv** para cargar la configuración privada desde `.env`.

## Estructura del proyecto

```text
flores_final/
├── app.py                 # Aplicación Flask y lógica del servidor
├── productos.json         # Datos del catálogo de flores
├── contactos.xlsx         # Datos locales generados (excluidos de Git)
├── .env.example           # Ejemplo de configuración sin secretos
├── requirements.txt       # Dependencias de Python
├── iniciar.command        # Inicio automático para macOS
├── static/
│   ├── img/               # Imágenes y recursos gráficos
│   ├── docs/              # Documentos legales
│   ├── Video1.mp4
│   ├── Video2.mp4
│   └── *.css              # Hojas de estilos de las secciones
└── templates/
    ├── mainDeIndex.html   # Portada
    ├── nosotros.html
    ├── bodas.html
    ├── eventos.html
    ├── flores.html
    ├── encargos.html
    └── contacto.html
```

## Requisitos previos

- Python 3.10 o una versión posterior.
- `pip`, incluido normalmente con Python.
- Git, únicamente si se desea clonar el repositorio.

## Instalación

1. Clona el repositorio y entra en su carpeta:

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd flores_final
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   En Windows, actívalo con:

   ```powershell
   venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Crea la configuración local:

   ```bash
   cp .env.example .env
   ```

5. Inicia la aplicación:

   ```bash
   python app.py
   ```

6. Abre [http://127.0.0.1:5001](http://127.0.0.1:5001) en el navegador.


## Configuración segura

Antes de iniciar la aplicación, copia el archivo de ejemplo:

```bash
cp .env.example .env
```

Variables disponibles:

| Variable | Obligatoria | Descripción |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | Sí | Firma de forma segura las sesiones y los tokens CSRF. |
| `GOOGLE_API_KEY` | No | Clave de Google Places para obtener reseñas reales. |
| `GOOGLE_PLACE_ID` | No | Identificador del negocio en Google Places. |
| `FLASK_DEBUG` | No | Activa el modo de depuración solo durante el desarrollo. |
| `SESSION_COOKIE_SECURE` | En producción | Limita el envío de cookies a conexiones HTTPS. |
| `RATELIMIT_STORAGE_URI` | En producción | Almacenamiento compartido para los límites de peticiones. |

Genera una clave privada para Flask:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copia el resultado en `FLASK_SECRET_KEY` dentro de `.env`. Para utilizar reseñas reales, completa también `GOOGLE_API_KEY` y `GOOGLE_PLACE_ID`. Si se dejan vacíos, la aplicación muestra reseñas de demostración.


Los formularios incluyen protección CSRF, límites de peticiones y longitudes máximas. Además, los valores guardados en Excel se tratan como texto cuando podrían interpretarse como fórmulas.

## Nota

El servidor Flask se ejecuta en modo de desarrollo. Para publicar la web en producción se debe usar un servidor WSGI y configurar correctamente las variables secretas.


## Autoría

Proyecto desarrollado de forma colaborativa como trabajo grupal.

<img width="1500" height="827" alt="inicio" src="https://github.com/user-attachments/assets/24a2d005-bfee-4319-b9ca-5389dbdf26b4" />

<img width="1509" height="827" alt="bodas" src="https://github.com/user-attachments/assets/86341b24-a318-416e-87a6-6534e2d76717" />

<img width="1511" height="827" alt="flores" src="https://github.com/user-attachments/assets/5208b576-7e3f-4d67-a823-4408331898fd" />

<img width="1508" height="827" alt="contacto" src="https://github.com/user-attachments/assets/c3322e2d-a4ea-4cd6-9bfd-e687818b519b" />




