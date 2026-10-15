import { expect, test } from 'claude-code/testing'
import type { Engine } from 'claude-code/testing'
import { FRAME_SETS } from '../hooks/frames'
const FRAMES = FRAME_SETS[24]!.frames

/** O painel montado uma vez por teste: ele se redesenha quando o humor muda. */
const panes = new WeakMap<Engine, Awaited<ReturnType<Engine['ui']['mount']>>>()

/** O humor como o painel o mostra: o rótulo desenhado sob o Jojo. */
const shown = async ($: Engine): Promise<string> => {
  let drawn = panes.get($)
  if (!drawn) {
    drawn = await $.ui.mount({
      plugin: 'jojo',
      surface: 'terminal',
      component: 'Pane',
      requestId: 'jojo',
      props: { title: 'jojo', isFocused: false, bodyColumns: 30 },
    })
    panes.set($, drawn)
  }
  for (const label of ['HAPPY', 'BARKING', 'WAITING', 'SLEEPING']) {
    if (await drawn.find({ type: 'Text', text: label })) return label
  }
  return ''
}

const done = (agentId?: string, isAborted = false) => ({
  answer: 'pronto',
  durationMs: 10,
  isAborted,
  reason: isAborted ? ('aborted' as const) : ('answer' as const),
  turnId: 't1',
  ...(agentId ? { agentId } : {}),
})

test('fica feliz quando o Claude termina uma resposta', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete(done())
  expect(await shown($)).toBe('HAPPY')
})

test('a resposta de um subagente não muda o humor', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete(done('sub-1'))
  expect(await shown($)).toBe('WAITING')
})

test('interrompido, volta a esperar', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete(done())
  await $.turn.complete(done(undefined, true))
  expect(await shown($)).toBe('WAITING')
})

test('late quando o Claude pede permissão', async ($, on) => {
  on('classic.Notification', async () => ({}))
  await $.classic.Notification({ message: 'precisa de permissão', notification_type: 'permission_prompt' })
  expect(await shown($)).toBe('BARKING')
})

test('em repouso (idle_prompt) cochila', async ($, on) => {
  on('classic.Notification', async () => ({}))
  await $.classic.Notification({ message: 'esperando', notification_type: 'idle_prompt' })
  expect(await shown($)).toBe('SLEEPING')
})

test('late durante uma pergunta à pessoa e volta a esperar depois', async ($, on) => {
  let during: unknown
  on('tool.call', async () => {
    during = await shown($)
    return { result: { answers: {} } as never }
  })
  await $.tool.call({ tool: 'AskUserQuestion', questions: [] } as never)
  expect(during).toBe('BARKING')
  expect(await shown($)).toBe('WAITING')
})

test('o painel desenha o Raster e o rótulo do humor', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete(done())
  const drawn = await $.ui.mount({
    plugin: 'jojo',
    surface: 'terminal',
    component: 'Pane',
    requestId: 'jojo',
    props: { title: 'jojo', isFocused: false, bodyColumns: 30 },
  })
  expect(await drawn.find({ type: 'Raster', key: 'jojo' })).toBeDefined()
  expect(await drawn.find({ type: 'Text', text: 'HAPPY' })).toBeDefined()
})

test('o desenho usa um quadro do humor mostrado no rótulo, não do WAITING', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete(done())
  const drawn = panes.get($) ?? (await shown($), panes.get($))
  expect(await shown($)).toBe('HAPPY')
  const raster = await drawn?.find({ type: 'Raster', key: 'jojo' })
  expect(FRAMES.happy).toContain(raster?.props.cells as string)
  expect(FRAMES.waiting).not.toContain(raster?.props.cells as string)
})


test('erro de API, incluindo falta de créditos, termina em cochilo e não HAPPY', async ($, on) => {
  on('turn.complete', async () => ({ text: '' }))
  await $.turn.complete({ ...done(), reason: 'error', answer: '' })
  expect(await shown($)).toBe('SLEEPING')
  await $.turn.complete(done('sub-1'))
  expect(await shown($)).toBe('SLEEPING')
})

test('um turno novo acorda o Jojo e permissão tem prioridade sobre cochilo', async ($, on) => {
  on('turn.start', async (_$, e) => ({ turnId: e.turnId }))
  on('classic.Notification', async () => ({}))
  on('ui.open', async () => ({ value: { isPlaced: true } }))
  await $.command.run({ command: 'jojo', args: 'sleeping' })
  await $.turn.start({ text: '', turnId: 'wake' })
  expect(await shown($)).toBe('WAITING')
  await $.classic.Notification({ message: 'inativo', notification_type: 'idle_prompt' })
  expect(await shown($)).toBe('WAITING')
  await $.classic.Notification({ message: 'permissão', notification_type: 'permission_prompt' })
  expect(await shown($)).toBe('BARKING')
})
