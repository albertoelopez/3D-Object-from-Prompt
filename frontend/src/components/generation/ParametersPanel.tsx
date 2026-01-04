import { LLMProvider, Resolution } from '@/types/api';

interface ParametersPanelProps {
  llmProvider: LLMProvider;
  onLlmProviderChange: (provider: LLMProvider) => void;
  resolution: Resolution;
  onResolutionChange: (resolution: Resolution) => void;
  seed?: number;
  onSeedChange: (seed: number | undefined) => void;
  disabled?: boolean;
}

export function ParametersPanel({
  llmProvider,
  onLlmProviderChange,
  resolution,
  onResolutionChange,
  seed,
  onSeedChange,
  disabled,
}: ParametersPanelProps) {
  return (
    <div className="p-4 bg-black/20 rounded-lg space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            AI Provider
          </label>
          <select
            value={llmProvider}
            onChange={(e) => onLlmProviderChange(e.target.value as LLMProvider)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="ollama">Ollama (Local)</option>
            <option value="groq">Groq (Cloud)</option>
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-300">
            Resolution
          </label>
          <select
            value={resolution}
            onChange={(e) => onResolutionChange(e.target.value as Resolution)}
            disabled={disabled}
            className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
          >
            <option value="low">Low (Fast)</option>
            <option value="medium">Medium (Balanced)</option>
            <option value="high">High (Quality)</option>
          </select>
        </div>
      </div>

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-300">
          Seed (optional)
        </label>
        <input
          type="number"
          value={seed ?? ''}
          onChange={(e) =>
            onSeedChange(e.target.value ? parseInt(e.target.value, 10) : undefined)
          }
          disabled={disabled}
          placeholder="Random"
          className="w-full px-3 py-2 bg-black/30 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 disabled:opacity-50"
        />
        <p className="text-xs text-gray-500">
          Use a seed for reproducible results
        </p>
      </div>
    </div>
  );
}
