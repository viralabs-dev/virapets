# ViraPets Studio — browser creation guide

Open **[the published studio](https://daneiel.github.io/virapets/)**. No account, Python installation or API key is needed to use the page. The interface is in Brazilian Portuguese; this guide explains its labels in English. The [project README](../README.md) has the complete Portuguese guide and Claude Code installation instructions.

## Choose a creation path

| Path | Best for | How it works |
|---|---|---|
| **Desenho procedural** | Trying the editor immediately | Choose an animal, breed or type, colors, name, package ID and author. Original pixel characters are drawn locally, without a model. |
| **Foto → pixel art local** | Keeping your photo's colors and silhouette | Cut out, pixelize and retouch a local image. The cutout moves; the editor does not draw new facial expressions. SlimSAM-assisted selection is optional. |
| **Ver e copiar prompt** | Creating an illustrated character in another platform | Copy the complete project prompt and attach your photo to an image-capable platform. That platform's tools determine the real files it can produce. |

Procedural output uses stylized silhouettes, not exact breed portraits. Birds and reptiles are grouped by type rather than breed. Cow and ox are separate visual choices for the requested characters. Procedural and photo output have a simpler finish than the illustrated Jojo, Mel and Dara assets. The studio does not call a text-to-image service, Gradio endpoint or free LLM API.

## First use: procedural drawing

1. Select **Desenho procedural** in the inline mode switch. Choose an animal, its breed or type when available, then customize colors. Only the active mode’s tools are visible; switching preserves both editors.
2. Set **Nome**, **ID do pacote** and **Seu nome / autor**. The ID becomes the pet's directory: start with a lowercase letter and use lowercase letters, digits and hyphens, up to 48 characters. Choose an unused ID before copying into a clone.
3. Try **Feliz**, **Latindo** (or **Chamando** for other animals), **Esperando** and **Dormindo**. Use **Pausar animação** to examine the preview. Reduced-motion preference is respected.
4. Save a JSON recipe to resume later, or download ZIP for the local delivery pipeline.

The page has light/dark themes using the BRABO semantic tokens, follows the system preference initially and remembers your theme choice. Its favicon is Jojo; that does not put Jojo's artwork into your exported pet.

## Photo: cut out, pixelize, mark the head and animate

1. Select **Foto → pixel art local**. Choose a local PNG, JPEG or WebP, up to 10 MiB (the interface abbreviates this as 10 MB) and 40 megapixels. A working copy is reduced to a longest side of 768 pixels. **Testar com desenho de exemplo** creates a synthetic dog drawing if you want to try the tools without a personal photo.
2. Refine the cutout. Green marks the area to keep. For a manual selection, choose **Pincel: manter** or **Pincel: apagar** and adjust brush size. **Manter tudo**, **Limpar máscara** and **Desfazer máscara** help restart or correct it; up to ten mask changes can be undone. Arrow keys move the canvas cursor and Enter applies the tool.
3. Optionally activate **Ativar recorte assistido**. Place **Ponto no pet** points on the animal and **Ponto no fundo** points on unwanted background. A single point may preserve only one part: add points on both head and body, then correct with brushes. No model is needed for manual masking.
4. Watch the live cutout preview, choose grid resolution **16–96**, palette **2–32 colors**, and optional outline. Click **Aplicar recorte e pixelizar** to make the final art. Pick an extracted color or **Cor de retoque** and paint; **Borracha** erases pixels. Reapplying the cutout replaces these retouches.
5. On the final pixel art, mark the center of the head, adjust head size **8–100**, and select automatic, left or right muzzle direction. This mark is required before photo export and can be adjusted later. Reapplying the cutout resets it, so mark the head again.
6. Use **Simular latido e sono** to inspect the current art. With no art loaded, **Simular com exemplo local** provides a synthetic local demonstration without the model. An existing edited pet is preserved when simulating it. Switch through all four moods before downloading.

Bark rays and Zzz follow the marked head and its motion. Sleep wake-up frames 4 and 5, counted from zero, have no Zzz. Motion transforms the cutout; it does not invent new eyes, mouths or expressions. For a newly drawn character, use the full prompt instead.

## Assisted cutout: download, cache and privacy

SlimSAM q8 (`Xenova/slimsam-77-uniform`) runs locally in a module Worker using ONNX Runtime WASM CPU. WebGPU is not required. The first activation needs **36,315,496 uncompressed bytes** (about 36.3 MB): 13,786,820 bytes of weights/configuration and 22,528,676 bytes of JS/WASM runtime, excluding small page files. Transfer compression and cache can reduce actual network traffic. The download size is not a RAM requirement; speed, memory use and battery consumption vary by device.

The runtime is served with the site. Model files are downloaded from Hugging Face and its CDNs only when assisted cutout is activated. Downloads expose normal request metadata such as your IP to those hosts. Photo pixels are processed in this browser and are not uploaded; the site has no analytics or inference API fee. The optional model cache contains model files, not your photo or embeddings. Cache may be unavailable, evicted or cleared, so offline availability is not guaranteed.

- **Cancelar / liberar modelo** cancels the operation and releases its Worker, keeping the local photo/mask.
- **Limpar cache do modelo** releases the model and removes its dedicated cache; a later activation may download it again.
- If loading fails, retry or continue with manual brushes. The other editing/export paths remain usable.
- **Descartar foto e arte deste navegador** discards the working image and art from page memory. Reloading also loses unsaved work.

Save a recipe before leaving. Photo recipes contain the final derived 256×256 pixel art and normalized head marking, without the original photo, source filename, EXIF or editable mask. Importing lets you retouch and animate that art. To redo segmentation, select the source photo again. A recipe still contains a visible image of your pet: share it deliberately.

See [third-party notices](https://daneiel.github.io/virapets/vendor/PHOTO-ML-NOTICES.txt), the pinned revision in [implementation details](../docs/design/photo-editor-implementation.md), and the [consolidated published feature guide in Portuguese](../docs/design/studio-published.md).

## Prompt: use your preferred image platform

**Ver e copiar prompt** opens the complete prompt at `#prompt`. Use **Copiar prompt completo**, select/copy the text manually if clipboard access is unavailable, or choose **Baixar prompt.txt**. Attach your photo yourself in the chosen platform. The studio sends neither the prompt nor the photo there.

A text-only chat cannot produce real PNGs just from this instruction. The prompt asks an image-capable platform for four transparent sprite strips, `pet.json` and `README-INSTALAR.md`; code-capable platforms with repository access may also run the delivery pipeline. If only images are returned, follow the [manual preparation steps](../README.md#crie-seu-próprio-pet-com-sua-imagem). The [create-pet skill](../skills/virapets-create-pet/SKILL.md) and [universal prompt](../skills/virapets-create-pet/references/prompt.md) describe the full contract.

## What each download contains

| Download | Contents | Use |
|---|---|---|
| **Baixar meu companheiro · ZIP** | `assets/pets/<id>/pet.json`, four `sprites/{happy,barking,waiting,sleeping}.png` strips, recipe and installation README | Copy the pet directory into a working clone, then run `deliver`/`validate` |
| **PNG deste humor** | One transparent RGBA strip, 2048×256, eight 256×256 cells | Sprite source for the selected mood; a PNG strip is not an animated GIF |
| **Salvar receita JSON** | Procedural settings or derived photo pixel art with head marking | Resume with **Importar JSON**; recipes are validated and photo recipes have a larger size allowance |
| **Baixar figurinhas animadas** | A `.wastickers` archive with four transparent animated 512×512 WebPs, cover and author metadata | Open in an Android app compatible with animated `.wastickers` packs |

All four photo PNGs include their animated bark/sleep effects; their manifest has `sleepSigns` entries set to `null` to avoid adding Zzz twice. Procedural PNGs leave sleep letters to the pipeline. Both exports retain eight PNG cells per mood. Keep the manifest provided with your ZIP.

Sticker export requires browser Canvas WebP support. If it fails, save PNG/ZIP/JSON and use the Python pipeline. Browser WebP encoding may alter colors through lossy compression; Python `deliver`/`stickers` provides the project's lossless export and validation path. `.wastickers` is an importer format, not an official WhatsApp installation API. Downloading the pack does not install it into WhatsApp; dragging an animated WebP into WhatsApp Web is not equivalent. Android importer/device testing has not been performed.

## Turn the ZIP into GIFs, a gallery and an optional Claude pet

Use a working clone rather than an installed plugin cache, which an update may replace. Repository access is required. For an example package with ID `luna`:

```sh
git clone https://github.com/viralabs-dev/virapets.git
cd virapets
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r tools/requirements.txt
```

On Windows create the environment with `py -m venv .venv` and activate with `.venv\Scripts\activate` in Command Prompt. Then use the same `python -m pip` and pipeline commands.

Extract the ZIP and copy `assets/pets/luna/` into the clone's `assets/pets/luna/`, preserving all other pets. Do not run `new` for a package that already includes `pet.json`. Replace `luna` below with your actual package ID:

```sh
python tools/pets.py deliver --pet luna --output outputs/luna/animation-luna.html
python tools/pets.py validate --pet luna
```

Open `outputs/luna/animation-luna.html`. The offline gallery features Luna first, followed by Jojo, Mel and Dara, with individual GIFs, a GIF ZIP and sticker packs embedded for download. If the package already contains validated GIFs/stickers, regenerate only the gallery with `python tools/pets.py gallery --featured luna --output outputs/luna/animation-luna.html`. After changing your own art, repeat `deliver` with `--force` to replace its existing delivery.

To add Luna to the Claude Code panel, optionally run:

```sh
python tools/pets.py build --pet luna --featured luna --output outputs/luna/animation-luna.html
claude plugin validate .
claude plugin test .
claude plugin install virapets --marketplace . --scope user
```

Keep one ViraPets installation active; see [installation and migration](../README.md#instalação-e-migração). Then use `/reload-plugins`, `/virapets luna` or `/virapets luna sleeping` in Claude Code. `build` updates the generated catalog; no hook editing is needed. GIFs, the gallery and stickers work without this optional panel step. The installed plugin runtime does not require Python.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Model does not start | Use the published HTTPS page or localhost HTTP; file opening can block module Workers. Retry, cancel/release, or use manual brushes. |
| Only part of the animal is selected | Add positive points across head/body and negative background points, or use keep/erase brushes. |
| Pixelization says the mask is empty | Restore visible pixels with the keep brush or **Manter tudo** before applying. |
| Rays/Zzz appear in the wrong place | Mark the head again on the final art, adjust size and muzzle direction, then simulate. |
| Retouches disappeared | Reapplying pixelization regenerates from the source/mask. Import the saved recipe if available. |
| Imported recipe cannot redo the crop | Recipes omit the source photo/mask. Choose the source photo again to recut. |
| Clipboard or sticker download fails | Copy/select the prompt manually; save ZIP/PNG/JSON and use the local pipeline for stickers. |
| Pet is absent from the Claude panel | Generate delivery, validate, then run `build` and reload the correct local plugin installation. |

## Local development, validation and publication

The Studio files are published in the personal Pages repository. The plugin repository contains its Python pipeline and guides; its `site/` directory does not contain the complete runnable website. To serve the public website locally:

```sh
git clone https://github.com/daneiel/daneiel.github.io.git virapets-site
cd virapets-site
python3 -m http.server 8000
```

Open `http://localhost:8000/virapets/`. Use HTTP for the photo Worker/model. Python is only a convenient server here, not a visitor requirement. Public JS modules are in `virapets/`; the model notices are distributed with them.

The development checkout also retains Node unit tests and a Playwright mode-regression script; these are not all shipped in the public plugin checkout. Do not run missing `site/*.test.cjs` files from that checkout. Recorded [public browser evidence](../docs/validation/mode-regression-public.json) covers the published layout. The [Portuguese published guide](../docs/design/studio-published.md#evidências-e-limites-reais) separates current and historical validation. Desktop viewports are not physical-phone tests; Firefox, Safari, real devices and Android sticker import remain untested.

The published files live in `virapets/` of [daneiel/daneiel.github.io](https://github.com/daneiel/daneiel.github.io/tree/main/virapets). GitHub Pages serves that repository's `main` root. Editing this ViraPets repository does not automatically publish the personal site. A reviewed publication must copy all referenced static resources, including themes, favicon, prompt, photo modules, Worker, vendor runtime and notices, keeping relative paths intact, then verify the Pages deployment and public URL. There is no cross-repository synchronization workflow. Roll back by reverting the publication commit in the site repository; preserve its root page. Publishing the static page does not publish plugin commits.


## Inline active mode and selection

The creator stays open inline on the page with a visible mode selector. The entire procedural section, including its instructions, is hidden and inert in photo mode. The same shared preview/export node moves inside the photo editor once pixel art exists; no empty Pingo card or export form appears below an unfinished photo. Recipe import remains available above both modes. Switching preserves the photo, mask, head marker and procedural configuration. The page has no editor dialog or focus trap. The theme button in the header uses a sun/moon icon, action text and an accessible name. Object mode prefers a broader credible SAM candidate; detail mode prefers score. Positive/negative points remain spatial prompts, with add/subtract area operations and manual brush fallback. Pet/background inverse selection, color/transparent fill, grow/shrink/smooth and mask undo/redo run locally. The source photo is never modified.

Cutout preview interpolates motion; animated stickers use 32 frames per mood, while PNG strips retain 8. Head marking follows transformed final-art coordinates. Effects are baked into photo PNGs with null sleepSigns to avoid duplication; head guides are never exported.
