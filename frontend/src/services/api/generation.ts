import apiClient from './client';
import { TextTo3DRequest, GenerationResponse, Job, PromptEnhanceRequest, PromptEnhanceResponse } from '@/types/api';

export async function generateTextTo3D(request: TextTo3DRequest): Promise<GenerationResponse> {
  const response = await apiClient.post<GenerationResponse>('/generate/text-to-3d', request);
  return response.data;
}

export async function generateImageTo3D(
  file: File,
  params: {
    enhance_prompt?: boolean;
    llm_provider?: string;
    seed?: number;
    resolution?: string;
  }
): Promise<GenerationResponse> {
  const formData = new FormData();
  formData.append('file', file);

  if (params.enhance_prompt !== undefined) {
    formData.append('enhance_prompt', String(params.enhance_prompt));
  }
  if (params.llm_provider) {
    formData.append('llm_provider', params.llm_provider);
  }
  if (params.seed !== undefined) {
    formData.append('seed', String(params.seed));
  }
  if (params.resolution) {
    formData.append('resolution', params.resolution);
  }

  const response = await apiClient.post<GenerationResponse>('/generate/image-to-3d', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getJob(jobId: string): Promise<Job> {
  const response = await apiClient.get<Job>(`/jobs/${jobId}`);
  return response.data;
}

export async function cancelJob(jobId: string): Promise<void> {
  await apiClient.delete(`/jobs/${jobId}`);
}

export async function enhancePrompt(request: PromptEnhanceRequest): Promise<PromptEnhanceResponse> {
  const response = await apiClient.post<PromptEnhanceResponse>('/prompts/enhance', request);
  return response.data;
}

export function getDownloadUrl(jobId: string, type: 'glb' | 'ply'): string {
  const baseUrl = import.meta.env.VITE_API_URL || '';
  return `${baseUrl}/api/v1/download/${jobId}.${type}`;
}

export function getPreviewUrl(jobId: string): string {
  const baseUrl = import.meta.env.VITE_API_URL || '';
  return `${baseUrl}/api/v1/download/preview/${jobId}.png`;
}
