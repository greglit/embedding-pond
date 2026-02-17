import { PCA } from 'ml-pca'

type Point = { x: number; y: number }

export const computePcaLayout = (vectors: number[][]): Point[] => {
  if (vectors.length === 0) return []
  if (vectors.length === 1) return [{ x: 0, y: 0 }]

  const pca = new PCA(vectors, { scale: false, center: true })
  const projected = pca.predict(vectors, { nComponents: 2 }).to2DArray()

  const xs = projected.map((row) => row[0])
  const ys = projected.map((row) => row[1])
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)

  const pad = 220
  const width = window.innerWidth - pad * 2
  const height = window.innerHeight - pad * 2

  return projected.map(([x, y]) => {
    const normX = maxX === minX ? 0 : (x - minX) / (maxX - minX)
    const normY = maxY === minY ? 0 : (y - minY) / (maxY - minY)
    return {
      x: (normX - 0.5) * width,
      y: (normY - 0.5) * height,
    }
  })
}
