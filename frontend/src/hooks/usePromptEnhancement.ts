import { useState, useCallback } from 'react';
import { enhancePrompt } from '@/services/api/generation';
import { LLMProvider } from '@/types/api';

export function usePromptEnhancement() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const enhance = useCallback(
    async (prompt: string, provider: LLMProvider = 'ollama') => {
      setLoading(true);
      setError(null);

      try {
        const response = await enhancePrompt({ prompt, provider });
        return response.enhanced_prompt;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to enhance prompt';
        setError(message);
        return prompt;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return {
    enhance,
    loading,
    error,
  };
}
