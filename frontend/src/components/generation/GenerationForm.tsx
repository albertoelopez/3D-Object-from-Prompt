import { useState } from 'react';
import { Type, Image, Sparkles, Settings } from 'lucide-react';
import { TextInput } from './TextInput';
import { ImageUpload } from './ImageUpload';
import { ParametersPanel } from './ParametersPanel';
import { useGeneration } from '@/hooks/useGeneration';
import { useGenerationStore, useUIStore } from '@/store';
import { LLMProvider, Resolution } from '@/types/api';

export function GenerationForm() {
  const { activeTab, setActiveTab, showAdvancedOptions, setShowAdvancedOptions } = useUIStore();
  const { isGenerating } = useGenerationStore();
  const { generateFromText, generateFromImage, loading } = useGeneration();

  const [prompt, setPrompt] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [enhancePrompt, setEnhancePrompt] = useState(true);
  const [llmProvider, setLlmProvider] = useState<LLMProvider>('ollama');
  const [resolution, setResolution] = useState<Resolution>('medium');
  const [seed, setSeed] = useState<number | undefined>(undefined);

  const handleSubmit = async () => {
    if (activeTab === 'text') {
      if (!prompt.trim()) return;

      await generateFromText({
        prompt: prompt.trim(),
        enhance_prompt: enhancePrompt,
        llm_provider: llmProvider,
        resolution,
        seed,
      });
    } else {
      if (!imageFile) return;

      await generateFromImage(imageFile, {
        enhance_prompt: enhancePrompt,
        llm_provider: llmProvider,
        resolution,
      });
    }
  };

  const isSubmitDisabled = loading || isGenerating || (activeTab === 'text' ? !prompt.trim() : !imageFile);

  return (
    <div className="glass rounded-xl p-6 space-y-6">
      <div className="flex gap-2">
        <button
          onClick={() => setActiveTab('text')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg transition-all ${
            activeTab === 'text'
              ? 'bg-primary-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <Type className="w-5 h-5" />
          Text to 3D
        </button>
        <button
          onClick={() => setActiveTab('image')}
          className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-lg transition-all ${
            activeTab === 'image'
              ? 'bg-primary-600 text-white'
              : 'bg-white/5 text-gray-400 hover:bg-white/10'
          }`}
        >
          <Image className="w-5 h-5" />
          Image to 3D
        </button>
      </div>

      <div className="space-y-4">
        {activeTab === 'text' ? (
          <TextInput value={prompt} onChange={setPrompt} disabled={isGenerating} />
        ) : (
          <ImageUpload file={imageFile} onFileChange={setImageFile} disabled={isGenerating} />
        )}

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={enhancePrompt}
              onChange={(e) => setEnhancePrompt(e.target.checked)}
              disabled={isGenerating}
              className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-primary-600 focus:ring-primary-500"
            />
            <Sparkles className="w-4 h-4 text-primary-400" />
            <span className="text-sm text-gray-300">Enhance prompt with AI</span>
          </label>

          <button
            onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
            className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors"
          >
            <Settings className="w-4 h-4" />
            Advanced
          </button>
        </div>

        {showAdvancedOptions && (
          <ParametersPanel
            llmProvider={llmProvider}
            onLlmProviderChange={setLlmProvider}
            resolution={resolution}
            onResolutionChange={setResolution}
            seed={seed}
            onSeedChange={setSeed}
            disabled={isGenerating}
          />
        )}
      </div>

      <button
        onClick={handleSubmit}
        disabled={isSubmitDisabled}
        className={`w-full py-4 px-6 rounded-lg font-semibold text-lg transition-all ${
          isSubmitDisabled
            ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-500 hover:to-purple-500 text-white shadow-lg hover:shadow-primary-500/25'
        }`}
      >
        {loading || isGenerating ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Generating...
          </span>
        ) : (
          'Generate 3D Model'
        )}
      </button>
    </div>
  );
}
