import { useState, useCallback } from 'react';
import { generateTextTo3D, generateImageTo3D, getJob } from '@/services/api/generation';
import { wsClient } from '@/services/websocket/client';
import { useGenerationStore, useToastStore } from '@/store';
import { TextTo3DRequest, WSMessage, Job, JobStatus } from '@/types/api';

export function useGeneration() {
  const [loading, setLoading] = useState(false);
  const {
    setCurrentJob,
    updateJobProgress,
    setJobCompleted,
    setJobFailed,
    setIsGenerating,
    setError,
  } = useGenerationStore();
  const { addToast } = useToastStore();

  const handleWebSocketMessage = useCallback(
    (message: WSMessage) => {
      switch (message.type) {
        case 'progress_update':
          updateJobProgress(
            message.progress || 0,
            message.stage || '',
            message.stage_progress || 0
          );
          break;

        case 'completion':
          if (message.result) {
            setJobCompleted(message.result);
            addToast({
              type: 'success',
              message: '3D model generated successfully! Ready to download.',
              duration: 6000,
            });
          }
          wsClient.disconnect();
          break;

        case 'error':
          setJobFailed(message.error?.message || 'Unknown error');
          addToast({
            type: 'error',
            message: `Generation failed: ${message.error?.message || 'Unknown error'}`,
            duration: 8000,
          });
          wsClient.disconnect();
          break;
      }
    },
    [updateJobProgress, setJobCompleted, setJobFailed, addToast]
  );

  const generateFromText = useCallback(
    async (request: TextTo3DRequest) => {
      setLoading(true);
      setError(null);
      setIsGenerating(true);

      try {
        const response = await generateTextTo3D(request);

        const job: Job = {
          job_id: response.job_id,
          status: response.status as JobStatus,
          progress: 0,
          stage: 'queued',
          stage_progress: 0,
          created_at: response.created_at,
          started_at: null,
          completed_at: null,
          input: {
            type: 'text',
            prompt: request.prompt,
            parameters: {},
          },
          result: null,
          error: null,
        };

        setCurrentJob(job);

        wsClient.addHandler(handleWebSocketMessage);
        wsClient.connect(response.job_id);

        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to start generation';
        setError(message);
        setIsGenerating(false);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [handleWebSocketMessage, setCurrentJob, setError, setIsGenerating]
  );

  const generateFromImage = useCallback(
    async (file: File, params: { enhance_prompt?: boolean; llm_provider?: string; resolution?: string }) => {
      setLoading(true);
      setError(null);
      setIsGenerating(true);

      try {
        const response = await generateImageTo3D(file, params);

        const job: Job = {
          job_id: response.job_id,
          status: response.status as JobStatus,
          progress: 0,
          stage: 'queued',
          stage_progress: 0,
          created_at: response.created_at,
          started_at: null,
          completed_at: null,
          input: {
            type: 'image',
            image_filename: file.name,
            parameters: {},
          },
          result: null,
          error: null,
        };

        setCurrentJob(job);

        wsClient.addHandler(handleWebSocketMessage);
        wsClient.connect(response.job_id);

        return response;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to start generation';
        setError(message);
        setIsGenerating(false);
        throw err;
      } finally {
        setLoading(false);
      }
    },
    [handleWebSocketMessage, setCurrentJob, setError, setIsGenerating]
  );

  const pollJobStatus = useCallback(
    async (jobId: string) => {
      try {
        const job = await getJob(jobId);
        setCurrentJob(job);

        if (job.status === 'completed' && job.result) {
          setJobCompleted(job.result);
        } else if (job.status === 'failed') {
          setJobFailed(job.error?.message || 'Job failed');
        }

        return job;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to get job status';
        setError(message);
        throw err;
      }
    },
    [setCurrentJob, setJobCompleted, setJobFailed, setError]
  );

  return {
    generateFromText,
    generateFromImage,
    pollJobStatus,
    loading,
  };
}
