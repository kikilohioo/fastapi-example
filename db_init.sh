#!/bin/sh
set -e  # Si algo falla, el script se detiene

# --------------------------------------------------------
# Esperar a que la base de datos esté lista
# --------------------------------------------------------
until pg_isready -h "$DATABASE_HOSTNAME" -p "$DATABASE_PORT" -U "$DATABASE_USERNAME" >/dev/null 2>&1; do
  sleep 2
done

echo "🔄 [DB_INIT] Iniciando proceso de arranque..."
sleep 1

echo "⏳ Verificando conexión a la base de datos en $DATABASE_HOSTNAME:$DATABASE_PORT ..."
sleep 1

echo "✅ Conexión establecida con la base de datos."
sleep 1

# --------------------------------------------------------
# Mostrar estado actual y migraciones disponibles
# --------------------------------------------------------
echo "📄 Consultando estado de migraciones..."
CURRENT=$(alembic current --verbose 2>/dev/null | grep -Eo '^ *Revision ID: *[a-f0-9]+' | awk '{print $3}' | tr '\n' ' ' | xargs || echo "none")
HEADS=$(alembic heads --verbose 2>/dev/null | grep -Eo '^ *Revision ID: *[a-f0-9]+' | awk '{print $3}' | tr '\n' ' ' | xargs || echo "none")

if [ -z "$CURRENT" ]; then
  echo "⚠️  No hay revisión actual (base de datos vacía o sin control de migraciones)."
else
  echo "🔹 Revisión actual: $CURRENT"
fi

if [ -z "$HEADS" ]; then
  echo "⚠️  No hay 'heads' definidos en las migraciones locales."
else
  echo "🔹 Último head disponible: $HEADS"
fi

sleep 1

if [ "$CURRENT" != "$HEADS" ]; then
  echo "🚀 Migraciones pendientes detectadas. Ejecutando 'alembic upgrade head'..."
  sleep 2
  alembic upgrade head
  echo "✅ Migraciones aplicadas correctamente."
else
  echo "✨ La base de datos ya está al día. No se requieren migraciones."
fi

sleep 1

# --------------------------------------------------------
# Iniciar la aplicación FastAPI
# --------------------------------------------------------
echo "🚀 Iniciando aplicación Uvicorn..."
echo "--------------------------------------------"

exec "$@"