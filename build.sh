#!/usr/bin/env bash
# build.sh

echo "🚀 Iniciando build en Render..."

# Instalar dependencias
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p media/alertas
mkdir -p media/videos
mkdir -p staticfiles

# Verificar estructura de archivos
echo "🔍 Verificando estructura de archivos..."
find . -name "*.mp4" -o -name "*.pt" | head -10

# Colectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# Aplicar migraciones
echo "🔄 Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado"