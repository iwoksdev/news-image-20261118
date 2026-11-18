# Bundled fonts

Static instances of Google Fonts variable fonts, subset to Latin + punctuation
so the renderer is self-contained (the sandbox has no Noto fonts installed).

| File | Source (google/fonts, ofl/) | Axes |
|---|---|---|
| NotoSerif-Regular/Bold/ExtraBold/Italic.ttf | notoserif | wght 400/700/800, wdth 100 |
| NotoSans-Regular/Bold.ttf | notosans | wght 400/700, wdth 100 |
| NotoSerifDisplay-Black.ttf | notoserifdisplay | wght 900 |
| PlayfairDisplay-Black.ttf | playfairdisplay | wght 900 |

All fonts are licensed under the SIL Open Font License 1.1
(https://openfontlicense.org). Instanced with `fontTools.varLib.instancer`
and subset with `pyftsubset`.
