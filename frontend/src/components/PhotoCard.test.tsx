import { afterEach, describe, expect, test, vi } from 'vitest'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import PhotoCard from './PhotoCard'
import type { Photo } from '../types'

afterEach(cleanup)

const photo: Photo = {
  id: 1,
  thumb_url: '/thumbs/a.jpg',
  folder: 'Birds',
  path: 'Demo/Birds/owl.jpg',
  copies: 2,
  also_found: ['Demo/Birds/owl2.jpg', 'Demo/Other/owl3.jpg'],
}

describe('PhotoCard', () => {
  test('shows the folder and the number of copies while duplicates are hidden', () => {
    render(<PhotoCard photo={photo} showCopies onOpen={() => {}} />)
    expect(screen.getByText(/Birds/)).toBeTruthy()
    expect(screen.getByText(/\+2 copies/)).toBeTruthy()
  })

  test('hides the copies badge when duplicates are shown', () => {
    render(<PhotoCard photo={photo} showCopies={false} onOpen={() => {}} />)
    expect(screen.queryByText(/copies/)).toBeNull()
  })

  test('calls onOpen with the photo when clicked', () => {
    const onOpen = vi.fn()
    render(<PhotoCard photo={photo} showCopies onOpen={onOpen} />)
    fireEvent.click(screen.getByRole('button'))
    expect(onOpen).toHaveBeenCalledWith(photo)
  })
})
