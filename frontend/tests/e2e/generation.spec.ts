import { test, expect } from '@playwright/test'

test.describe('3D Generation Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('should display the main page with generation form', async ({ page }) => {
    await expect(page.getByText('TRELLIS 3D Generator')).toBeVisible()
    await expect(page.getByText('Text to 3D')).toBeVisible()
    await expect(page.getByText('Image to 3D')).toBeVisible()
  })

  test('should switch between text and image tabs', async ({ page }) => {
    await page.getByText('Image to 3D').click()
    await expect(page.getByText('Upload an image')).toBeVisible()

    await page.getByText('Text to 3D').click()
    await expect(page.getByText('Describe your 3D object')).toBeVisible()
  })

  test('should show advanced options when clicked', async ({ page }) => {
    await page.getByText('Advanced').click()
    await expect(page.getByText('AI Provider')).toBeVisible()
    await expect(page.getByText('Resolution')).toBeVisible()
  })

  test('should have enhance prompt checkbox checked by default', async ({ page }) => {
    const checkbox = page.getByRole('checkbox')
    await expect(checkbox).toBeChecked()
  })

  test('should disable generate button when prompt is empty', async ({ page }) => {
    const button = page.getByRole('button', { name: /generate 3d model/i })
    await expect(button).toBeDisabled()
  })

  test('should enable generate button when prompt is entered', async ({ page }) => {
    const textarea = page.getByPlaceholder(/a red sports car/i)
    await textarea.fill('a wooden chair')

    const button = page.getByRole('button', { name: /generate 3d model/i })
    await expect(button).toBeEnabled()
  })

  test('should show 3D preview section', async ({ page }) => {
    await expect(page.getByText('3D Preview')).toBeVisible()
    await expect(page.getByText('No model yet')).toBeVisible()
  })
})
