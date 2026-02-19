type SourceType = 'text' | 'image'

type LilyLike = {
  sourceType: SourceType
  embedding: number[]
}

export type CentroidAlignOptions = {
  enabled: boolean
  alpha: number
  target?: 'shift-text-to-image' | 'shift-image-to-text'
  renormalize?: boolean
}

const l2Normalize = (vector: number[]) => {
  let sum = 0
  for (let i = 0; i < vector.length; i += 1) {
    const v = vector[i] ?? 0
    sum += v * v
  }
  const norm = Math.sqrt(sum) || 1
  return vector.map((v) => (v ?? 0) / norm)
}

const meanVector = (vectors: number[][], dims: number) => {
  const mean = new Array(dims).fill(0)
  if (vectors.length === 0) return mean
  for (const vec of vectors) {
    for (let i = 0; i < dims; i += 1) {
      mean[i] += vec[i] ?? 0
    }
  }
  for (let i = 0; i < dims; i += 1) {
    mean[i] /= vectors.length
  }
  return mean
}

export const buildVectorsForPca = (items: LilyLike[], options: CentroidAlignOptions): number[][] => {
  if (!options.enabled) return items.map((item) => item.embedding)
  if (items.length < 2) return items.map((item) => item.embedding)

  const text = items.filter((item) => item.sourceType === 'text').map((item) => item.embedding)
  const image = items.filter((item) => item.sourceType === 'image').map((item) => item.embedding)

  if (text.length === 0 || image.length === 0) return items.map((item) => item.embedding)

  const dims = items[0]?.embedding.length ?? 0
  if (dims === 0) return items.map((item) => item.embedding)

  const muText = meanVector(text, dims)
  const muImage = meanVector(image, dims)
  const alpha = Number.isFinite(options.alpha) ? options.alpha : 1
  const renormalize = options.renormalize ?? true
  const target = options.target ?? 'shift-text-to-image'

  const delta = new Array(dims)
  for (let i = 0; i < dims; i += 1) {
    const d = (muImage[i] ?? 0) - (muText[i] ?? 0)
    delta[i] = target === 'shift-text-to-image' ? d : -d
  }

  return items.map((item) => {
    const shouldShift = target === 'shift-text-to-image' ? item.sourceType === 'text' : item.sourceType === 'image'
    if (!shouldShift) return item.embedding

    const shifted = new Array(dims)
    for (let i = 0; i < dims; i += 1) {
      shifted[i] = (item.embedding[i] ?? 0) + alpha * (delta[i] ?? 0)
    }
    return renormalize ? l2Normalize(shifted) : shifted
  })
}
