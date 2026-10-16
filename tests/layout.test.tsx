import { expect, mock, test } from 'claude-code/testing'
import { FRAME_SETS as DARA } from '../generated/pets/dara/frames'
import { FRAME_SETS as MEL } from '../generated/pets/mel/frames'
import { FRAME_SETS } from '../generated/pets/jojo/frames'
import { frameSetForWidth as fit } from '../hooks/layout'
const frameSetForWidth = (width: number) => fit(width, FRAME_SETS)

test('todos os tamanhos respeitam a largura útil e a margem direita', () => {
  for (let width = 1; width <= 80; width++) {
    const fitted = frameSetForWidth(width)
    if (fitted) {
      expect(fitted.columns + 2 <= width).toBe(true)
      expect((fitted.rows - 2) * 2).toBe(fitted.columns)
    } else expect(width < 10).toBe(true)
  }
})

test('o corpo real de 50 colunas conserva o sprite de 48 pixels', () => {
  expect(frameSetForWidth(50)?.columns).toBe(48)
  expect(frameSetForWidth(49)?.columns).toBe(40)
})

test('painel estreito monta quadros menores e o blit mantém a mesma geometria', async ($, on) => {
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  const clock = mock.clock(on)
  const paints: { columns?: number; rows?: number; cells: string }[] = []
  on('ui.blit', async (_$, e) => {
    if ('cells' in e) paints.push(e)
    return { value: {} }
  })
  await $.session.start({ cwd: '/jojo', surface: 'terminal', isInteractive: true })
  const panel = await $.ui.mount({ plugin: 'virapets', surface: 'terminal', component: 'Pane', requestId: 'virapets',
    props: { title: 'jojo', isFocused: false, bodyColumns: 30 } })
  const raster = await panel.find({ type: 'Raster', key: 'virapets' })
  expect(raster?.props.columns).toBe(24)
  expect(raster?.props.rows).toBe(14)
  await clock.advance(1440)
  expect(paints.length).toBe(1)
  expect(paints[0]?.columns).toBe(24)
  expect(paints[0]?.rows).toBe(14)
  expect(paints[0]?.cells).toBe(FRAME_SETS[24]!.frames.waiting[1])
})

test('a composição Flightdeck também cabe no corpo estreito do painel', async ($, on) => {
  on('ui.render', { component: 'Pane', requestId: 'flightdeck' }, async ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>Flightdeck</Text>
  })
  const panel = await $.ui.mount({ plugin: 'virapets', surface: 'terminal', component: 'Pane', requestId: 'flightdeck',
    props: { title: 'Flightdeck', isFocused: false, bodyColumns: 38 } })
  const raster = await panel.find({ type: 'Raster', key: 'virapets' })
  expect(raster?.props.columns).toBe(32)
  expect(raster?.props.rows).toBe(18)
})

test('Dara aproveita larguras intermediárias sem alterar Mel ou Jojo', () => {
  for (const [width, size] of [[30, 28], [38, 36], [44, 42], [46, 44], [48, 46], [50, 48]]) {
    expect(fit(width!, DARA)?.columns).toBe(size)
  }
  expect(fit(48, MEL)?.columns).toBe(40)
  expect(frameSetForWidth(48)?.columns).toBe(40)
  for (let width = 1; width <= 80; width++) {
    const fitted = fit(width, DARA)
    if (fitted) expect(fitted.columns + 2 <= width).toBe(true)
  }
})

test('Dara anima a escala intermediária com a mesma geometria do painel', async ($, on) => {
  on('session.start', async (_$, e) => ({ cwd: e.cwd }))
  on('command.register', async (_$, e) => ({ value: { command: e.name } }))
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  const clock = mock.clock(on)
  const paints: { columns?: number; rows?: number; cells: string }[] = []
  on('ui.blit', async (_$, e) => { if ('cells' in e) paints.push(e); return { value: {} } })
  await $.session.start({ cwd: '/virapets', surface: 'terminal', isInteractive: true })
  const panel = await $.ui.mount({ plugin: 'virapets', surface: 'terminal', component: 'Pane', requestId: 'virapets',
    props: { title: 'ViraPets', isFocused: false, bodyColumns: 48 } })
  await $.command.run({ command: 'virapets', args: 'dara sleeping' })
  const raster = await panel.find({ type: 'Raster', key: 'virapets' })
  expect(raster?.props.columns).toBe(46)
  expect(raster?.props.rows).toBe(25)
  await clock.advance(1600)
  expect(paints.length > 0).toBe(true)
  for (const paint of paints) {
    expect(paint.columns).toBe(46)
    expect(paint.rows).toBe(25)
    expect(DARA[46]!.frames.sleeping).toContain(paint.cells)
  }
})
