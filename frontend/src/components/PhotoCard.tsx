import { t } from '../strings'
import type { Photo } from '../types'

interface Props {
  photo: Photo
  showCopies: boolean   // only true while duplicates are hidden
  onOpen: (photo: Photo) => void
}

export default function PhotoCard({ photo, showCopies, onOpen }: Props) {
  const caption = photo.folder || t.mainFolder
  return (
    <figure className="card">
      <button className="card-button" onClick={() => onOpen(photo)} aria-label={`Open ${caption}`}>
        <img src={photo.thumb_url} alt={caption} loading="lazy" />
      </button>
      <figcaption>
        {caption}
        {showCopies && photo.copies > 0 && <span className="copies"> ({t.copies(photo.copies)})</span>}
      </figcaption>
    </figure>
  )
}
