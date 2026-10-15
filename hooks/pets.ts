import { PETS } from '../generated/catalog'
import type { Selection } from '../types'
import { isMood } from './mood'
export { PETS }
export type PetId = keyof typeof PETS
export const DEFAULT_PET: PetId = 'jojo'
export const isPet = (value: string): value is PetId => Object.hasOwn(PETS, value)
export const normalizeSelection = (value: Selection): { pet: PetId; mood: Selection['mood'] } => ({
  pet: isPet(value.pet) ? value.pet : DEFAULT_PET,
  mood: isMood(value.mood) ? value.mood : 'waiting',
})
export const USAGE = 'Uso: /virapets <' + Object.keys(PETS).join('|') + '> [happy|barking|waiting|sleeping]'
export function parseCommand(args: string, current: Selection) {
  const words = args.trim().toLowerCase().split(/\s+/).filter(Boolean)
  if (!words.length) return { selection: normalizeSelection(current) }
  if (words.length === 1 && (words[0] === 'list' || words[0] === 'help')) {
    return { text: USAGE + '\nPets: ' + Object.values(PETS).map(pet => pet.name).join(', ') }
  }
  const [pet, mood] = words
  if (!pet || !isPet(pet) || words.length > 2 || (mood !== undefined && !isMood(mood))) {
    return { text: USAGE }
  }
  return { selection: { pet, mood: mood === undefined ? normalizeSelection(current).mood : mood } }
}
