import { expect, mock, test } from 'claude-code/testing'
import { FRAME_SETS } from '../hooks/frames'
import { frameSetForWidth } from '../hooks/layout'

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
  const panel = await $.ui.mount({ plugin: 'jojo', surface: 'terminal', component: 'Pane', requestId: 'jojo',
    props: { title: 'jojo', isFocused: false, bodyColumns: 30 } })
  const raster = await panel.find({ type: 'Raster', key: 'jojo' })
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
  const panel = await $.ui.mount({ plugin: 'jojo', surface: 'terminal', component: 'Pane', requestId: 'flightdeck',
    props: { title: 'Flightdeck', isFocused: false, bodyColumns: 38 } })
  const raster = await panel.find({ type: 'Raster', key: 'jojo' })
  expect(raster?.props.columns).toBe(32)
  expect(raster?.props.rows).toBe(18)
})
