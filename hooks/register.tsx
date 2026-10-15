import { atom, read, update } from 'claude-code'
import type { Hook, Register, RenderInput, StateDollar } from 'claude-code'

import type { Mood } from '../types'
import { COLUMNS, FRAMES, ROWS } from './frames'
import { FRAME_MS, HAPPY_MS, LABEL, afterTurn, asksUser, needsUser } from './mood'

const PANE = 'jojo'
const RASTER = 'jojo'
/** O painel do plugin Flightdeck: havendo ele, o Jojo mora embaixo do que ele desenha. */
const HOST = 'flightdeck'
/**
 * Linhas da tela abaixo do painel: as duas réguas e a linha do prompt, mais as linhas de
 * status (de 3 a 6, conforme os avisos do momento). O painel não diz a própria altura;
 * a folga evita que o Jojo passe do fundo quando aparece um aviso a mais.
 */
const BELOW_PANE = 11
/** Passo do relógio da animação; cada humor anda no seu ritmo (FRAME_MS). */
const TICK_MS = 40

const mood = atom({ plugin: 'jojo', key: 'mood' } as const, 'waiting' as Mood)

// O que o relógio lê a cada passo: o humor desenhado, o quadro e há quanto tempo.
let shown: Mood = 'waiting'
let frame = 0
let sinceFrame = 0
let sinceMood = 0
// O Jojo está sendo desenhado embaixo da Flightdeck (o hook dela passou a vez ao nosso).
let hosted = false
let ownClosed = false

/**
 * Alinha o relógio da animação ao humor guardado. O humor mora em `$.state` e sobrevive a
 * uma recarga do módulo; as variáveis do relógio não. Sem isto, depois de uma recarga o
 * relógio voltava a desenhar os quadros do WAITING por cima de um HAPPY ou BARKING.
 */
function follow(next: Mood): void {
  if (next === shown) return
  shown = next
  frame = 0
  sinceFrame = 0
  sinceMood = 0
}

const setMood = async ($: StateDollar, next: Mood): Promise<void> => {
  follow(next)
  // O Jojo é só enfeite: uma falha ao gravar o humor nunca barra o Claude.
  await update($, mood, () => next).catch(() => undefined)
}

/** O desenho do Jojo, no painel próprio ou embaixo da Flightdeck. */
async function drawJojo($: Parameters<Hook<'ui.render'>>[0], e: RenderInput<'Pane'>) {
  const now = await read($, mood)
  follow(now)
  const { Box, Text } = $.ui.resolve(e)
  const label = <Text bold color={now === 'barking' ? 'warning' : now === 'happy' ? 'success' : 'inactive'}>{LABEL[now]}</Text>
  if (e.surface !== 'terminal') {
    return <Box flexDirection="column" alignItems="center">{label}</Box>
  }
  const { Raster } = $.ui.resolve(e)
  const cells = FRAMES[now][frame]

  return (
    // Centralizado só na horizontal: o Jojo e o rótulo no meio da largura do painel.
    // O rótulo em cima: faltando altura, some o pescoço do Jojo, não o nome do humor.
    <Box flexDirection="column" alignItems="center">
      {label}
      <Raster key={RASTER} columns={COLUMNS} rows={ROWS} cells={cells} />
    </Box>
  )
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'jojo', description: 'Abre o painel do Jojo' })
    void $.ui.open({ id: PANE, title: 'jojo', columns: COLUMNS + 4 })
    // Depois de uma recarga, o relógio retoma o humor que estava guardado.
    follow(await read($, mood))
    // A animação: troca as células do Raster sem redesenhar o painel.
    $.clock.every(TICK_MS, () => {
      sinceFrame += TICK_MS
      sinceMood += TICK_MS
      if (hosted && !ownClosed) {
        // Já mora embaixo da Flightdeck: o painel próprio sobraria como aba vazia.
        ownClosed = true
        $.ui.close({ id: PANE }).catch(() => {})
      }
      if (shown === 'happy' && sinceMood >= HAPPY_MS) {
        void setMood($, 'waiting')
        return
      }
      if (sinceFrame < FRAME_MS[shown]) return
      sinceFrame = 0
      frame = (frame + 1) % FRAMES[shown].length
      const cells = FRAMES[shown][frame]
      $.ui.blit({ requestId: hosted ? HOST : PANE, key: RASTER, cells }).catch(() => {})
    })

    return next(e)
  })

  on('command.run', { command: 'jojo' }, async $ => {
    if (hosted) return { text: 'O Jojo está embaixo do painel Flightdeck.' }
    // Pedido pela pessoa: traz a aba do Jojo para a frente (Esc devolve o teclado).
    await $.ui.open({ id: PANE, title: 'jojo', focus: true, columns: COLUMNS + 4 })

    return { text: 'Painel do Jojo aberto.' }
  })

  // Trabalhando: um turno começou ou a pessoa respondeu.
  on('turn.start', async ($, e, next) => {
    await setMood($, 'waiting')

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

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    const after = afterTurn(e.agentId, e.isAborted)
    if (after !== undefined) await setMood($, after)

    return next(e)
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => drawJojo($, e))

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
        <Box marginTop={1} flexDirection="column" flexShrink={0}>{await drawJojo($, e)}</Box>
      </Box>
    )
  })
}
