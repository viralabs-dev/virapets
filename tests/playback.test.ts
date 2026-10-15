import { expect, mock, test } from 'claude-code/testing'
import { FRAMES } from '../hooks/frames'

test('o relógio real do hook respeita o repouso e envia a próxima pose ao Raster', async ($, on) => {
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  const clock = mock.clock(on)
  const painted: string[] = []
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  on('ui.blit', async (_$, e) => {
    if ('cells' in e) painted.push(e.cells)
    return { value: {} }
  })
  await $.session.start({ cwd: '/jojo', surface: 'terminal', isInteractive: true })
  await $.ui.mount({ plugin: 'jojo', surface: 'terminal', component: 'Pane', requestId: 'jojo',
    props: { title: 'jojo', isFocused: false, bodyColumns: 52 } })
  await clock.advance(1424)
  expect(painted).toEqual([])
  await clock.advance(16)
  expect(painted).toEqual([FRAMES.waiting[1]])
})

test('a prévia por comando seleciona cada estado sem depender de um turno de modelo', async ($, on) => {
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  const panel = await $.ui.mount({ plugin: 'jojo', surface: 'terminal', component: 'Pane', requestId: 'jojo',
    props: { title: 'jojo', isFocused: false, bodyColumns: 52 } })
  for (const mood of ['barking', 'happy', 'waiting', 'sleeping'] as const) {
    const response = await $.command.run({ command: 'jojo', args: mood })
    expect(response.text).toBe('Painel do Jojo aberto.')
    expect(await panel.find({ type: 'Text', text: mood.toUpperCase() })).toBeDefined()
    const raster = await panel.find({ type: 'Raster', key: 'jojo' })
    expect(FRAMES[mood]).toContain(raster?.props.cells as string)
  }
})


test('cochila em 30 s de repouso, mas não no meio de um turno longo', async ($, on) => {
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('turn.start', async (_$, e) => ({ turnId: e.turnId }))
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  on('ui.blit', async () => ({ value: {} }))
  const clock = mock.clock(on)
  await $.session.start({ cwd: '/jojo', surface: 'terminal', isInteractive: true })
  const panel = await $.ui.mount({ plugin: 'jojo', surface: 'terminal', component: 'Pane', requestId: 'jojo',
    props: { title: 'jojo', isFocused: false, bodyColumns: 52 } })
  await clock.advance(29984)
  expect(await panel.find({ type: 'Text', text: 'WAITING' })).toBeDefined()
  await clock.advance(16)
  expect(await panel.find({ type: 'Text', text: 'SLEEPING' })).toBeDefined()
  await $.turn.start({ text: '', turnId: 'long' })
  await clock.advance(31008)
  expect(await panel.find({ type: 'Text', text: 'WAITING' })).toBeDefined()
})
