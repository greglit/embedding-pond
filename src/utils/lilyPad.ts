type LilyPadPathOptions = {
  cx?: number
  cy?: number
  r?: number
  slitAngle: number
  slitWidth: number
  slitInset?: number
}

export function createLilyPadPaths(options: LilyPadPathOptions) {
  const cx = options.cx ?? 60
  const cy = options.cy ?? 60
  const r = options.r ?? 56
  // Extending the slit endpoints slightly helps avoid tiny seams
  // between the fill and the slit stroke due to antialiasing.
  const slitInset = options.slitInset ?? 1

  const slitR = Math.max(0, r + slitInset)
  const start = options.slitAngle - options.slitWidth / 2
  const end = options.slitAngle + options.slitWidth / 2

  const startOuter = polarPoint(cx, cy, r, start)
  const endOuter = polarPoint(cx, cy, r, end)
  const slitStart = polarPoint(cx, cy, slitR, start)
  const slitEnd = polarPoint(cx, cy, slitR, end)

  // Fill: full circle with a wedge cut out (evenodd).
  const circle = `M ${cx + r} ${cy} A ${r} ${r} 0 1 0 ${cx - r} ${cy} A ${r} ${r} 0 1 0 ${cx + r} ${cy} Z`
  const wedge = `M ${cx} ${cy} L ${startOuter.x} ${startOuter.y} A ${r} ${r} 0 0 1 ${endOuter.x} ${endOuter.y} Z`

  // Slit outline: the two wedge edges; end slightly inside the pad.
  const slitPath = `M ${cx} ${cy} L ${slitStart.x} ${slitStart.y} M ${cx} ${cy} L ${slitEnd.x} ${slitEnd.y}`

  return {
    fillPath: `${circle} ${wedge}`,
    slitPath,
  }
}

function polarPoint(cx: number, cy: number, r: number, angle: number) {
  return {
    x: (cx + r * Math.cos(angle)).toFixed(2),
    y: (cy + r * Math.sin(angle)).toFixed(2),
  }
}
