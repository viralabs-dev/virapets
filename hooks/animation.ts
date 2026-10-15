import type { Mood, Durations } from '../types'
import { FRAME_MS } from './mood'
/** Each pet owns its GIF timings. */
export const frameDuration = (mood: Mood, frame: number, durations: Durations): number =>
  durations[mood][frame] ?? FRAME_MS[mood]
export function advanceAnimation(mood: Mood, frame: number, remainder: number, elapsed: number, count: number, durations: Durations) {
  let remaining = remainder + Math.max(0, elapsed)
  let cycle = 0
  for (let i = 0; i < count; i++) cycle += frameDuration(mood, i, durations)
  if (count < 1 || cycle <= 0) return { frame: 0, remainder: 0 }
  remaining %= cycle
  frame %= count
  while (remaining >= frameDuration(mood, frame, durations)) {
    remaining -= frameDuration(mood, frame, durations)
    frame = (frame + 1) % count
  }
  return { frame, remainder: remaining }
}
