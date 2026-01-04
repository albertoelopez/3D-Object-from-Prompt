import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useGeneration } from '@/hooks/useGeneration'

vi.mock('@/services/api/generation', () => ({
  generateTextTo3D: vi.fn(),
  generateImageTo3D: vi.fn(),
  getJob: vi.fn(),
}))

vi.mock('@/services/websocket/client', () => ({
  wsClient: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    addHandler: vi.fn(),
    removeHandler: vi.fn(),
  },
}))

vi.mock('@/store', () => ({
  useGenerationStore: () => ({
    setCurrentJob: vi.fn(),
    updateJobProgress: vi.fn(),
    setJobCompleted: vi.fn(),
    setJobFailed: vi.fn(),
    setIsGenerating: vi.fn(),
    setError: vi.fn(),
  }),
}))

describe('useGeneration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with loading false', () => {
    const { result } = renderHook(() => useGeneration())

    expect(result.current.loading).toBe(false)
  })

  it('provides generateFromText function', () => {
    const { result } = renderHook(() => useGeneration())

    expect(typeof result.current.generateFromText).toBe('function')
  })

  it('provides generateFromImage function', () => {
    const { result } = renderHook(() => useGeneration())

    expect(typeof result.current.generateFromImage).toBe('function')
  })

  it('provides pollJobStatus function', () => {
    const { result } = renderHook(() => useGeneration())

    expect(typeof result.current.pollJobStatus).toBe('function')
  })
})
