#!/bin/bash
# Script de configuración automática del backend

set -e  # Salir si hay error

echo "🚀 Setup del Backend - CU0008 y CU0016"
echo "======================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    echo "Instala Python 3.11+ desde https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Verificar MongoDB
if ! command -v mongosh &> /dev/null && ! command -v mongo &> /dev/null; then
    echo "⚠️  MongoDB no está instalado o no está en PATH"
    echo "Instálalo desde https://www.mongodb.com/try/download/community"
    echo "O en macOS: brew install mongodb-community"
    read -p "¿Continuar de todos modos? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ MongoDB encontrado"
fi

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo ""
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo ""
echo "📦 Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependencias
echo ""
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "✅ Dependencias instaladas"

# Crear .env si no existe
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creando archivo .env..."
    cat > .env << 'EOF'
# MongoDB Local
MONGODB_HOST=localhost
MONGODB_PORT=27017

# JWT
SECRET_KEY=dev-secret-key-change-in-production-min-32-chars-long-enough
JWT_SECRET_KEY=jwt-secret-key-change-in-production-min-32-chars-long-enough-too
JWT_ACCESS_TOKEN_EXPIRES=3600

# Email (para CU0016)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=test@example.com
MAIL_PASSWORD=your_app_password_here
MAIL_DEFAULT_SENDER=noreply@app.com

# CORS
CORS_ORIGINS=http://localhost:4200

# Flask
FLASK_ENV=development
PORT=5000
EOF
    echo "✅ Archivo .env creado"
    echo ""
    echo "⚠️  IMPORTANTE: Edita .env para configurar tus credenciales de email"
else
    echo "✅ Archivo .env ya existe"
fi

# Inicializar base de datos
echo ""
echo "💾 Inicializando base de datos con datos de prueba..."
python init_db.py --with-sample-data

echo ""
echo "======================================="
echo "✅ Setup completado!"
echo ""
echo "📋 Próximos pasos:"
echo ""
echo "1. Activar el entorno virtual:"
echo "   source venv/bin/activate"
echo ""
echo "2. Iniciar el backend:"
echo "   python app.py"
echo ""
echo "3. En otra terminal, configurar el frontend:"
echo "   cd ../frontend"
echo "   npm install"
echo "   npm start"
echo ""
echo "4. Abrir navegador:"
echo "   http://localhost:4200"
echo ""
echo "🧪 Para probar CU0016 (tendencias):"
echo "   python enviar_tendencias.py --test"
echo ""
echo "======================================="
