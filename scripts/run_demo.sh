#!/usr/bin/env bash
# ==============================================================================
# eRTMAC-NWIS One-Command Live Demonstration Launcher
# Smart India Hackathon 2026 · Problem Statement SIH26121 · Oil India Limited
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "======================================================================"
echo "  🚀 Starting OIL eRTMAC-NWIS Demonstration Platform"
echo "  Problem Statement: SIH26121 · Oil India Limited"
echo "  Design Language: Palette 1 (Assam Crude & Industrial Amber)"
echo "======================================================================"

# Check Python environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

# Trap Ctrl+C to cleanly kill both processes
cleanup() {
    echo ""
    echo "🛑 Shutting down eRTMAC-NWIS services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    echo "✓ All services stopped cleanly."
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 1. Start FastAPI Backend
echo "📡 Launching FastAPI Backend on http://localhost:8000..."
cd "$DIR/backend"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$DIR/backend.log" 2>&1 &
BACKEND_PID=$!
cd "$DIR"

# Wait for backend health check
echo "⏳ Waiting for backend health check..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        echo "✓ FastAPI Backend is healthy and responding!"
        break
    fi
    sleep 0.5
done

# 2. Start Next.js Frontend
echo "💻 Launching Next.js Industrial Dashboard on http://localhost:3000..."
cd "$DIR/frontend"
npm run dev -- -p 3000 > "$DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
cd "$DIR"

# Wait for frontend
echo "⏳ Waiting for frontend server..."
for i in {1..30}; do
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✓ Next.js Frontend is live at http://localhost:3000!"
        break
    fi
    sleep 0.5
done

echo ""
echo "======================================================================"
echo "  ✅ eRTMAC-NWIS LIVE SYSTEM IS OPERATIONAL"
echo "  ------------------------------------------------------------------"
echo "  🌐 Dashboard URL:    http://localhost:3000"
echo "  📡 API Docs / Swag:  http://localhost:8000/docs"
echo "  📊 Presentation:     $DIR/presentations/SIH26121_eRTMAC_NWIS_Official_Deck.pptx"
echo "  📄 Tour Advisory PDF: http://localhost:8000/api/v1/reports/tour-advisory"
echo "======================================================================"
echo "Press Ctrl+C to shut down all servers."

# Keep alive
wait $BACKEND_PID $FRONTEND_PID
