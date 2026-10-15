import { expect, mock, test } from 'claude-code/testing'
import { PETS, normalizeSelection, parseCommand, USAGE } from '../hooks/pets'
import { advanceAnimation } from '../hooks/animation'

test('comandos inválidos e list não trocam o personagem; nomes ignoram caixa', () => {
  const current = { pet: 'mel', mood: 'sleeping' as const }
  expect(parseCommand('', current)).toEqual({ selection: current })
  expect(parseCommand('DARA', current)).toEqual({ selection: { pet: 'dara', mood: 'sleeping' } })
  for (const args of ['x', 'dara x', 'jojo happy extra']) expect(parseCommand(args, current)).toEqual({ text: USAGE })
  expect(parseCommand('list', current).text).toContain('Mel')
  expect(normalizeSelection({ pet: 'removido', mood: 'happy' })).toEqual({ pet: 'jojo', mood: 'happy' })
})

test('seleciona os três pets nos quatro estados e mantém o alias /jojo', async ($, on) => {
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  const panel = await $.ui.mount({ plugin: 'virapets', surface: 'terminal', component: 'Pane', requestId: 'virapets',
    props: { title: 'ViraPets', isFocused: false, bodyColumns: 52 } })
  for (const id of ['jojo', 'mel', 'dara'] as const) {
    for (const mood of ['happy', 'barking', 'waiting', 'sleeping'] as const) {
      const result = await $.command.run({ command: 'virapets', args: `${id} ${mood}` })
      expect(result.text).toBe(`Painel de ${PETS[id].name} aberto.`)
      const raster = await panel.find({ type: 'Raster', key: 'virapets' })
      expect(raster?.props.cells).toBe(PETS[id].FRAMES[mood][0])
    }
  }
  await $.command.run({ command: 'virapets', args: 'desconhecido' })
  expect((await panel.find({ type: 'Raster', key: 'virapets' }))?.props.cells).toBe(PETS.dara.FRAMES.sleeping[0])
  await $.command.run({ command: 'jojo', args: 'barking' })
  expect((await panel.find({ type: 'Raster', key: 'virapets' }))?.props.cells).toBe(PETS.jojo.FRAMES.barking[0])
})

test('trocar de pet reinicia a pose e os próximos blits não reaproveitam o cão anterior', async ($, on) => {
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  const clock = mock.clock(on)
  const painted: string[] = []
  on('ui.blit', async (_$, e) => { if ('cells' in e) painted.push(e.cells); return { value: {} } })
  await $.session.start({ cwd: '/virapets', surface: 'terminal', isInteractive: true })
  const panel = await $.ui.mount({ plugin: 'virapets', surface: 'terminal', component: 'Pane', requestId: 'virapets',
    props: { title: 'ViraPets', isFocused: false, bodyColumns: 30 } })
  await clock.advance(1600)
  for (const id of ['mel', 'dara', 'jojo'] as const) {
    await $.command.run({ command: 'virapets', args: `${id} barking` })
    expect((await panel.find({ type: 'Raster', key: 'virapets' }))?.props.cells).toBe(PETS[id].FRAME_SETS[24]!.frames.barking[0])
    painted.length = 0
    await clock.advance(480)
    expect(painted.length > 0).toBe(true)
    for (const cells of painted) expect(PETS[id].FRAME_SETS[24]!.frames.barking).toContain(cells)
  }
})

test('o relógio aceita contagens e tempos diferentes por personagem', () => {
  const times = { happy: [40, 90, 170], barking: [20], waiting: [50], sleeping: [100] }
  expect(advanceAnimation('happy', 0, 0, 135, 3, times)).toEqual({ frame: 2, remainder: 5 })
  expect(advanceAnimation('happy', 0, 0, 335, 3, times)).toEqual({ frame: 0, remainder: 35 })
})
