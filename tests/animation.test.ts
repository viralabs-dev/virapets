import { expect, test } from 'claude-code/testing'
import { DURATIONS } from '../generated/pets/jojo/frames'
import { advanceAnimation as advance, frameDuration as duration } from '../hooks/animation'
const frameDuration = (mood: Parameters<typeof duration>[0], frame: number) => duration(mood, frame, DURATIONS)
const advanceAnimation = (...args: [Parameters<typeof advance>[0], number, number, number, number]) => advance(...args, DURATIONS)

test('o WAITING mantém repouso, pisca rápido e fecha o ciclo sem salto de tempo', () => {
  expect(advanceAnimation('waiting', 0, 0, 1439, 8).frame).toBe(0)
  expect(advanceAnimation('waiting', 0, 0, 1440, 8).frame).toBe(1)
  expect(frameDuration('waiting', 3) + frameDuration('waiting', 4)).toBe(160)
  expect(advanceAnimation('waiting', 0, 0, 2400, 8)).toEqual({ frame: 0, remainder: 0 })
})

test('atrasos irregulares produzem a mesma pose que o tempo total, sem acumular deriva', () => {
  for (const mood of ['happy', 'barking', 'waiting', 'sleeping'] as const) {
    let state = { frame: 0, remainder: 0 }
    let total = 0
    for (let i = 0; i < 100; i++) {
      const delta = [41, 47, 79, 121, 36][i % 5]!
      total += delta
      state = advanceAnimation(mood, state.frame, state.remainder, delta, 8)
    }
    expect(state).toEqual(advanceAnimation(mood, 0, 0, total, 8))
  }
})

test('retoma após uma suspensão longa sem reproduzir milhares de quadros atrasados', () => {
  expect(advanceAnimation('barking', 3, 25, 1140000 + 160, 8)).toEqual({ frame: 4, remainder: 25 })
  expect(advanceAnimation('happy', 2, 10, -50, 8)).toEqual({ frame: 2, remainder: 10 })
})

test('o latido separa o fechamento da boca e sustenta a abertura máxima (tempos do GIF, em 10 ms)', () => {
  expect(frameDuration('barking', 0)).toBe(360)
  expect(frameDuration('barking', 3) + frameDuration('barking', 4)).toBe(290)
  expect(advanceAnimation('barking', 0, 0, 1140, 8)).toEqual({ frame: 0, remainder: 0 })
})

test('o HAPPY sustenta o sorriso, pisca rápido e completa o ciclo sem deriva', () => {
  expect(advanceAnimation('happy', 0, 0, 239, 8).frame).toBe(0)
  expect(advanceAnimation('happy', 0, 0, 240, 8).frame).toBe(1)
  expect(frameDuration('happy', 3) + frameDuration('happy', 4)).toBe(160)
  expect(advanceAnimation('happy', 0, 0, 960, 8)).toEqual({ frame: 0, remainder: 0 })
})


test('o cochilo respira devagar e tomba a cabeça, desperta e repete o ciclo em 3,74 s', () => {
  expect(frameDuration('sleeping', 0)).toBe(1000)
  expect(advanceAnimation('sleeping', 0, 0, 2070, 8).frame).toBe(4)
  expect(frameDuration('sleeping', 4)).toBe(220)
  expect(advanceAnimation('sleeping', 0, 0, 3740, 8)).toEqual({ frame: 0, remainder: 0 })
})
