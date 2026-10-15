import { atom, read, update } from 'claude-code'
import type { Hook, Register, RenderInput, StateDollar } from 'claude-code'

import type { Mood, FrameSet, Selection } from '../types'
import { PETS, DEFAULT_PET, normalizeSelection, parseCommand } from './pets'
import type { PetId } from './pets'
import { frameSetForWidth } from './layout'
import { advanceAnimation } from './animation'
import { HAPPY_MS, IDLE_MS, LABEL, afterTurn, asksUser, needsUser } from './mood'

const PANE = 'virapets'
const RASTER = 'virapets'
/** O painel do plugin Flightdeck: havendo ele, o Jojo mora embaixo do que ele desenha. */
const HOST = 'flightdeck'
/**
 * Linhas da tela abaixo do painel: as duas réguas e a linha do prompt, mais as linhas de
 * status (de 3 a 6, conforme os avisos do momento). O painel não diz a própria altura;
 * a folga evita que o Jojo passe do fundo quando aparece um aviso a mais.
 */
const BELOW_PANE = 11
/** Consulta do relógio a cada 16 ms; a pose só muda quando sua duração termina. */
const TICK_MS = 16

// O blit precisa usar exatamente o tamanho montado em cada painel.
const rasters = new Map<string, FrameSet>()

const selection = atom({ plugin: 'virapets', key: 'selection' } as const, { pet: DEFAULT_PET, mood: 'waiting' } as Selection)
let activePet: PetId = DEFAULT_PET

// O que o relógio lê a cada passo: o humor desenhado, o quadro e há quanto tempo.
let shown: Mood = 'waiting'
let frame = 0
let sinceFrame = 0
let sinceMood = 0
// Um turno longo não é inatividade: só cochila entre turnos.
let working = false
// O Jojo está sendo desenhado embaixo da Flightdeck (o hook dela passou a vez ao nosso).
let hosted = false
let ownClosed = false

/**
 * Alinha o relógio da animação ao humor guardado. O humor mora em `$.state` e sobrevive a
 * uma recarga do módulo; as variáveis do relógio não. Sem isto, depois de uma recarga o
 * relógio voltava a desenhar os quadros do WAITING por cima de um HAPPY ou BARKING.
 */
function follow(next: Mood, pet: PetId = activePet): void {
  if (next === shown && pet === activePet) return
  if (pet !== activePet) rasters.clear()
  activePet = pet
  shown = next
  frame = 0
  sinceFrame = 0
  sinceMood = 0
}

const setMood = async ($: StateDollar, next: Mood): Promise<void> => {
  follow(next)
  // O Jojo é só enfeite: uma falha ao gravar o humor nunca barra o Claude.
  await update($, selection, () => ({ pet: activePet, mood: next })).catch(() => undefined)
}

/** O desenho do pet, no painel próprio ou embaixo da Flightdeck. */
async function drawPet($: Parameters<Hook<'ui.render'>>[0], e: RenderInput<'Pane'>) {
  const current = normalizeSelection(await read($, selection))
  const now = current.mood
  follow(now, current.pet)
  const pet = PETS[current.pet]
  const { Box, Text } = $.ui.resolve(e)
  const label = <Text bold color={now === 'barking' ? 'warning' : now === 'happy' ? 'success' : 'inactive'}>{LABEL[now]}</Text>
  if (e.surface !== 'terminal') {
    rasters.delete(e.requestId)
    return <Box flexDirection="column" alignItems="center">{label}</Box>
  }
  const fitted = frameSetForWidth(e.props.bodyColumns, pet.FRAME_SETS)
  if (!fitted) {
    rasters.delete(e.requestId)
    return <Box overflow="hidden">{label}</Box>
  }
  rasters.set(e.requestId, fitted)
  const { Raster } = $.ui.resolve(e)
  const cells = fitted.frames[now][frame] ?? fitted.frames[now][0] ?? ''

  return (
    // Centralizado só na horizontal: o Jojo e o rótulo no meio da largura do painel.
    // O rótulo em cima: faltando altura, some o pescoço do Jojo, não o nome do humor.
    <Box width="100%" overflow="hidden" flexDirection="column" alignItems="center">
      <Box flexDirection="row"><Text>{pet.name} · </Text>{label}</Box>
      <Raster key={RASTER} columns={fitted.columns} rows={fitted.rows} cells={cells} />
    </Box>
  )
}

