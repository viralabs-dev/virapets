// Gerado por tools/pets.py build. Não edite à mão.
import * as pet0 from './pets/dara/frames'
import * as pet1 from './pets/jojo/frames'
import * as pet2 from './pets/mel/frames'
export const PETS = {
  "dara": { name: "Dara", status: "draft", ...pet0 },
  "jojo": { name: "Jojo", status: "ready", ...pet1 },
  "mel": { name: "Mel", status: "draft", ...pet2 },
} as const
