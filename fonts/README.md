# Bundled fonts

Static instances of Google Fonts variable fonts, subset to Latin + punctuation
so the renderer is self-contained (the sandbox has no Noto fonts installed).

| File | Source (google/fonts, ofl/) | Axes |
|---|---|---|
| NotoSerif-Regular/Bold/ExtraBold/Italic.ttf | notoserif | wght 400/700/800, wdth 100 |
| NotoSans-Regular/Bold.ttf | notosans | wght 400/700, wdth 100 |
| NotoSerifDisplay-Black.ttf | notoserifdisplay | wght 900 |
| PlayfairDisplay-Black/ExtraBold/Bold.ttf | playfairdisplay | wght 900 / 800 / 700 |
| EBGaramond-Regular/Medium/SemiBold/Italic.ttf | ebgaramond | wght 400 / 500 / 600, italic 400 |
| DMSerifDisplay-Regular/Italic.ttf | dmserifdisplay | static |

All fonts are licensed under the SIL Open Font License 1.1
(https://openfontlicense.org). Instanced with `fontTools.varLib.instancer`
and subset with `pyftsubset`.
