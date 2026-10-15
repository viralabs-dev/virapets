export type Mood = 'happy' | 'barking' | 'waiting' | 'sleeping'
export type Durations = Record<Mood, readonly number[]>
export type FrameSet = { columns: number; rows: number; frames: Record<Mood, readonly string[]> }
export type Selection = { pet: string; mood: Mood }
declare module 'claude-code' {
  interface PluginState { virapets: { selection: Selection } }
}
