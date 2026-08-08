"""
Main FastAPI Backend Server.
Exposes POST /api/interview, GET /api/candidates, GET /api/curriculum.
Also includes a fallback HTTP runner for standalone execution.
"""

import os
import json
import sys
from typing import Dict, Any

# Ensure project root & app dir are in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from backend.app.schemas import InterviewRequest, InterviewResponse
    from backend.app.interview_engine import (
        process_interview_turn,
        get_candidates,
        get_curriculum
    )
except ImportError:
    from app.schemas import InterviewRequest, InterviewResponse
    from app.interview_engine import (
        process_interview_turn,
        get_candidates,
        get_curriculum
    )

# Optional FastAPI integration
try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI(
        title="Adaptive AI Interviewer API",
        description="Backend service for 31-day Enterprise AI Engineering Cohort Interviewer",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health_check():
        return {"status": "ok", "service": "adaptive-ai-interviewer"}

    @app.get("/api/candidates")
    def list_candidates():
        return get_candidates()

    @app.get("/api/curriculum")
    def list_curriculum():
        return get_curriculum()

    @app.post("/api/interview", response_model=InterviewResponse)
    def handle_interview(req: InterviewRequest):
        try:
            messages_list = [m.model_dump() for m in req.messages] if req.messages else []
            res = process_interview_turn(
                session_id=req.sessionId,
                candidate_data=req.candidate,
                messages=messages_list
            )
            return res
        except Exception as e:
            print(f"Error processing interview turn: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

except ImportError:
    app = None


# Standalone Standard Library HTTP Server Fallback
if __name__ == "__main__":
    import http.server
    import socketserver
    
    PORT = int(os.environ.get("PYTHON_PORT", "8000"))
    
    class InterviewHTTPHandler(http.server.BaseHTTPRequestHandler):
        def _send_json(self, status: int, payload: Any):
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode("utf-8"))

        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def log_message(self, format, *args):
            sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
            sys.stdout.flush()

        def do_GET(self):
            if self.path == "/api/health":
                self._send_json(200, {"status": "ok", "service": "adaptive-ai-interviewer"})
            elif self.path == "/api/candidates":
                self._send_json(200, get_candidates())
            elif self.path == "/api/curriculum":
                self._send_json(200, get_curriculum())
            else:
                self._send_json(404, {"error": "Not Found"})

        def do_POST(self):
            if self.path == "/api/interview":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length).decode("utf-8")
                try:
                    data = json.loads(body)
                    session_id = data.get("sessionId", "session_default")
                    candidate = data.get("candidate", {})
                    messages = data.get("messages", [])
                    
                    res = process_interview_turn(session_id, candidate, messages)
                    self._send_json(200, res)
                except Exception as e:
                    print(f"Server Error: {str(e)}")
                    self._send_json(500, {"error": str(e)})
            else:
                self._send_json(404, {"error": "Not Found"})

    class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True

    print(f"Starting Python HTTP Interview Service on port {PORT}...")
    with ThreadedHTTPServer(("0.0.0.0", PORT), InterviewHTTPHandler) as httpd:
        httpd.serve_forever()
