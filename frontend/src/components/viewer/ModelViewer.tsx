import { Suspense, useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Center, Html } from '@react-three/drei';
import { Download, RotateCcw } from 'lucide-react';
import { useGenerationStore } from '@/store';
import { getDownloadUrl } from '@/services/api/generation';
import { Job } from '@/types/api';
import * as THREE from 'three';

function Model({ url }: { url: string }) {
  const { scene } = useGLTF(url);
  const ref = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
    }
  });

  return (
    <Center>
      <primitive ref={ref} object={scene} scale={2} />
    </Center>
  );
}

function LoadingPlaceholder() {
  return (
    <Html center>
      <div className="flex flex-col items-center gap-4 text-center">
        <div className="w-16 h-16 border-4 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
        <p className="text-white text-sm">Loading model...</p>
      </div>
    </Html>
  );
}

function EmptyState() {
  return (
    <Html center>
      <div className="flex flex-col items-center gap-4 text-center max-w-xs">
        <div className="w-24 h-24 rounded-full bg-white/5 flex items-center justify-center">
          <RotateCcw className="w-10 h-10 text-gray-500" />
        </div>
        <div>
          <p className="text-white font-medium">No model yet</p>
          <p className="text-gray-400 text-sm mt-1">
            Generate a 3D model to see it here
          </p>
        </div>
      </div>
    </Html>
  );
}

function Scene() {
  const { currentJob } = useGenerationStore();
  const hasModel = currentJob?.status === 'completed' && currentJob.result?.glb_url;
  const modelUrl = hasModel ? getDownloadUrl(currentJob!.job_id, 'glb') : null;

  return (
    <>
      <ambientLight intensity={0.5} />
      <directionalLight position={[10, 10, 5]} intensity={1} />
      <Environment preset="studio" />
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={1}
        maxDistance={20}
      />

      {modelUrl ? (
        <Suspense fallback={<LoadingPlaceholder />}>
          <Model url={modelUrl} />
        </Suspense>
      ) : (
        <EmptyState />
      )}
    </>
  );
}

function sanitizeFilename(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .replace(/\s+/g, '_')
    .substring(0, 50);
}

function generateFilename(job: Job | null, type: 'glb' | 'ply'): string {
  if (!job?.input) return `model.${type}`;

  const timestamp = new Date().toISOString().slice(0, 10);

  if (job.input.type === 'text' && job.input.prompt) {
    const promptSlug = sanitizeFilename(job.input.prompt);
    return `${promptSlug}_${timestamp}.${type}`;
  }

  if (job.input.type === 'image' && job.input.image_filename) {
    const imageName = job.input.image_filename.replace(/\.[^/.]+$/, '');
    const imageSlug = sanitizeFilename(imageName);
    return `${imageSlug}_3d_${timestamp}.${type}`;
  }

  return `model_${timestamp}.${type}`;
}

export function ModelViewer() {
  const { currentJob } = useGenerationStore();
  const hasModel = currentJob?.status === 'completed' && currentJob.result;

  const handleDownload = async (type: 'glb' | 'ply') => {
    if (!currentJob) return;

    const url = getDownloadUrl(currentJob.job_id, type);
    const filename = generateFilename(currentJob, type);

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();

      if ('showSaveFilePicker' in window) {
        try {
          const mimeType = type === 'glb' ? 'model/gltf-binary' : 'application/x-ply';
          const handle = await (window as unknown as { showSaveFilePicker: (options: { suggestedName: string; types: Array<{ description: string; accept: Record<string, string[]> }> }) => Promise<FileSystemFileHandle> }).showSaveFilePicker({
            suggestedName: filename,
            types: [{
              description: `3D Model (${type.toUpperCase()})`,
              accept: { [mimeType]: [`.${type}`] }
            }]
          });
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
          return;
        } catch (err) {
          if ((err as Error).name === 'AbortError') return;
        }
      }

      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Download error:', error);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-white">3D Preview</h3>
        {hasModel && (
          <div className="flex gap-2">
            <button
              onClick={() => handleDownload('glb')}
              className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 hover:bg-primary-500 text-white text-sm rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              GLB
            </button>
            <button
              onClick={() => handleDownload('ply')}
              className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors"
            >
              <Download className="w-4 h-4" />
              PLY
            </button>
          </div>
        )}
      </div>

      <div className="flex-1 rounded-lg overflow-hidden bg-gradient-to-b from-gray-900 to-black">
        <Canvas
          camera={{ position: [0, 0, 5], fov: 50 }}
          style={{ width: '100%', height: '100%' }}
        >
          <Scene />
        </Canvas>
      </div>

      <p className="text-xs text-gray-500 mt-2 text-center">
        Drag to rotate • Scroll to zoom • Right-click to pan
      </p>
    </div>
  );
}
