#!/bin/bash
set -e

echo "=== JALDRISTHI Vercel Build ==="

# 1. Build frontend
echo "Building frontend..."
cd frontend
npm install
npm run build
cd ..

# 2. Copy frontend build to root for Vercel static serving
echo "Copying frontend build to root..."
cp -r frontend/dist/* .

# 3. Copy backend modules to api/ for Vercel serverless function
echo "Copying backend modules to api/..."
mkdir -p api
cp backend/main.py api/
cp backend/config.py api/
cp backend/database.py api/
cp backend/parser.py api/
cp backend/geo_resolver.py api/
cp backend/query_router.py api/
cp backend/numeric_calc.py api/
cp backend/smart_chat.py api/
cp backend/rag.py api/
cp backend/auth_routes.py api/
cp backend/auth_middleware.py api/
cp backend/water_quality_routes.py api/
cp backend/supabase_client.py api/
cp backend/ingestion.py api/

# 4. Create Vercel-compatible entry point
cat > api/index.py << 'PYEOF'
import sys
import os

# Add api/ directory to path so local imports work
sys.path.insert(0, os.path.dirname(__file__))

from main import app
PYEOF

echo "=== Build complete ==="
