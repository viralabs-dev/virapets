import type { Mood } from '../types'
import { DURATIONS } from './frames'
import { FRAME_MS } from './mood'

/** O tempo de cada quadro vem do GIF do humor (tools/build_frames.py). */
export const frameDuration = (mood: Mood, frame: number): number =>
  DURATIONS[mood][frame] ?? FRAME_MS[mood]

/** Avança pelo tempo real, preservando a sobra e pulando ciclos após uma suspensão. */
export function advanceAnimation(mood: Mood, frame: number, remainder: number, elapsed: number, count: number) {
  let remaining = remainder + Math.max(0, elapsed)
  let cycle = 0
  for (let i = 0; i < count; i++) cycle += frameDuration(mood, i)
  if (count < 1 || cycle <= 0) return { frame: 0, remainder: 0 }
  remaining %= cycle
  while (remaining >= frameDuration(mood, frame)) {
    remaining -= frameDuration(mood, frame)
    frame = (frame + 1) % count
  }
  return { frame, remainder: remaining }
}
