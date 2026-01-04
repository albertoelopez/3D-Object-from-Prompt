import { useGenerationStore } from '@/store';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';

const stageLabels: Record<string, string> = {
  queued: 'Waiting in queue...',
  initializing: 'Initializing...',
  enhancing_prompt: 'Enhancing prompt with AI...',
  loading_image: 'Loading image...',
  preprocessing: 'Preprocessing input...',
  preparing_prompt: 'Preparing prompt...',
  generating_sparse_structure: 'Generating 3D structure...',
  generating_slat: 'Generating details...',
  exporting: 'Exporting model...',
  exporting_glb: 'Exporting GLB...',
  exporting_ply: 'Exporting PLY...',
  generating_preview: 'Generating preview...',
  finalizing: 'Finalizing...',
  completed: 'Completed!',
};

export function ProgressTracker() {
  const { currentJob, error } = useGenerationStore();

  if (!currentJob) return null;

  const status = currentJob.status;
  const progress = currentJob.progress;
  const stage = currentJob.stage || 'queued';
  const stageLabel = stageLabels[stage] || stage;

  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const isProcessing = status === 'processing' || status === 'queued';

  return (
    <div className="glass rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-white">Generation Progress</h3>
        <div className="flex items-center gap-2">
          {isCompleted && <CheckCircle className="w-5 h-5 text-green-400" />}
          {isFailed && <XCircle className="w-5 h-5 text-red-400" />}
          {isProcessing && <Loader2 className="w-5 h-5 text-primary-400 animate-spin" />}
          <span
            className={`text-sm font-medium ${
              isCompleted ? 'text-green-400' : isFailed ? 'text-red-400' : 'text-primary-400'
            }`}
          >
            {progress}%
          </span>
        </div>
      </div>

      <div className="space-y-2">
        <div className="h-2 bg-black/30 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ease-out ${
              isCompleted
                ? 'bg-green-500'
                : isFailed
                ? 'bg-red-500'
                : 'bg-gradient-to-r from-primary-500 to-purple-500'
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className="text-sm text-gray-400">{stageLabel}</p>
      </div>

      {isFailed && error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
