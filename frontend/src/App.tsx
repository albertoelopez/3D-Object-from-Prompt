import { Layout } from '@/components/layout/Layout';
import { GenerationForm } from '@/components/generation/GenerationForm';
import { ModelViewer } from '@/components/viewer/ModelViewer';
import { ProgressTracker } from '@/components/progress/ProgressTracker';
import { useGenerationStore } from '@/store';

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
    </Layout>
  );
}

export default App;
