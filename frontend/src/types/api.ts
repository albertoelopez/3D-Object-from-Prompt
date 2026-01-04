export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
export type InputType = 'text' | 'image';
export type Resolution = 'low' | 'medium' | 'high';
export type LLMProvider = 'ollama' | 'groq';

export interface SamplerParams {
  steps: number;
  cfg_strength: number;
}

export interface TextTo3DRequest {
  prompt: string;
  enhance_prompt?: boolean;
  llm_provider?: LLMProvider;
  seed?: number;
  resolution?: Resolution;
  sparse_structure_sampler_params?: SamplerParams;
  slat_sampler_params?: SamplerParams;
}

export interface GenerationResponse {
  job_id: string;
  status: JobStatus;
  created_at: string;
  estimated_time: number;
  websocket_url: string;
}

export interface JobResult {
  glb_url: string | null;
  ply_url: string | null;
  preview_url: string | null;
  file_sizes: {
    glb: number;
    ply: number;
  };
}

export interface JobError {
  code: string;
  message: string;
  recoverable: boolean;
}

export interface Job {
  job_id: string;
  status: JobStatus;
  progress: number;
  stage: string | null;
  stage_progress: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  input: {
    type: InputType;
    prompt?: string;
    enhanced_prompt?: string;
    image_filename?: string;
    parameters: Record<string, unknown>;
  } | null;
  result: JobResult | null;
  error: JobError | null;
}

export interface PromptEnhanceRequest {
  prompt: string;
  provider: LLMProvider;
  model?: string;
}

export interface PromptEnhanceResponse {
  original_prompt: string;
  enhanced_prompt: string;
  provider: string;
  model_used: string;
}

export interface HealthResponse {
  status: string;
  services: {
    api: string;
    redis: string;
    ollama: string;
    groq: string;
  };
  queue: {
    pending: number;
    processing: number;
    workers_available: number;
  };
}

export interface WSMessage {
  type: 'connected' | 'status_update' | 'progress_update' | 'stage_complete' | 'completion' | 'error' | 'pong';
  job_id: string;
  timestamp: string;
  status?: JobStatus;
  progress?: number;
  stage?: string;
  stage_progress?: number;
  message?: string;
  result?: JobResult;
  error?: JobError;
}
