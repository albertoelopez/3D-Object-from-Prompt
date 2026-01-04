import '@testing-library/jest-dom'
import { vi } from 'vitest'

vi.mock('@react-three/fiber', () => ({
  Canvas: ({ children }: { children: React.ReactNode }) => children,
  useFrame: vi.fn(),
  useThree: vi.fn(() => ({
    camera: {},
    gl: {},
    scene: {},
  })),
}))

vi.mock('@react-three/drei', () => ({
  OrbitControls: () => null,
  Environment: () => null,
  useGLTF: vi.fn(() => ({ scene: {} })),
  Center: ({ children }: { children: React.ReactNode }) => children,
  Html: ({ children }: { children: React.ReactNode }) => children,
}))

global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

global.URL.createObjectURL = vi.fn(() => 'blob:test')
global.URL.revokeObjectURL = vi.fn()
