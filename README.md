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
- Pasos para crear una distribucion de Ubunutu con wsl
- Configuracion de la maquina Ubuntu montada con wsl para despliegue de la aplicacion
- Creacion de service con gunicorn para mejor gestion de la aplicacion corriendo
- Creacion de un proxy con NGINX para mejorar la gestion de ssl terminations
- Configuracion basica de seguridad con ufw para restringir trafico mediante el firewall de Ubuntu
- Comming soon

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
30. Ahora para continuar con el curso necesitaremos una maquina Ubuntu disponible y accesible desde nuestra maquina local con Windows. Para ello en este manual usaremos wsl, por lo que lo tenemos que tener instalado y operativo, una vez confirmado esto ejecutaremos ```wsl --install -d Ubuntu``` lo que nos creara una instancia de Ubuntu dentro de nuestra maquina de Windows. Luego de completar el proceso ejecutaremos ```wsl --list``` y dara un resultado similar a:
```
Windows Subsystem for Linux Distributions:
Ubuntu (Default)
```
Como podemos ver tenemos por defecto en mi caso Ubuntu, entonces al ejecutar ```wsl``` se iniciara una sesion dentro de esta distibucion. Tambien para no extender demasiado esto, se recomienda instalar y configurar adecuadamente ssh para mejorar la experiencia de desarrollo/despliegue en la maquin Ubuntu.
31. Ahora tendremos que asegurarnos de tener python instalado con ```python3 --version``` y ademas deberemos de instalar si no lo tenemos aun pip3 con ```sudo apt install python3-pip -y```
32. Luego instalaremos ```sudo apt install python3.12-venv -y``` para crear los virtual environments. Adicionalmente para solventar otros errores encontrados mas adelante instalaremos lo siguiente ```sudo apt install -y libpq-dev python3-dev build-essential```
33. Tambien deberemos de tener una db de PostgreSQL lista para el entorno de produccion, idealmente instalada en esta maquin de Ubuntu, como este proceso es muy largo, lo agregaremos como requerimiento.
34. Con un usario sudo, pero no root por ejemplo "mynewuser" crearemos un directorio en nuestra maquina virtual, para alamacenar la aplicacion de FastAPI por ejemplo ```mkdir app```
35. Luego ```cd app``` y ahi crearemos un venv con ```python3 -m venv venv```
36. Luego crearemos una carpeta llamada src con ```mkdir src``` donde clonaremos nuestra aplicacion con git, hacemos ```cd src```
37. Clonamos con ```git clone <repo_clone_url> .```
38. Una vez clonado volvemos hacia atras con ```cd ..``` activamos el venv con ```source venv/bin/activate```
39. Volvemos a ```cd src``` y ejecutamos ```pip install -r requirements.txt``` para instalar todas las dependencias necesarias, quizas esto no funcione a la primera, actualmente lo hizo con los ajustes del paso 32. Y luego de eso desactivaremos el venv haciendo ```cd ..``` y luego ```deactivate```. Porque no lo necesitamos para los pasos inmediatos.
40. Ahora tendremos que configurar nuestras variables de entorno, las mismas que en desarrollo se resolvian con el archivo .env directamente en la raiz del proyecto, ahora vamos a hacer algo un poco diferente. Crearemos un archivo .env en /home/<mynewuser> con ```cd ~``` luego ```sudo vi .env``` y ahi copiaremos todas las variables de nuestro .env actual ajustando los valores para que tengan sentido con produccion. Guardamos ese archivo.
41. Luego editaremos el siguiente archivo ```sudo vi .profile``` y al final agregaremos lo siguiente ```set -o allexport; source /home/<mynewuser>/.env; set +o allexport```, que hara que persistan las variables de entorno incluso si se reinicia la maquina de Ubuntu.
42. En la nueva base de datos de produccion no tendremos las tablas creadas, por lo que usaremos Alembic, la herramienta que configuramos varios pasos atras. Para eso activaremos el venv estando en /home/<mynewuser>/app/ ```source venv/bin/activate``` nos moveremos a src con ```cd src``` y ejecutaremos el comando ```alembic upgrade head```
43. Ahora para el despliegue y la configuracion de persistencia de la aplicacion deberemos de instalar 2 nuevos paquetes con el siguiente comando ```pip install gunicorn uvloop```
44. Luego para probar que funcione correctamente ejecutaremos manualmente el siguiente comando ```gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:<port>```, con esto la api deberia de poder ser consumida con http://<ip_ubuntu_machine>:<port>/
45. Ahora vamos a crear un servicio en la maquina Ubuntu, copiando el que podemos encontrar en la raiz de este proyecto(gunicorn.service) y ajustando lo necesario para la implementacion que se esté haciendo. Para eso vamos a ```cd /etc/systemd/system/``` y ejecutamos ```vi <new_service_name>.service```, pegamos el contenido, lo ajustamos y listo, ya podemos ejecutar algo como ```sudo systemctl start newservicename``` y ahi deberiamos de ver algo muy similar a esto si todo sale bien y ejecutamos ```systemctl status newservicename```:
```
● newservicename.service - demo fastapi application
     Loaded: loaded (/etc/systemd/system/newservicename.service; disabled; preset: enabled)
     Active: active (running) since Wed 2025-10-29 23:23:32 -03; 9s ago
   Main PID: 607 (gunicorn)
      Tasks: 9 (limit: 9313)
     Memory: 274.5M (peak: 275.0M)
        CPU: 4.702s
     CGroup: /system.slice/newservicename.service
             ├─607 /home/fastapi/app/venv/bin/python3 /home/fastapi/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.Uvico>
             ├─608 /home/fastapi/app/venv/bin/python3 /home/fastapi/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.Uvico>
             ├─609 /home/fastapi/app/venv/bin/python3 /home/fastapi/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.Uvico>
             ├─610 /home/fastapi/app/venv/bin/python3 /home/fastapi/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.Uvico>
             └─611 /home/fastapi/app/venv/bin/python3 /home/fastapi/app/venv/bin/gunicorn -w 4 -k uvicorn.workers.Uvico>

Oct 29 23:23:33 kiki-pc gunicorn[609]: [2025-10-29 23:23:33 -0300] [609] [INFO] Started server process [609]
Oct 29 23:23:33 kiki-pc gunicorn[609]: [2025-10-29 23:23:33 -0300] [609] [INFO] Waiting for application startup.
Oct 29 23:23:33 kiki-pc gunicorn[610]: [2025-10-29 23:23:33 -0300] [610] [INFO] Application startup complete.
Oct 29 23:23:33 kiki-pc gunicorn[608]: [2025-10-29 23:23:33 -0300] [608] [INFO] Started server process [608]
Oct 29 23:23:33 kiki-pc gunicorn[608]: [2025-10-29 23:23:33 -0300] [608] [INFO] Waiting for application startup.
Oct 29 23:23:33 kiki-pc gunicorn[611]: [2025-10-29 23:23:33 -0300] [611] [INFO] Started server process [611]
Oct 29 23:23:33 kiki-pc gunicorn[611]: [2025-10-29 23:23:33 -0300] [611] [INFO] Waiting for application startup.
Oct 29 23:23:33 kiki-pc gunicorn[609]: [2025-10-29 23:23:33 -0300] [609] [INFO] Application startup complete.
Oct 29 23:23:33 kiki-pc gunicorn[608]: [2025-10-29 23:23:33 -0300] [608] [INFO] Application startup complete.
Oct 29 23:23:33 kiki-pc gunicorn[611]: [2025-10-29 23:23:33 -0300] [611] [INFO] Application startup complete.
``` 
de lo contrario debemos revisar que sucede y corregirlo
46. Por ultimo en este sentido ejecutaremos esto ```sudo systemctl enable newservicename``` para hacer que se reinicie automaticamente si se cae o se reinicia la maquina
47. Para mejorar la gestion de las ssl terminatios y las solicutdes https como seria en un ambiente de produccion configuraremos NGINX, primero lo vamos a instalar con el siguiente comando ```sudo apt install nginx -y```
48. Luego editaremos este archivo ```sudo vi /etc/nginx/sites-available/default``` y cambiaremos lo location por esto:
```
location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-NginX-Proxy true;
        proxy_redirect off;
}
```
49. Luego reiniciamos NGINX con ```sudo systemtl restart nginx``` y ahora apuntando a nuestra ip sin puerto o sea el por defecto :80, responde nuestra api.
50. Para mayor seguridad se recomienda tener un dns, certificados y toda lo necesario para configurar NGINX de una forma similar a esta:
```
# Redirección HTTP → HTTPS
server {
    listen 80;
    server_name midominio.local;
    return 301 https://$host$request_uri;
}

# HTTPS con proxy hacia FastAPI
server {
    listen 443 ssl http2;
    server_name midominio.local;

    ssl_certificate     /etc/ssl/localcerts/midominio.local.crt;
    ssl_certificate_key /etc/ssl/localcerts/midominio.local.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```
51. (No funcionara en WSL2 Ubuntu)Lo siguiente que vamos a hacer es activar el firewall y restringir lo mas posible como medida de seguriad la disponibilidad de los puertos de la maquina Ubuntu, para esto ejecutaremos estos comandos:
```
sudo ufw allow http
sudo ufw allow https
sudo ufw allow ssh  
sudo ufw allow 5432 # para conectarse desde pgadmin (no recomendado para produccion)
```
52. Comming soon