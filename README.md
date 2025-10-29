# Manual/Plantilla de API con FastAPI
#### Nota:
El proyecto fue construido en base a una maquina Windows, por lo que pueden haber diferencias cuando se quiera integrar en MacOS o Linux

### Resumen:
Este repositorio esta pensado como una especie de plantilla/manual para utilizar como base para nuevos proyectos basados en FastAPI. Incluye algunas cosas importantes como:
- Integracion con modelos de SQLAlchemy, asi como las operaciones CRUD y algunas consultas mas complejas de ejemplos
- Integracion con Alembic para la gestion de migraciones a la base de datos ya integrada con SQLAlchemy lo que facilita la reutilizacion de modelos de SQLAlchemy para la gestion de la base de datos
- Implementacion de OAuth2 con JWT
- Gestion profesional de variables de entorno
- Gestion profesional basica de Usuarios/Claves
- Configuracion basica de CORS

---
# Paso a Paso

1. Asgurarse de tener la version de python necesaria
2. Crear una carpeta para el nuevo proyecto
3. Ejecutar esto ```py -3 -m venv <name>``` para crear un virtual environment esto es especialmente necesario para aislar las dependencias de cada proyecto
4. Activar el venv con ```.\<name>\Scripts\activate```
5. Instalar FastAPI con ```pip install fastapi[all]``` que instala FastAPI con otros paquetes de uso "comun", aunque se puede hacer una instalacion mas custom
6. Crear un archivo ./app/main.py e incluir este codigo:
    ```
    from fastapi import FastAPI

    app = FastAPI()


    @app.get("/")
    async def root():
        return {"message": "Hello World"}

    ```
    Esto es lo minimo y necesario para levantar la API
7. Crear un archivo ./app/__init__.py. Luego ejecutamos ```uvicorn app.main:app --reload``` para dejar corriendo la API y que se refresque automaticamente con cambios gracias a las flag "--reload"
8. Para este punto ya necesitariamos tener la fuente de datos normalmente la base de datos creada
9. Para el control maximo o mas core respecto a consultas sql podemos usar psycopg2 instalando ```pip install psycopg2```, aunque tenemos otras alternativas por ahi
10. Para el uso CRUD basico se encuentra un archivo ./app/main.py.rawsql que puedes usar como referencia para el uso de esta libreria. Ahi tenemos conexion a la db, uso de commits, etc.
11. En caso de preferir un ORM como es usual, usaremos SQLAlchemy uno de los ORMs mas utilizados en python, para ello instalaremos la dependencia con ```pip install sqlalchemy```
12. Segun la doc oficial de FastAPI tambien nos recomiendan usar sqlmodel con este comando ```pip install sqlmodel``` y mas adelante veremos como se utiliza. (Investigar) por ahora lo hacemos con SQLAlchemy BaseModel en ./app/models.py
13. Ademas tenemos ./app/schemas.py para definir los RequestSchemas y ResponseSchemas para controlar que info se puede y debe recibir y cual se tiene que retornar en respuesta a la solicitud.
14. Ahora pasaremos a un tema importante que es Authentication: para almacenar contraseñas, claves u otros datos sensibles de forma segura. Para ello tendremos que instalar lo siguiente ```pip install passlib[bcrypt]``` que instala la libreria passlib con el algoritmo bcrypt sumamente usado para este fin. Hay que eliminar bcrypt e instalar la version 4.0.1 con ```pip install "bcrypt==4.0.1"```, ya que sino hay un conflicto entre passlib y bcrypt.
15. Ahora para poder generar sesiones con JWT que es una forma usual de resolver la gestion de sesiones vamos a instalar ```pip install python-jose[cryptography]```.
16. La implementacion de JWT y Authentication se puede ver en el archivo ./app/oauth2.py donde estan todos los metodos necesarios para procesar correctamente las solicitudes que requieren o generan la authentication.
17. Ahora pasamos a modificar los modelos de SQLAlchemy para generar claves foraneas y relaciones, lo cual se puede ver reflejado en ./app/models.py, tambien es necesario ajustar ./app/schemas.py para ajustar las ResponseSchemas segun se requiera agregar alguno de ellos.
18. Lo siguiente es crear un archivo ./app/config.py para cargar las variables de entorno almacenadas en ./.env
19. Otro tema importante son las db migrations para eso usaremos alembic que se instala con ```pip install alembic``` y nos deja utilizar el comando ```alembic <some_cool_extra_command>```.
20. En relacion al punto anterior ejecutaremos ```alembic init <dir_name>``` que nos creara un directorio de inicializacion de la herramienta con el nombre indicado, donde encontraremos varias cosas.
21. Entre ellas un archivo ./<dir_name>/env.py que es el archivo principal de configuracion de la herramienta. En este tenemos que importar la declarative base model(Base) creada en nuestro archivo ./app/database.py agregando esto ```from app.models import Base``` y modificando esta linea ```target_metadata = None``` por ```target_metadata = Base```
22. Ademas ese comando nos genera un alembic.ini en la raiz del proyecto, archivo en el cual deberemos de modificar esta linea ```sqlalchemy.url = driver://user:pass@localhost/dbname``` por ```sqlalchemy.url = ```.
23. Luego de eso volvemos a editar el archivo ./<dir_name>/env.py, importaremos ```from app.config import settings``` y luego de esta linea ```config = context.config``` agregamos ```config.set_main_option('sqlalchemy.url', f'postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}')```
24. Ahora pasamos a crear manualmente las migraciones en el orden que creamos necesario por tema de keys, contraints, etc. Para eso ejecutaremos ```alembic revision -m "<nombre de la migracion>"``` por ejemplo ```alembic revision -m "create posts table"```, es una libreria bastante compleja pero aqui podemos encontrar todo lo necesario https://alembic.sqlalchemy.org/ y especifiamente aqui https://alembic.sqlalchemy.org/en/latest/api/ddl.html cosas relacionadas sobre las operaciones mas comunes de las migraciones.
25. Luego de creada toda la estructura de las migraciones, podremos ejecutar ```almebic upgrade <Revision ID>/head``` y si todo sale relativamente bien deberiamos de ver algo como esto:
```
alembic upgrade 260852ba2f36
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 260852ba2f36, create posts table
```
26. Tambien podemos hacer downgrade con ```almebic downgrade <Revision ID>/-n(1,2,3,etc)``` o para reiniciar todo ```alembic downgrade base```
27. Al conectar alembic en el paso 21 con los modelos de sqlalchemy, podriamos autogenerar todas las migraciones necesarias con ```alembic revision --autogenerate -m "<autogenerated_cool_name>"```, en mi caso solo deje una tabla por fuera, asi que tendria que generar una revision para crear dicha tabla.
28. Ahora para no tener conlflictos entre alembic y sqlalchemy tendremos que asegurarnos de no tener esta linea en nuestro ./app/main.py ```models.Base.metadata.create_all(bind=engine)``` y tambien es conveniente eliminar las dependencias importadas para el mismo.
29. Lo siguiente es configurar CORS adecuadamente segun nuestras necesidades, para eso importaremos en nuestro ./app/main.py esto ```from fastapi.middleware.cors import CORSMiddleware``` y agregaremos esto luego de instanciar FastAPI:
```
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
```
30. 