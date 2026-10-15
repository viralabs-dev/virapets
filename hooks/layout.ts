import { FRAME_SETS } from './frames'

/** Uma coluna de cada lado; o host já reserva as bordas do painel. */
export function frameSetForWidth(bodyColumns: number) {
  const available = Math.max(0, bodyColumns - 2)
  const size = Object.keys(FRAME_SETS).map(Number).sort((a, b) => b - a)
    .find(columns => columns <= available)
  return size === undefined ? undefined : FRAME_SETS[size]
}
