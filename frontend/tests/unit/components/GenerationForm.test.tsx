import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { GenerationForm } from '@/components/generation/GenerationForm'

vi.mock('@/hooks/useGeneration', () => ({
  useGeneration: () => ({
    generateFromText: vi.fn(),
    generateFromImage: vi.fn(),
    loading: false,
  }),
}))

vi.mock('@/store', () => ({
  useGenerationStore: () => ({
    isGenerating: false,
  }),
  useUIStore: () => ({
    activeTab: 'text',
    setActiveTab: vi.fn(),
    showAdvancedOptions: false,
    setShowAdvancedOptions: vi.fn(),
  }),
}))

describe('GenerationForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders text and image tabs', () => {
    render(<GenerationForm />)

    expect(screen.getByText('Text to 3D')).toBeInTheDocument()
    expect(screen.getByText('Image to 3D')).toBeInTheDocument()
  })

  it('renders text input in text mode', () => {
    render(<GenerationForm />)

    expect(screen.getByPlaceholderText(/a red sports car/i)).toBeInTheDocument()
  })

  it('renders generate button', () => {
    render(<GenerationForm />)

    expect(screen.getByRole('button', { name: /generate 3d model/i })).toBeInTheDocument()
  })

  it('shows enhance prompt checkbox', () => {
    render(<GenerationForm />)

    expect(screen.getByText(/enhance prompt with ai/i)).toBeInTheDocument()
  })

  it('disables generate button when prompt is empty', () => {
    render(<GenerationForm />)

    const button = screen.getByRole('button', { name: /generate 3d model/i })
    expect(button).toBeDisabled()
  })
})
