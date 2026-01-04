import { create } from 'zustand';
import { Job, JobStatus, JobResult } from '@/types/api';

interface GenerationState {
  currentJob: Job | null;
  isGenerating: boolean;
  error: string | null;

  setCurrentJob: (job: Job | null) => void;
  updateJobProgress: (progress: number, stage: string, stageProgress: number) => void;
  setJobCompleted: (result: JobResult) => void;
  setJobFailed: (error: string) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useGenerationStore = create<GenerationState>((set) => ({
  currentJob: null,
  isGenerating: false,
  error: null,

  setCurrentJob: (job) => set({ currentJob: job, error: null }),

  updateJobProgress: (progress, stage, stageProgress) =>
    set((state) => ({
      currentJob: state.currentJob
        ? { ...state.currentJob, progress, stage, stage_progress: stageProgress }
        : null,
    })),

  setJobCompleted: (result) =>
    set((state) => ({
      currentJob: state.currentJob
        ? { ...state.currentJob, status: 'completed' as JobStatus, result, progress: 100 }
        : null,
      isGenerating: false,
    })),

  setJobFailed: (error) =>
    set((state) => ({
      currentJob: state.currentJob
        ? {
            ...state.currentJob,
            status: 'failed' as JobStatus,
            error: { code: 'ERROR', message: error, recoverable: false },
          }
        : null,
      isGenerating: false,
      error,
    })),

  setIsGenerating: (isGenerating) => set({ isGenerating }),

  setError: (error) => set({ error }),

  reset: () => set({ currentJob: null, isGenerating: false, error: null }),
}));

interface UIState {
  activeTab: 'text' | 'image';
  showAdvancedOptions: boolean;

  setActiveTab: (tab: 'text' | 'image') => void;
  setShowAdvancedOptions: (show: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  activeTab: 'text',
  showAdvancedOptions: false,

  setActiveTab: (tab) => set({ activeTab: tab }),
  setShowAdvancedOptions: (show) => set({ showAdvancedOptions: show }),
}));

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  message: string;
  duration?: number;
}

interface ToastState {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newToast = { ...toast, id };

    set((state) => ({ toasts: [...state.toasts, newToast] }));

    const duration = toast.duration ?? 5000;
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },

  removeToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),
}));
