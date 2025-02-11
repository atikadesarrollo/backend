# Backend Atika

Este es un proyecto basado en Flask llamado **Backend_Atika**. El proyecto está diseñado para proporcionar dos servicios principales: **odoo_api** y **datalake_api**.

## Estructura del Proyecto

```
Backend_Atika
├── odoo_api
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── datalake_api
│   ├── __init__.py
│   ├── routes.py
│   └── models.py
├── app.py
├── requirements.txt
└── README.md
```

## Instalación

1. Clona el repositorio:
   ```
   git clone <URL_DEL_REPOSITORIO>
   cd backend
   ```

2. Crea un entorno virtual:
   ```
   python -m venv venv
   ```

3. Activa el entorno virtual:
   - En Windows:
     ```
     venv\Scripts\activate
     ```
   - En macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Ejecución

Para ejecutar la aplicación, utiliza el siguiente comando:
```
python app.py
```

## Servicios

### odoo_api

- **Rutas**: Define las rutas para manejar las solicitudes HTTP relacionadas con Odoo.
- **Modelos**: Contiene las definiciones de los modelos de datos utilizados por el servicio.

### datalake_api

- **Rutas**: Define las rutas para manejar las solicitudes HTTP relacionadas con el Datalake.
- **Modelos**: Contiene las definiciones de los modelos de datos utilizados por el servicio.

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o envía un pull request para discutir cambios.

## Licencia

Este proyecto está bajo la Licencia MIT.