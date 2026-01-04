#!/bin/bash
cd /home/darthvader/AI_Projects/create_3d_objects/backend

export PYTHONPATH="/home/darthvader/AI_Projects/create_3d_objects/backend:/home/darthvader/AI_Projects/create_3d_objects/TRELLIS"
export REDIS_HOST=localhost
export REDIS_PORT=6379
export OLLAMA_BASE_URL=http://localhost:11434
export TRELLIS_DEVICE=cuda
export STORAGE_PATH=/tmp/trellis_storage
export UPLOADS_PATH=/tmp/trellis_storage/uploads
export OUTPUTS_PATH=/tmp/trellis_storage/outputs
export PREVIEWS_PATH=/tmp/trellis_storage/previews

echo "Starting GPU worker with TRELLIS..."
echo "PYTHONPATH: $PYTHONPATH"
python3 -m app.workers.gpu_worker
