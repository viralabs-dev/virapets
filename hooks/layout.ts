import type { FrameSet } from '../types'
/** Uma coluna de margem em cada lado; quadros pertencem ao pet ativo. */
export function frameSetForWidth(bodyColumns: number, frameSets: Record<number, FrameSet>) {
  const available = Math.max(0, bodyColumns - 2)
  const size = Object.keys(frameSets).map(Number).sort((a, b) => b - a)
    .find(columns => columns <= available)
  return size === undefined ? undefined : frameSets[size]
}
