import { Layout } from '@/components/layout/Layout';
import { GenerationForm } from '@/components/generation/GenerationForm';
import { ModelViewer } from '@/components/viewer/ModelViewer';
import { ProgressTracker } from '@/components/progress/ProgressTracker';
import { useGenerationStore, useToastStore } from '@/store';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';

function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg backdrop-blur-md border transition-all animate-slide-in ${
            toast.type === 'success'
              ? 'bg-green-500/20 border-green-500/30 text-green-100'
              : toast.type === 'error'
              ? 'bg-red-500/20 border-red-500/30 text-red-100'
              : 'bg-blue-500/20 border-blue-500/30 text-blue-100'
          }`}
        >
          {toast.type === 'success' && <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />}
          {toast.type === 'error' && <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />}
          {toast.type === 'info' && <Info className="w-5 h-5 text-blue-400 flex-shrink-0" />}
          <span className="text-sm font-medium">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="ml-2 p-1 hover:bg-white/10 rounded transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ))}
    </div>
  );
}

function App() {
  const { currentJob, isGenerating } = useGenerationStore();

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
        <div className="flex flex-col gap-6">
          <GenerationForm />

          {(isGenerating || currentJob) && (
            <ProgressTracker />
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div className="glass rounded-xl p-4 flex-1 min-h-[500px]">
            <ModelViewer />
          </div>
        </div>
      </div>
      <ToastContainer />
    </Layout>
  );
}

export default App;
