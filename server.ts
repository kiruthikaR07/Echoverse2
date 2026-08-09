import express from "express";
import path from "path";
import { spawn } from "child_process";
import { createServer as createViteServer } from "vite";

const app = express();
const PORT = 3000;
const PYTHON_PORT = 8085;

app.use(express.json());

// Spawn Python Interview Backend Service
let pythonProcess: any = null;

function startPythonBackend() {
  console.log("[Server] Spawning Python Interview Engine on port", PYTHON_PORT);
  const env = { ...process.env, PYTHON_PORT: String(PYTHON_PORT), PYTHONPATH: process.cwd() };
  
  pythonProcess = spawn("python3", ["backend/app/main.py"], {
    env,
    stdio: ["pipe", "pipe", "pipe"],
  });

  pythonProcess.stdout.on("data", (data: Buffer) => {
    console.log(`[Python Engine] ${data.toString().trim()}`);
  });

  pythonProcess.stderr.on("data", (data: Buffer) => {
    console.error(`[Python Engine Error] ${data.toString().trim()}`);
  });

  pythonProcess.on("close", (code: number) => {
    console.log(`[Python Engine] Exited with code ${code}. Restarting...`);
    setTimeout(startPythonBackend, 2000);
  });
}

startPythonBackend();

// Helper to forward HTTP requests to Python service with retry logic
async function forwardToPython(reqPath: string, method: string, body?: any) {
  const url = `http://127.0.0.1:${PYTHON_PORT}${reqPath}`;
  const options: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };
  if (body) {
    options.body = JSON.stringify(body);
  }

  let lastError: any = null;
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Python API Error (${response.status}): ${errText}`);
      }
      return await response.json();
    } catch (err) {
      lastError = err;
      await new Promise((resolve) => setTimeout(resolve, 500));
    }
  }

  throw lastError || new Error("Failed to connect to Python backend after retries");
}

// API Routes
app.get("/health", async (req, res) => {
  res.json({ status: "ok" });
});

app.get("/api/health", async (req, res) => {
  try {
    const data = await forwardToPython("/api/health", "GET");
    res.json({ ...data, express: "ok" });
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/candidates", async (req, res) => {
  try {
    const data = await forwardToPython("/api/candidates", "GET");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.get("/api/curriculum", async (req, res) => {
  try {
    const data = await forwardToPython("/api/curriculum", "GET");
    res.json(data);
  } catch (err: any) {
    res.status(500).json({ error: err.message });
  }
});

app.post("/api/interview", async (req, res) => {
  try {
    const data = await forwardToPython("/api/interview", "POST", req.body);
    res.json(data);
  } catch (err: any) {
    console.error("[Express API Error]", err);
    res.status(500).json({ error: err.message || "Interview turn failed" });
  }
});

// Setup Vite Development / Static Middleware
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`[Server] Adaptive AI Interviewer running on http://0.0.0.0:${PORT}`);
  });
}

startServer();

// Clean up child process on shutdown
process.on("exit", () => {
  if (pythonProcess) pythonProcess.kill();
});
