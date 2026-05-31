#!/bin/bash

set -e

PROJECT_ROOT=$(pwd)

BACKEND="$PROJECT_ROOT/backend"
FRONTEND="$PROJECT_ROOT/frontend"

#
# =====================================
# Models
# =====================================
#

OLLAMA_MODEL="qwen2.5:7b-instruct-q4_K_M"

EMBED_MODEL="intfloat/multilingual-e5-small"


echo ""
echo "======================================"
echo "🚀 Starting APGovAI"
echo "======================================"
echo ""


########################################
# Backend Setup
########################################

cd "$BACKEND"


#
# Create virtual environment
#

if [ ! -d "venv" ]; then

echo "📦 Creating Python virtual environment..."

python3 -m venv venv

fi


#
# Activate environment
#

echo "⚡ Activating environment..."

source venv/bin/activate


#
# Upgrade pip
#

python -m pip install --upgrade pip -q


#
# Install dependencies
#

echo ""
echo "📥 Installing backend dependencies..."
echo ""

pip install -q -r requirements.txt


#
# Formatter
#

echo ""
echo "🧹 Formatting backend..."
echo ""

black app || true


########################################
# Verify Required Commands
########################################

echo ""
echo "🔍 Checking required tools..."
echo ""

REQUIRED_COMMANDS=(

docker
ollama
python3
npm
tesseract

)

for cmd in "${REQUIRED_COMMANDS[@]}"
do

if ! command -v $cmd &> /dev/null
then

echo "❌ Missing dependency: $cmd"

exit 1

fi

done

echo "✅ Required tools available"


########################################
# Infrastructure
########################################

echo ""
echo "🐳 Starting Infrastructure..."
echo ""

docker compose up -d

echo ""
echo "⏳ Waiting for services..."
echo ""

sleep 10

#
# PostgreSQL
#

if ! docker ps | grep apgovai-postgres >/dev/null
then

echo "❌ PostgreSQL failed to start"

exit 1

fi

echo "✅ PostgreSQL running"


#
# Redis
#

if ! docker ps | grep apgovai-redis >/dev/null
then

echo "❌ Redis failed to start"

exit 1

fi

echo "✅ Redis running"


#
# Qdrant
#

if ! docker ps | grep apgovai-qdrant >/dev/null
then

echo "❌ Qdrant failed to start"

exit 1

fi

echo "✅ Qdrant running"


########################################
# Ollama
########################################

echo ""
echo "🤖 Checking Ollama..."
echo ""

if ! pgrep -x "ollama" >/dev/null
then

echo "🚀 Starting Ollama..."

nohup ollama serve \
>/tmp/ollama.log \
2>&1 &

sleep 10

fi

echo "✅ Ollama running"


########################################
# Pull LLM Model
########################################

echo ""
echo "📦 Checking LLM model..."
echo ""

if ollama list | grep "$OLLAMA_MODEL" >/dev/null
then

echo "✅ Model already exists"

else

echo "⬇️ Pulling model: $OLLAMA_MODEL"

ollama pull "$OLLAMA_MODEL"

fi


########################################
# Warm Embedding Model
########################################

echo ""
echo "🧠 Warming embedding model..."
echo ""

python -c "
from sentence_transformers import SentenceTransformer

print('Loading embeddings: $EMBED_MODEL')

SentenceTransformer(
    '$EMBED_MODEL',
    device='cpu'
)

print('✅ Embedding model ready')
"


########################################
# Verify OCR Telugu Support
########################################

echo ""
echo "🔍 Checking OCR Telugu support..."
echo ""

if ! tesseract --list-langs | grep tel >/dev/null
then

echo "❌ Telugu OCR data missing"

echo ""
echo "Install using:"
echo ""

echo "sudo apt install tesseract-ocr-tel"

exit 1

fi

echo "✅ Telugu OCR available"


########################################
# Incremental Ingestion
########################################

echo ""
echo "📚 Checking document updates..."
echo ""

PYTHONPATH=. python app/ingestion/registry.py

echo "✅ Ingestion completed"


########################################
# Frontend Setup
########################################

cd "$FRONTEND"

echo ""
echo "📥 Installing frontend dependencies..."
echo ""

npm install


########################################
# Kill Existing Ports
########################################

echo ""
echo "🧹 Cleaning old processes..."
echo ""

fuser -k 8000/tcp >/dev/null 2>&1 || true
fuser -k 5173/tcp >/dev/null 2>&1 || true


########################################
# Start Backend
########################################

echo ""
echo "🔥 Starting backend..."
echo ""

gnome-terminal \
-- bash \
-c "
cd $BACKEND

source venv/bin/activate

PYTHONPATH=. uvicorn app.main:app \
--host 0.0.0.0 \
--port 8000 \
--reload

exec bash
"


########################################
# Wait Backend
########################################

sleep 5


########################################
# Start Frontend
########################################

echo ""
echo "🔥 Starting frontend..."
echo ""

gnome-terminal \
-- bash \
-c "
cd $FRONTEND

npm run dev

exec bash
"


########################################
# Final Status
########################################

echo ""
echo "======================================"
echo "✅ APGovAI Started Successfully"
echo "======================================"
echo ""

echo "Frontend:"
echo "http://localhost:5173"
echo ""

echo "Backend:"
echo "http://localhost:8000"
echo ""

echo "LLM:"
echo "$OLLAMA_MODEL"
echo ""

echo "Embeddings:"
echo "$EMBED_MODEL"
echo ""

echo "PostgreSQL:"
echo "localhost:5432"
echo ""

echo "Redis:"
echo "localhost:6379"
echo ""

echo "Qdrant:"
echo "http://localhost:6333"
echo ""

echo "OCR:"
echo "Tesseract (eng + tel)"
echo ""

echo "Vector DB:"
echo "Qdrant"
echo ""

echo "======================================"
echo ""