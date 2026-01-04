# 3D Object Generator from Prompt

A web application that generates 3D objects from text prompts or images using Microsoft's TRELLIS model. Features AI-powered prompt enhancement via Ollama (local) or Groq (cloud).

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB)
![3D](https://img.shields.io/badge/3D-TRELLIS-purple)

## Features

- **Text-to-3D Generation**: Describe any object and generate a 3D model
- **Image-to-3D Generation**: Upload an image and convert it to 3D
- **AI Prompt Enhancement**: Automatically enhance prompts using Ollama or Groq LLMs
- **Real-time Progress**: WebSocket-based live progress updates
- **3D Preview**: Interactive Three.js viewer with orbit controls
- **Multiple Export Formats**: Download as GLB or PLY
- **Self-Hosted**: Full Docker Compose setup for local deployment

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   React SPA     │────────▶│   FastAPI Server │────────▶│  GPU Worker     │
│   (Frontend)    │◀────────│   (API + WS)     │◀────────│  (TRELLIS)      │
└─────────────────┘         └──────────────────┘         └─────────────────┘
                                     │                            │
                                     ▼                            ▼
                            ┌─────────────────┐         ┌─────────────────┐
                            │  Redis Queue    │         │  File Storage   │
                            │  + Cache        │         │  (Volumes)      │
                            └─────────────────┘         └─────────────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Ollama/Groq    │
                            │  LLM Services   │
                            └─────────────────┘
```

## Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with 16GB+ VRAM (for TRELLIS generation)
- NVIDIA Container Toolkit (for GPU support)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/albertoelopez/3D-Object-from-Prompt.git
cd 3D-Object-from-Prompt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key (optional):
```
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Start services

**Development mode (no GPU required):**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

**Production mode (GPU required):**
```bash
docker-compose up --build
```

### 4. Pull Ollama model

```bash
docker exec -it trellis_ollama ollama pull llama3.2
```

### 5. Access the application

- Frontend: http://localhost (production) or http://localhost:3000 (development)
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/v1/health

## Development Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export REDIS_HOST=localhost
export OLLAMA_BASE_URL=http://localhost:11434

uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Worker (requires GPU)

```bash
cd backend
python -m app.workers.gpu_worker
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/generate/text-to-3d` | POST | Generate 3D from text |
| `/api/v1/generate/image-to-3d` | POST | Generate 3D from image |
| `/api/v1/prompts/enhance` | POST | Enhance prompt with AI |
| `/api/v1/jobs/{job_id}` | GET | Get job status |
| `/api/v1/jobs/{job_id}` | DELETE | Cancel job |
| `/api/v1/download/{job_id}.glb` | GET | Download GLB |
| `/api/v1/download/{job_id}.ply` | GET | Download PLY |
| `/api/v1/health` | GET | Health check |
| `/ws/jobs/{job_id}` | WebSocket | Real-time progress |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | redis | Redis host |
| `REDIS_PORT` | 6379 | Redis port |
| `OLLAMA_BASE_URL` | http://ollama:11434 | Ollama API URL |
| `GROQ_API_KEY` | - | Groq API key (optional) |
| `TRELLIS_DEVICE` | cuda | Device for TRELLIS (cuda/cpu) |
| `CORS_ORIGINS` | localhost:3000 | Allowed CORS origins |

### LLM Providers

**Ollama (Local)**
- Free, runs locally
- Default model: `llama3.2`
- Pull models: `docker exec -it trellis_ollama ollama pull <model>`

**Groq (Cloud)**
- Fast inference (280-1000 tokens/sec)
- Requires API key from https://console.groq.com
- Default model: `llama-3.3-70b-versatile`

## Tech Stack

### Backend
- FastAPI (Python)
- Redis (Queue + Cache)
- TRELLIS (3D Generation)
- Ollama/Groq (LLM)

### Frontend
- React 18 + TypeScript
- Vite
- Three.js / React Three Fiber
- Tailwind CSS
- Zustand (State)

### Infrastructure
- Docker + Docker Compose
- Nginx (Production)
- NVIDIA Container Toolkit

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core utilities
│   │   ├── services/      # Business logic
│   │   └── workers/       # GPU worker
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   ├── services/      # API clients
│   │   └── store/         # State management
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## License

MIT

## Acknowledgments

- [Microsoft TRELLIS](https://github.com/microsoft/TRELLIS) - 3D generation model
- [Ollama](https://ollama.ai) - Local LLM inference
- [Groq](https://groq.com) - Fast cloud LLM inference
