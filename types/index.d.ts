/** O humor do Jojo: uma linha da folha de sprites. */
export type Mood = 'happy' | 'barking' | 'waiting' | 'sleeping'

declare module 'claude-code' {
  interface PluginState {
    jojo: { mood: Mood }
  }
}
