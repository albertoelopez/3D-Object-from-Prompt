import { Suspense, useRef, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Center, Html } from '@react-three/drei';
import { Download, RotateCcw } from 'lucide-react';
import { useGenerationStore } from '@/store';
import { getDownloadUrl } from '@/services/api/generation';
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

export function ModelViewer() {
  const { currentJob } = useGenerationStore();
  const hasModel = currentJob?.status === 'completed' && currentJob.result;

  const handleDownload = (type: 'glb' | 'ply') => {
    if (!currentJob) return;
    const url = getDownloadUrl(currentJob.job_id, type);
    const link = document.createElement('a');
    link.href = url;
    link.download = `model.${type}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
