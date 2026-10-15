import type { Mood } from '../types'

/** Quanto o Jojo fica feliz depois de uma resposta antes de voltar a esperar. */
export const HAPPY_MS = 6000
export const IDLE_MS = 30000

/** Intervalo entre quadros de cada humor, em milissegundos. */
export const FRAME_MS: Record<Mood, number> = { happy: 120, barking: 80, waiting: 200, sleeping: 400 }

export const LABEL: Record<Mood, string> = { happy: 'HAPPY', barking: 'BARKING', waiting: 'WAITING', sleeping: 'SLEEPING' }

export const isMood = (text: string): text is Mood => Object.hasOwn(LABEL, text)

/** Ferramentas cuja chamada espera uma resposta da pessoa. */
const ASKS_USER = new Set(['AskUserQuestion', 'ExitPlanMode'])

/** Avisos do Claude Code que pedem um gesto da pessoa (o `idle_prompt` leva ao cochilo). */
const NEEDS_USER = new Set(['permission_prompt', 'elicitation_dialog'])

export const asksUser = (tool: string): boolean => ASKS_USER.has(tool)

export const needsUser = (notificationType: string): boolean => NEEDS_USER.has(notificationType)

/** Fim do turno principal: erro de API leva ao cochilo; subagentes não mudam o humor. */
export const afterTurn = (agentId: string | undefined, isAborted: boolean, reason?: string): Mood | undefined =>
  agentId !== undefined ? undefined : reason === 'error' ? 'sleeping' : isAborted ? 'waiting' : 'happy'
