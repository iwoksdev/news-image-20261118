# Bundled fonts

Static instances of Google Fonts, subset to Latin + punctuation so the
renderer is self-contained (the sandbox has no system fonts installed).
Three families only (the NYT-style role split: display serif / text serif /
grotesque labels).

| File | Source (google/fonts, ofl/) | Role | Axes |
|---|---|---|---|
| PlayfairDisplay-Bold/ExtraBold/Black.ttf | playfairdisplay | masthead, headlines, stat numbers | wght 700 / 800 / 900 |
| PTSerif-Regular/Bold/Italic.ttf | ptserif | deks, body, index; italic subtitle | static |
| Inter-Regular/SemiBold/Bold.ttf | inter | tracked-caps labels, kickers, folio | wght 400 / 600 / 700, opsz 14 |

All fonts are licensed under the SIL Open Font License 1.1
(https://openfontlicense.org). Instanced with `fontTools.varLib.instancer`
and subset with `pyftsubset`.
