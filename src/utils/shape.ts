export const embeddingToPath = (embedding: number[], size = 120) => {
  if (!embedding.length) return ''

  const center = size / 2
  const innerRadius = size * 0.22
  const outerRadius = size * 0.46

  let min = Infinity
  let max = -Infinity
  for (const value of embedding) {
    if (value < min) min = value
    if (value > max) max = value
  }
  const range = max - min || 1

  const points = embedding.map((value, index) => {
    const angle = (index / embedding.length) * Math.PI * 2 - Math.PI / 2
    const normalized = (value - min) / range
    const radius = innerRadius + normalized * (outerRadius - innerRadius)
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    }
  })

  const path = points
    .map((point, index) => `${index === 0 ? 'M' : 'L'}${point.x.toFixed(2)} ${point.y.toFixed(2)}`)
    .join(' ')

  return `${path} Z`
}
