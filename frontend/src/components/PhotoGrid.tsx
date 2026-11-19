import PhotoCard from './PhotoCard'
import type { Photo } from '../types'

interface Props {
  photos: Photo[]
  showCopies: boolean
  onOpen: (photo: Photo) => void
}

export default function PhotoGrid({ photos, showCopies, onOpen }: Props) {
  return (
    <div className="grid">
      {photos.map(p => (
        <PhotoCard key={p.id} photo={p} showCopies={showCopies} onOpen={onOpen} />
      ))}
    </div>
  )
}
