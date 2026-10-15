import type { Mood } from '../types'

/** Quanto o Jojo fica feliz depois de uma resposta antes de voltar a esperar. */
export const HAPPY_MS = 6000

/** Intervalo entre quadros de cada humor, em milissegundos. */
export const FRAME_MS: Record<Mood, number> = { happy: 220, barking: 160, waiting: 450 }

export const LABEL: Record<Mood, string> = { happy: 'HAPPY', barking: 'BARKING', waiting: 'WAITING' }

/** Ferramentas cuja chamada espera uma resposta da pessoa. */
const ASKS_USER = new Set(['AskUserQuestion', 'ExitPlanMode'])

/** Avisos do Claude Code que pedem um gesto da pessoa (o `idle_prompt` não: em repouso o Jojo espera). */
const NEEDS_USER = new Set(['permission_prompt', 'elicitation_dialog'])

export const asksUser = (tool: string): boolean => ASKS_USER.has(tool)

export const needsUser = (notificationType: string): boolean => NEEDS_USER.has(notificationType)

/** Fim de um turno: só o da conversa principal deixa o Jojo feliz, e só com resposta. */
export const afterTurn = (agentId: string | undefined, isAborted: boolean): Mood | undefined =>
  agentId !== undefined ? undefined : isAborted ? 'waiting' : 'happy'