const command = async ($: Parameters<Hook<'command.run'>>[0], args: string) => {
  const result = parseCommand(args, await read($, selection))
  if ('text' in result) return { text: result.text }
  const current = normalizeSelection(result.selection)
  follow(current.mood, current.pet)
  frame = 0
  sinceFrame = 0
  sinceMood = 0
  await update($, selection, () => current).catch(() => undefined)
  const name = PETS[current.pet].name
  if (hosted) return { text: `${name} está embaixo do painel Flightdeck.` }
  await $.ui.open({ id: PANE, title: 'ViraPets', focus: true, columns: PETS[current.pet].COLUMNS + 4 })
  return { text: `Painel de ${name} aberto.` }
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'virapets', description: 'Escolhe um pet e abre o painel ViraPets' })
    await $.command.register({ name: 'jojo', description: 'Compatibilidade: /virapets jojo [humor]' })
    void $.ui.open({ id: PANE, title: 'ViraPets', columns: PETS[activePet].COLUMNS + 4 })
    // Depois de uma recarga, o relógio retoma o humor que estava guardado.
    const restored = normalizeSelection(await read($, selection))
    follow(restored.mood, restored.pet)
    // A animação: troca as células do Raster sem redesenhar o painel.
    let previousTick = await $.clock.now()
    let ticking = false
    $.clock.every(TICK_MS, async () => {
      if (ticking) return
      ticking = true
      try {
        const now = await $.clock.now()
        const elapsed = Math.max(0, now - previousTick)
        previousTick = now
        sinceMood += elapsed
        if (hosted && !ownClosed) {
          // Já mora embaixo da Flightdeck: o painel próprio sobraria como aba vazia.
          ownClosed = true
          rasters.delete(PANE)
          $.ui.close({ id: PANE }).catch(() => {})
        }
        if (shown === 'happy' && sinceMood >= HAPPY_MS) {
          await setMood($, 'waiting')
          return
        }
        if (!working && shown === 'waiting' && sinceMood >= IDLE_MS) {
          await setMood($, 'sleeping')
          return
        }
        const advanced = advanceAnimation(shown, frame, sinceFrame, elapsed, PETS[activePet].FRAMES[shown].length, PETS[activePet].DURATIONS)
        sinceFrame = advanced.remainder
        if (frame === advanced.frame) return
        frame = advanced.frame
        for (const [requestId, fitted] of rasters) {
          if (hosted && requestId === PANE) continue
          const cells = fitted.frames[shown][frame]
          if (cells === undefined) continue
          await $.ui.blit({ requestId, key: RASTER, cells, columns: fitted.columns, rows: fitted.rows }).catch(() => {})
        }
      } finally {
        ticking = false
      }
    })

    return next(e)
  })

  on('command.run', { command: 'virapets' }, async ($, e) => command($, e.args))
  on('command.run', { command: 'jojo' }, async ($, e) => command($, `jojo ${e.args}`))

  // Trabalhando: um turno começou ou a pessoa respondeu.
  on('turn.start', async ($, e, next) => {
    if (e.agentId === undefined) {
      working = true
      sinceMood = 0
      await setMood($, 'waiting')
    }

    return next(e)
  })

  // Uma ferramenta que pergunta à pessoa late até a resposta; a permissão de
  // qualquer ferramenta também (classic.PermissionRequest abaixo) e volta aqui.
  on('tool.call', async ($, e, next) => {
    if (asksUser(e.tool)) await setMood($, 'barking')
    const result = await next(e)
    if (shown === 'barking') await setMood($, 'waiting')

    return result
  })

  on('classic.PermissionRequest', async ($, e, next) => {
    await setMood($, 'barking')

    return next(e)
  })

  on('classic.Notification', async ($, e, next) => {
    if (needsUser(e.notification_type)) await setMood($, 'barking')
    else if (e.notification_type === 'idle_prompt' && !working && shown === 'waiting') await setMood($, 'sleeping')

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (e.agentId === undefined) {
      working = false
      sinceMood = 0
    }
    const after = afterTurn(e.agentId, e.isAborted, e.reason)
    if (after !== undefined) await setMood($, after)

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => drawPet($, e))

  // Embaixo da Flightdeck: o que ela desenhou, e o Jojo logo abaixo.
  on('ui.render', { component: 'Pane', requestId: HOST }, async ($, e, next) => {
    const host = await next(e)
    if (e.surface !== 'terminal' || host === undefined) return host
    hosted = true
    const { Box } = $.ui.resolve(e)

    // O Jojo no ponto mais baixo do painel, logo acima do prompt: a Flightdeck em
    // cima, o espaço que sobrar no meio, o Jojo no fundo. O painel não diz a própria
    // altura, só a da tela: tira-se o que fica embaixo dele (prompt e linhas de status).
    const rows = e.viewport?.rows

    return (
      <Box
        flexDirection="column"
        justifyContent="space-between"
        {...(rows ? { height: Math.max(1, rows - BELOW_PANE) } : {})}
      >
        {/* Faltando altura (a Flightdeck cresce enquanto o Claude trabalha), quem encolhe
            e esconde o resto é a parte de cima: o Jojo fica inteiro, no fundo. */}
        <Box flexDirection="column" flexShrink={1} overflow="hidden">{host}</Box>
        <Box marginTop={1} flexDirection="column" flexShrink={0}>{await drawPet($, e)}</Box>
      </Box>
    )
  })
}
