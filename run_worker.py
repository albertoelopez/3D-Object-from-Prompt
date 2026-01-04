#!/usr/bin/env python3
import os
import sys

os.chdir('/home/darthvader/AI_Projects/create_3d_objects/backend')
sys.path.insert(0, '/home/darthvader/AI_Projects/create_3d_objects/backend')

os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
os.environ['TRELLIS_DEVICE'] = 'cuda'
os.environ['STORAGE_PATH'] = '/tmp/trellis_storage'
os.environ['UPLOADS_PATH'] = '/tmp/trellis_storage/uploads'
os.environ['OUTPUTS_PATH'] = '/tmp/trellis_storage/outputs'
os.environ['PREVIEWS_PATH'] = '/tmp/trellis_storage/previews'

print("Starting GPU worker with TRELLIS...")
print(f"TRELLIS_DEVICE: {os.environ['TRELLIS_DEVICE']}")

import asyncio
from app.workers.gpu_worker import main

asyncio.run(main())
