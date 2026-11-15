# Notas técnicas: Premiere via MCP Bridge e ExtendScript

Tudo aqui foi testado entre 10 e 19/10/2026 (Premiere 26.5). Acrescente o que descobrir de novo.

## Ritmo e segurança
- Timeline pesada (mais de 300 clipes): lotes de **~20 operações**, um por vez, conferindo a contagem. Paralelo derruba o Bridge.
- Antes de mexer, confirme `app.project.activeSequence` e use sempre o ID da sequência (o usuário troca de aba).
- **Ao trocar um clipe por uma versão nova, use a posição atual do clipe antigo** (procure pelo nome na hora), nunca uma minutagem guardada: ele redecupa entre rodadas e tudo desliza.

## Padrão de script
- Escreva o `.jsx` no scratchpad com `function main(){...}` e chame `$.evalFile(lib.jsx); $.evalFile(script.jsx); return main();`. O `evalFile` sozinho devolve `undefined`.
- Acentos dentro de `.jsx`: use escapes `á` (o evalFile não lê UTF-8).
- Erros: `try{...}catch(e){return 'ERR '+e+' line '+e.line}`.
- Arquivos escritos pelo ExtendScript saem com `\r`: `tr '\r' '\n'`.
- `eval` e `JSON` são barrados pelo Bridge: trate JSON como string (regex).

## Unidades
- Tempo: `Time.seconds`; ticks = 254016000000 por segundo (`importMGT` quer ticks **como string**).
- **Motion Position e Anchor são normalizados (0–1)**, inclusive no `set_clip_position` do Bridge, que **não** usa pixels.
- Fill: escala = `max(W_seq/w, H_seq/h)·100`. Para enquadrar no rosto mantendo o Fill: `pos = 0,5 + (anchor − 0,5)·dim·scale/frame`.
- Still: a escala é relativa ao quadro (num 1080 de largura, 100% = largura do quadro). Pra cobrir a metade de cima de um 9:16: escala = 88,9 × w/h.
- Stills começam em tempo de mídia 3600 s (o inPoint de um PNG não é 0).
- `split_clip` usa tempo relativo ao clipe: prefira `razor_timeline_at_time`.
- `add_to_timeline_batch` com sourceIn/Out em still deixa 1 frame a menos: corrija com `trim_clip`.
- Label: `set_color_label` no **item do projeto** antes de pôr na timeline (Rose = 6, Mango = 7, Magenta = 11).

## Leitura
- Transcrição: dentro do .prproj (gzip), em `<TranscriptData Encoding="base64">`, uma por mídia. Os in-points dos cortes ficam em AudioClipTrackItem → SubClip → AudioClip `<InPoint>`. Use `scripts/transcricao.py`.
- Texto de Graphics (Essential Graphics) não é legível por script: exporte frames.
- Clipes feitos com o **Remix** aparecem sem projectItem (null).
- Ler o XML do .prproj direto (gunzip) é útil pra projetos com mídia offline ou de outro computador.

## Escrita
- Colocar: `item.setInPoint(t,4); item.setOutPoint(t2,4); track.overwriteClip(item, start)` e depois `clearInPoint/clearOutPoint`. **Sempre** com in/out, senão o clipe apaga o resto da faixa. O overwrite encaixa no frame: procure o clipe colocado com tolerância de ~0,05 s.
- Mover: `clip.move(T(delta))`. `clip.start = T(x)` estica a cabeça sem mudar o inPoint (acerte com `clip.inPoint`). `clip.end = T(x)` apara o fim. Apagar: `clip.remove(false,false)`.
- **Não dá pra copiar um clipe da timeline** (Graphic, nest colado, etc.): o script só coloca **itens do projeto**. Para um conjunto pronto do usuário (ex.: transição em Graphics), deixe marcadores "Colar …" e ele cola com Cmd+V; ou peça que ele transforme o conjunto numa nested sequence, que vira item do projeto.
- **Nunca una `Graphic`** ao juntar picotes: todos têm o mesmo nome e textos diferentes.
- Faixas novas: QE `seq.addTracks(nVideo, idxV, nAudio, 1, idxA, 0, 0)`. Inserir faixas desloca os índices das de cima.
- Marcadores: `seq.markers.createMarker(t)`, depois `name`, `comments` e `end` (em segundos). `m.end = T(...)` derruba o script.
- Volume: `db()` da `lib.jsx`. Níveis por keyframe com `lvl()`.

## Efeitos (só via QE)
- `qe.project.getVideoEffectByName('Transform' | 'Gaussian Blur' | 'Gaussian Blur (Legacy)' | 'Lumetri Color' | 'Lens Distortion')` + `qeItem.addVideoEffect(fx)`. O QE só funciona na **sequência ativa**; o DOM funciona por nome.
- matchNames: Transform = `AE.ADBE Geometry`; Gaussian Blur = `AE.ADBE Gaussian Blur 2` (o "Gaussian Blur" novo aparece como `AE.Impact_Blur_FX`, com `Amount`); Lumetri = `AE.ADBE Lumetri`; Opacity = `AE.ADBE Opacity`; Motion = `AE.ADBE Motion`.
- Transform da Adjustment Layer: ligue `Uniform Scale` e anime `Scale Height`. Desligue "Use Composition's Shutter Angle" para usar `Shutter Angle` próprio.
- Lumetri por índice: 14 temp, 15 tint, 16 sat, 20 contraste, 21 highlights, 22 shadows, 23 whites, 24 blacks, 40 faded, 42 vibrance, 43 sat criativa, 110 vinheta, 113 feather.
- Crop: está no componente Motion em alguns projetos ("Crop Top/Bottom") ou como efeito Crop; leia com `prop()` antes de setar.

## Keyframes
- **Nunca lineares.** O ExtendScript não ajusta alças de bezier: grave a curva frame a frame (`scripts/ease.py` → `ease.json`, `setKeys`).
- `set_keyframe_interpolation` do Bridge **zera o valor do keyframe**: não use. `setInterpolationTypeAtKey(t,5)` (bezier) funciona no DOM, mas as alças ficam no padrão.
- `setTimeVarying(false)` apaga os keyframes antigos.

## Texto
- `add_text_overlay` com Basic Title.mogrt diz que funcionou, mas renderiza vazio.
- **Texto editável funciona** com um .mogrt **feito no After Effects**: `seq.importMGT(caminho, String(seg*254016000000), vIdx, aIdx)` + `clip.getMGTComponent()`. A propriedade de texto devolve JSON: troque `"textEditValue":"..."` e `"fontEditValue":["Inter-Black"]` por regex e `setValue(v,true)`.
- .mogrt feito no Premiere vira Graphic nativo, com `Source Text` binário: qualquer `setValue` deixa em branco.
- Alternativa sempre segura: PNG gerado em Swift/AppKit.

## Limitações (não tente, avise)
- **Adjustment Layer não se cria por script** (o `add_adjustment_layer` gera um PNG transparente inútil). Peça para criar pela UI; depois ache com `item.isAdjustmentLayer()`.
- Aplicar preset (.prfpset) ou Remix: leia o preset e reproduza os valores.
- Transições de áudio (Cmd+Shift+D) não são confiáveis por script.
- Legendas (caption track) o Bridge não lê nem move: gere uma lista de ajustes para ele aplicar.
- Cor de clipe já na timeline: só pela UI.
- Área de transferência (Cmd+C/Cmd+V) não funciona em segundo plano.

## SFX (picos medidos, em s desde o início do arquivo)
Impact 01 = 0,34 · 02 = 0,54 · 03 = 0,20 (**banido**, "parece um sino") · 04 = 0,66 · 05 = 0,94 · Woosh 01 = 0,40 · 02 = 0,42 · Riser Long 01 = 2,40 · 02 = 1,94 · 03 = 4,80 · 04 = 5,52 · 05 = 4,48 · Riser Super 01 = 1,84 · Riser Sword = 1,70 · Kodak shutter = 0,30 · Vocal Cadence = 5,4. Posicione com início = corte − pico.

## Ferramentas locais
- `afconvert`/`afinfo` (macOS) para áudio; Swift + AppKit/Vision/AVFoundation para imagem, rostos e vídeo.
- `~/.local/bin/yt-dlp`, `~/.local/bin/ffmpeg`, `~/.local/bin/ffprobe`, `~/.local/bin/gh` (todos fora do PATH).
- Fontes: Inter Bold/Italic/Medium/SemiBold em `~/filmcraft/assets/fonts/` (sem Inter Black: use Bold + stroke −4,5).
- Sem PIL, sem fontTools instalados. Não instale pacotes sem pedir.

## Aprendido em 20/10/2026 (Calibase, Micro VSL ganchos)
- `verify_premiere_connection` sempre devolve `readOnly: true` (está fixo no código do Bridge, em discovery.js). Não quer dizer que o projeto está travado.
- **PROIBIDO subclipe na timeline (regra do Juliano, 01/11/2026):** `createSubClip` trava a duração e ele não consegue esticar o clipe. Sempre coloque o arquivo inteiro com in/out. B-roll sem áudio: baixe só imagem (`bv*`) e coloque o item original; se o arquivo tiver áudio, remova o áudio do clipe na timeline depois.
- Ao colocar várias vezes o mesmo item: `setInPoint(0,4)`, `setOutPoint(fim,4)`, `setInPoint(inicio,4)`, nessa ordem. Com o in/out anterior ainda ativo, o overwrite pode não colocar nada e não dá erro: confira a contagem. `clearOutPoint` nem sempre limpa; não afeta esticar o clipe na timeline.
- `getMediaPath()` pode vir com `/Volumes/Macintosh HD` na frente e com acento decomposto (NFD). Para achar um item pelo caminho, compare sem esse prefixo e sem acentos.
- `importFiles` às vezes não importa nada e mesmo assim devolve true: confira a contagem do bin depois.
- PNG regerado com o mesmo nome só atualiza no Premiere depois de `item.refreshMedia()`.
- A Poppins da Adobe Fonts fica em `~/Library/Application Support/Adobe/CoreSync/plugins/livetype/.r/.37522.otf`. Registre com `CTFontManagerRegisterFontsForURL` para usar no Swift.

## Aprendido em 21/10/2026 (CHZ, matéria da Vans)
- **Não usar WKWebView (Swift) para print de site**: dispara pedido de senha do Keychain no Mac do Juliano. Para matéria, baixe o HTML com `curl` e monte o cartão com o texto literal; sites com Cloudflare (shop-eat-surf, fashionista) bloqueiam curl.
- Recorte de produto sem fundo: Vision `VNGenerateForegroundInstanceMaskRequest` + `generateMaskedImage(... croppedToInstancesExtent: true)` funciona bem em tênis.
- `NSBitmapImageRep` lido de PNG não aceita `setColor`: desenhe num rep novo RGBA e mexa em `bitmapData`.
- **Frame fantasma (21/10/2026):** 88 de 129 fotos tinham início/fim fora da grade de frames (tempos em segundos tipo 168,001) e havia 45 vãos de fração de frame entre fotos coladas. Correção na `lib.jsx`: `snapTicks(seg)` arredonda para `Math.round(seg*254016000000/timebase)*timebase`, `TT(ticks)` cria o Time por ticks e `place()` usa os dois. Para conferir: `Number(clip.start.ticks) % Number(seq.timebase) == 0` em todos e `(start − end anterior)/timebase` nunca entre 0 e 3.

## Aprendido em 30/10/2026 (CHZ, 10 itens)
- Still com `place()` sem inPt coloca a duração inteira: use `item.setInPoint(0,4); item.setOutPoint(dur,4)` (JPG importado vem com in=0, out=5) e depois `c.end=TT(en)`. Com folga zero o clipe não come o vizinho.
- `refreshMedia()` em lote (39 itens de 4K, com a sequência aberta) deixou o Bridge sem resposta e o Premiere a 100% de CPU. Faça em lotes pequenos, um por vez.
- Sem mexer no ExtendScript dá pra ler os cortes: `AudioClipTrackItem` (Start/End) → `SubClip` → `AudioClip` `<InPoint>` no XML do .prproj.

## Aprendido em 22/10/2026 (deLegenda no deCupagem)
- Legenda nativa a partir de SRT: `importFiles([srt], true, bin, false)` e `seq.createCaptionTrack(item, 0, Sequence.CAPTION_FORMAT_SUBTITLE)` funcionam no 26.5. O DOM não expõe as faixas de legenda (`seq.captionTracks` não existe): confira pelo `exportFramePNG`, que mostra a legenda. SRT com BOM UTF-8 mantém os acentos.
- `execute_extendscript` recusa script inline com `eval(...)` ("Script validation failed"): grave um `.jsx` com `function main()` e chame `$.evalFile(lib); $.evalFile(teste); return main();`.
- **`place()` come 0,2 s do vizinho (27/10/2026):** o out-point vai com +0,2 s de folga e o `overwriteClip` apaga esse pedaço do clipe que já estava logo depois; o `place` corta o fim do novo, mas o início do vizinho fica comido (vão de ~4 frames). Ao colocar um clipe colado **antes** de outro já existente, depois devolva o início do vizinho: `viz.start = TT(novo.end.ticks)` e confira que o `end` dele não mudou.
- **Vários projetos abertos:** `app.openDocument()` abre outro .prproj e o torna `app.project`; `app.projects[i].sequences` de um projeto que não é o ativo vem vazio. O `path` volta com acento decomposto (NFD): compare pelo `name`. Feche com `closeDocument(0,0)` (sem salvar). O texto de Graphics não sai pelo `getValue()` (vem binário): leia o `InstanceName` do componente Text no XML do .prproj.

## Aprendido em 01/11/2026 (Reels Felipe, Sidemen/Red Bull/Cleo)
- Folha de contato com `-skip_frame nokey` mostra o keyframe anterior, não o tempo do rótulo (erro de vários segundos). Para escolher in-point, confira o frame exato com `-ss t`.
- Neste projeto o still entra em pixels reais (escala 100 = tamanho do arquivo), não ajustado ao quadro. Cobrir a metade de cima: `max(1080/w, 960/h)·100`; inteira: `min(0,92·1080/w, 860/h)·100`. Teste um clipe antes do lote.
- Tela dividida com zoom em Adjustment Layer acima do Felipe: desligue o clipe do zoom (`clip.disabled=true`) nos cortes com B-roll; senão ele desloca o Felipe.
- `tile` do ffmpeg zera ao mudar o formato do pixel entre imagens: use `format=rgb24` + `xstack`.

## Aprendido em 01/11/2026 (Bruno, B-rolls da Leva 01)
- `download_file_content` do Drive: acima de ~500 KB a resposta vai para um arquivo em `tool-results/` (JSON com `content` em base64 e `title`). Decodifique com Python. Limite de 10 MB por arquivo; link público `uc?export=download` não serve para pasta privada.
- Mover projeto aberto: `app.project.saveAs(caminho)` troca o projeto de lugar sem quebrar nada; depois mova o `.prproj` antigo para `99. Temp`.
- `tile` do ffmpeg também zera quando o tamanho do frame muda (vídeo 4:3 no meio): normalize cada JPG antes de montar a folha.

## Aprendido em 02/11/2026 (Bruno, legendas da Leva 01)
- Script não edita nem apaga faixa de legenda. `createCaptionTrack` sempre cria faixa nova ao lado das antigas, então confira o SRT inteiro **antes** de importar. O `exportFramePNG` mostrou só a faixa mais nova, e ele grava com `.png` duplicado se o caminho já terminar em `.png`.

## Aprendido em 02/11/2026 (Bruno, ajustes de split e cortes)
- `duplicate_sequence` deixa a **cópia** como sequência ativa: volte com `app.project.openSequence(id)` e edite sempre pelo ID.
- Mover a cabeça de um clipe: `clip.start = ...` e depois `clip.inPoint = in + delta`. Sem checar, o in de `07 color.mp4` foi para −0,033 s: corrija para 0.
- As legendas do .prproj ficam em `CaptionDataClipTrack` → `CaptionDataClipTrackItem` (`Start`/`End` na timeline) → `SubClip` → `TranscriptClip` (`InPoint`/`OutPoint`); o texto e o estilo ficam no `Block`. Dá para ler as legendas atuais daí; o SRT antigo fica defasado depois da decupagem.
- **Mover legenda sem perder estilo (testado):** numa cópia do `.prproj` (gunzip, patch, gzip), some o mesmo delta em `End`+`OutPoint` da legenda e `Start`+`InPoint` da seguinte. Ache a faixa pela sequência (`Sequence` → `TrackGroup` → `Track ObjectURef`). A cópia abriu no Premiere com estilo e texto intactos. Para conferir: `exportFramePNG`.

## Aprendido em 30/10/2026 (CHZ, .mogrt do After Effects)
- `.mogrt` feito no AE funciona por script: `seq.importMGT(caminho, String(ticks), vIdx, aIdx)` (~0,15 s) e `clip.getMGTComponent().properties`. Texto: troque `"textEditValue"` por regex e `setValue(v,true)`, com `\r` para quebrar linha. Checkbox e slider aceitam `setValue` direto.
- **Cor parcial num campo só:** expressão no Source Text que tira os `[colchetes]` e faz `thisProperty.style.setText(limpo).setFillColor(cor, inicio, n)`.
- Rodar script no AE: `osascript` + `DoScriptFile`. AE em português: use `effect("X")(1)`, não `("Slider")`/`("Checkbox")`. Sem "Permitir scripts gravar arquivos" o script trava; exporte pelo botão do painel Gráficos essenciais (pede salvar o .aep antes). Slider publicado fica limitado a 0–100.
- Cliques em segundo plano não funcionam no AE: precisa de controle de tela.
- `importMGT` entra com a duração inteira do template e apaga o que vem depois na faixa: limpe a faixa e coloque do início para o fim. Máscara e modo de mesclagem dentro do `.mogrt` são ignorados no Premiere: desenhe o buraco na própria forma. `exportFramePNG` logo depois do import pode sair incompleto.
- Texto em `.mogrt` centralizado por `sourceRectAtTime` muda de altura conforme acento e descendente. Fixe a linha de base: `y = centro - (linhas-1)*entrelinha/2 + 0,364*tamanho`. Slider publicado vai de 0 a 100: multiplique na expressão para dar folga acima do padrão.

## Aprendido em 04/11/2026 (Felipe TH, marca-texto)
- **Modo de mesclagem por script:** Opacity → `properties[1]` ("Blend Mode", o primeiro dos dois). Normal = 18, **Multiply = 17**, Darken = 3, Difference = 5, Hardlight = 8, Lighten = 11, Add = 14. O segundo "Blend Mode" (`properties[2]`) não muda nada. Para descobrir outro código: `seq.exportAsFinalCutProXML(caminho,1)` e procurar `<compositemode>`.
- `exportFramePNG` reflete o modo de mesclagem na hora. Muitos `exportAsFinalCutProXML` seguidos derrubam o Bridge: um por chamada.
- Revelar da esquerda pra direita ("passar o marca-texto"): keyframes em Motion → `Crop Right` (em %), com a curva do ease.
- Keyframe hold: `prop.setInterpolationTypeAtKey(t, 4, true)` depois de criar as chaves (4 = Hold; testado em 04/11/2026 com `getValueAtTime` no meio do intervalo). Útil pra trocar posição no meio de um clipe sem deslizar.
- Stills e vídeos entram em tamanho nativo (Scale 100 = pixels da mídia) quando o projeto não usa "Scale to frame size": escala de preenchimento = max(W/w, H/h)·100.

## Aprendido em 06/11/2026 (Reels Felipe, teste F1/Huberman)
- **Overwrite por cima de vídeo deixa sobra de 1 frame** do clipe de baixo (ex.: 97,567–97,600) quando o `put()` estica o `end` do novo. Depois de cada lote, procure clipes com menos de 0,05 s na faixa e remova.
- **Tela dividida ou cheia não se lê pelo valor exato da Position:** o Juliano reenquadra clipe a clipe (Y 0,62–0,79 dividida; 0,38–0,46 cheia). Use um limiar (Y > 0,6 = dividida), nunca o valor do padrão.
- Ele edita a V1 enquanto você trabalha (ripple de 2 frames muda tudo depois do ponto). Refaça o dump **antes** de calcular tempos de legenda/B-roll e compare a contagem com o anterior.
- Legenda em PNG: um PNG 2160×3840 por legenda, transparente, na escala 100 e Position (0,5; 0,5). 416 clipes em lotes de 60 (o último lote estourou os 45 s, mas terminou).

- **`place()` com folga comia o clipe seguinte (06/11/2026):** o out-point com +0,2 s fazia o `overwriteClip` cortar 4 frames do início do vizinho, e reduzir `c.end` depois não devolve. O `place()` agora usa a duração exata. Depois de colocar, procure vãos de 1–5 frames na faixa.
- **Marcadores:** `seq.markers` (getFirstMarker/getNextMarker) dá início, fim, nome e `comments`. O Juliano escreve os pedidos no comentário do marcador da sequência.

## Aprendido em 06/11/2026 (Calibase, aulas de Novembro)
- **`transcricao.py` erra com nomes de arquivo repetidos** (várias falas "Video falado.MOV" ou "Parte 1.MOV" de pastas diferentes): casa tudo com o mesmo bloco. Cada `<TranscriptData>` fica num `ExternallyProvidedTranscriptDocument` logo depois do `AudioMediaSource` da mídia; pegue o `<Media ObjectURef>` desse AudioMediaSource e leia o caminho em `<Media ObjectUID=...>` → `ActualMediaFilePath`. Assim cada transcrição vai pra pasta/arquivo certo.
- **`qe ... exportFramePNG(T(s).ticks, ...)` devolveu o mesmo frame para todos os tempos** (playhead), sem erro. Para conferir pontos da timeline use a ferramenta `export_frame` do Bridge (sequenceId, time em segundos, outputPath), uma chamada por frame.
- `createNewSequenceFromClips(nome,[item],bin)` cria a sequência com as configurações do clipe; depois remova o clipe e monte do zero.
- B-roll de vídeo colocado com `overwriteClip` na V2 leva o áudio pra A2: remova os clipes da A2 depois (B-roll entra só com imagem).

## Aprendido em 08/11/2026 (FRS, 8 vídeos de novembro)
- Sequência vertical a partir de clipe de iPhone: `createNewSequenceFromClips` dá 1080×1920 mas com timebase de 29,996 fps. Corrija: `st=s.getSettings(); t.ticks="8467200000"; st.videoFrameRate=t; s.setSettings(st)` (30 fps exatos).
- Escala no quadro 1080×1920: MOV 1080p girado = 100, MP4 720p do SharePoint = 150, 4K = 50. JPG de iPhone já entra preenchendo.
- .mogrt feito pelo MCP do After Effects (`egp.add_property` + `egp.export_mogrt`, sem eval) funciona no `importMGT`; o texto troca pelo regex do `textEditValue` e mantém a fonte. Caixa que acompanha o texto: expressão `sourceRectAtTime` no Size/Position do retângulo. Ao criar texto pelo MCP do AE, desligue `allCaps` e `applyStroke` (vieram ligados).
- `app.quit()` pelo ExtendScript fecha o Premiere (salve antes).
- **Correção do Juliano (08/11/2026):** `createNewSequenceFromClips` com clipe de iPhone cria a sequência em **Rec. 2100 HLG**. Errado. Crie sempre pelo preset `Social Media Portrait 9x16 30 fps` (BT.709, 30 fps, 1080×1920): `app.enableQE(); qe.project.newSequence(nome, "/Applications/Adobe Premiere Pro 2026/Adobe Premiere Pro 2026.app/Contents/Settings/SequencePresets/Social/Social Media Portrait 9x16 30 fps.sqpreset")`. Confira com `s.getSettings().workingColorSpace.name` == "Rec. 709". Os clipes HLG ficam com tom correto nela.

## .mogrt: variações de cor e testes (aprendido em 08/11/2026, cartelas Vivi)

- **Mudar a cor por script no After não muda o padrão do controle do Essential Graphics.** O AE guarda o valor de cada controle separado (`CVal`/`CDef` no .aep) e o Premiere lê o padrão de `definition.json › sourceInfoLocalized › capsuleparams › capParams[].capPropDefault`. Exportar V1/V2/V3 da mesma comp só trocando cores sai tudo com a cor da V1. Comp duplicada (`comp.duplicate`) zera os padrões (preto e slider 0).
- Solução usada: exportar e depois gravar as cores nos 3 lugares (`clientControls[].value`, `capPropDefault` e `CVal`/`CDef` do .aep dentro do `project.aegraphic`, floats big-endian RGBA) + `capsuleID` novo. Script de exemplo na sessão de 08/11 (`patch_mogrt.py`).
- Para testar no Premiere, **importe com capsuleID novo**; o mesmo ID reaproveita o item antigo do projeto.
- Texto de mogrt pelo Bridge: `set_effect_property` (componente "Graphic Parameters") com o **JSON completo** (fonte, tamanho, `fontTextRunLength`) e só trocar `textEditValue`; mandar só `{"textEditValue":...}` faz o texto sumir.
- **`remove_from_timeline` é ripple por padrão**: fecha os vãos de todas as faixas (inclusive V1/A1). Sempre passe `deleteMode: "lift"`.

## Aprendido em 08/11/2026 (entrevista Watchfolio)
- **Não confie no índice da faixa entre um script e outro.** O Juliano duplicou a V1 na V2 e subiu a moldura pra V3 no meio do trabalho; o script seguinte mexeu em `videoTracks[1].clips[0]` achando que era a moldura e esticou o clipe dele. Procure o clipe **pelo nome** (`clip.name`) e liste as faixas antes de cada lote.
- `createNewSequenceFromClips` + `place()` deixou 1 frame de vão na A1 entre dois cortes (o áudio terminou em 452,2333 e o próximo começa em 452,25, a 60 fps). Depois de colocar, confira o fim de cada clipe de áudio contra o início do seguinte.
- **Regerar um .mov (ProRes) com o mesmo nome enquanto o Premiere usa o arquivo deixa o clipe branco**, mesmo sem ficar offline e mesmo com `changeMediaPath` pro mesmo caminho. PNG relinka normal; vídeo não. Para vídeo, gere com `_v02` e faça `item.changeMediaPath(novo,true)`: mantém posição, duração e efeitos do clipe. O arquivo antigo vai pra `99. Temp`.

## Aprendido em 09/11/2026 (Vivi, cartelas Divorce Stories da Camille)
- **Abrir projeto com mídia em HD externo sem travar no Link Media:** gunzip do .prproj, troque `<ActualMediaFilePath>`/`<FilePath>` pelos caminhos locais (casando pelo nome do arquivo), gzip e abra com `app.openDocument(caminho,true,true,true,true)` (o 3º `true` pula o diálogo de localizar). O que não existe fica offline sem diálogo.
- **Dois projetos abertos:** `app.project` continua sendo o primeiro, e as ferramentas do Bridge (`export_frame`, `list_sequences`) só enxergam ele. Nos scripts, pegue o projeto por nome em `app.projects` (função `PRJ()`); fechar o outro com `closeDocument` foi bloqueado pelo classificador.
- **`seq.clone()` não põe a cópia no fim de `sequences`:** a lista é ordenada por ID. Pegue a cópia comparando os IDs antes/depois; nunca renomeie `sequences[numSequences-1]` (renomeei a sequência errada assim).
- **Cor de .mogrt por script:** `getValue()` devolve um inteiro empacotado e copiar esse número com `setValue` troca os canais (saiu ciano). Use `prop.setColorValue(255, r, g, b, true)`.
- **Conferir mogrt/faixas de cima:** o `exportFramePNG` do QE só devolveu a V1 no cursor. Funciona: `seq.setInPoint/OutPoint` + `seq.exportAsMediaDirect(mp4, ".../systempresets/4E49434B_48323634/01 - Match Source - Medium bitrate.epr", 1)` e frames com ffmpeg.
- Drive local (`~/Library/CloudStorage/.../Drives compartilhados`) deu "Operation timed out" em tudo. Acima de 10 MB o conector também recusa; arquivo de Drive compartilhado por link baixou com `curl -L "https://drive.usercontent.google.com/download?id=ID&export=download&confirm=t"`.

## Aprendido em 11/11/2026 (Calibase, .mogrt de texto feito por script no After 2026)
- Rodar script no AE: `osascript -e 'with timeout of N seconds' -e 'tell application "Adobe After Effects 2026" to DoScriptFile "x.jsx"' -e 'end timeout'`. Retorno `1` imediato = o AE está com janela modal aberta e recusou o script; peça para o Juliano fechar. Grave log em arquivo a cada passo (o script às vezes morre sem cair no catch).
- Antes de `addToMotionGraphicsTemplateAs`: `comp.openInViewer(); comp.openInEssentialGraphics();` e confira `canAddToMotionGraphicsTemplate(comp)`. Se for false e você adicionar mesmo assim, o AE abre um aviso modal e trava.
- `exportAsMotionGraphicsTemplate` com projeto nunca salvo abre a janela de salvar (modal): salve o .aep antes (`app.project.save(File)`). O segundo argumento é tratado como **pasta**: passe a pasta de destino, senão ele cria uma subpasta com o nome do .mogrt. Export pode levar 2–4 min (miniatura); espere em vez de rodar outro script.
- Caixa alta: `td.allCaps=false` derruba o script; use `td.fontCapsOption = FontCapsOption.FONT_NORMAL_CAPS`.
- No Premiere, o JSON do Source Text do .mogrt aceita trocar `textEditValue` (atualize `fontTextRunLength` para o novo comprimento); `fontSizeEditValue` e `fontFSAllCapsValue` são ignorados. Tamanho = escala do Motion; para não tirar a Posição do quadro, mantenha a Posição do .mogrt no ponto desejado e ponha `Motion Position = 0,5 + (P − 0,5)·(1 − k)`.
- O clipe do .mogrt não passa da duração do comp do AE (texto some depois de 10 s num comp de 10 s): faça o comp longo (120 s). Como o `importMGT` entra com a duração inteira e apaga o que vem depois na faixa, coloque em **ordem cronológica** e apare cada um logo depois.
- **Nunca `importMGT` numa faixa que tem clipes depois do ponto:** ele entra com a duração inteira do modelo (120 s) e apaga tudo no caminho, mesmo que você apare logo depois (11/11/2026: sumiram dois textos 25 s adiante). Use uma faixa vazia daquele ponto em diante ou coloque em ordem cronológica; confira com `seguro()` antes.
- Ao acrescentar um controle novo nos Gráficos essenciais do AE, a ordem das propriedades do .mogrt no Premiere muda: sempre procure por `displayName`, nunca por índice.
- Textos com acento escritos por script às vezes saíram em mojibake ("Voc√™"): gere o .jsx com `json.dumps(..., ensure_ascii=True)` e confira o `textEditValue` depois.
- **Salvar com dois projetos abertos (11/11/2026):** `app.projects[i].save()` devolveu ok e não gravou nada (o arquivo ficou com 2 KB). Funcionou `saveAs(mesmo caminho)` com o projeto ativo; confira o tamanho e a hora do `.prproj` depois de salvar.

## Aprendido em 13/11/2026 (CHZ, Itens que me arrependi e New Balance)
- **Input LUT da Lumetri por script:** `properties[6]` aceita só o índice dos 8 LUTs técnicos que vêm no Premiere (1–11). LUT personalizado (.cube) não entra: gravar o caminho em `LUTAsset` (`properties[128]`) não muda a imagem, e a pasta `~/Library/Application Support/Adobe/Common/LUTs/Input` não entra na lista. Deixe para o Juliano pela UI (Input LUT › Browse).
- **Premiere trava em lote grande de fotos 4K + `importMGT`:** duas vezes o ExtendScript passou de 45 s e o Premiere parou de responder (logs UXP parados, CPU ~33%). Só voltou matando o processo. Use lotes de no máximo 3 fotos e `app.project.save()` entre eles.
- **Nunca mande duas chamadas `execute_extendscript` na mesma mensagem:** elas rodam juntas e derrubam o Bridge.
- Bruto da Sony ZV-E10: 23,976 fps, S-Log3/S-Gamut3.Cine. O Premiere interpreta como Rec.709 (sem detectar o log).

## Aprendido em 13/11/2026 (tarde): inserir no meio da timeline
- `trackItem.move(offset)` move o clipe mas **não leva as transições** (crossfades de áudio da A1 ficam no tempo antigo, caindo no meio dos clipes, e os cortes novos ficam sem). Depois de empurrar clipes, refaça as transições pelo QE: `qeTrack.getTransitionAt(i).remove()` nas que não estão em corte e `qeItem.addTransition(qe.project.getAudioTransitionByName('Constant Power'), true, '00:00:00:04', '00:00:00:00', 0.5, false, true)` nos cortes sem. Lotes de ~100 (cada add varre os itens; 200 passa de 45 s). Sem sobra de mídia o Premiere põe a transição terminando no corte (2 frames): é normal.
- `marker.start = Time` dá "Illegal Parameter type 16"; use número em segundos (`m.start = seg`).
- Antes de qualquer script que dependa de tempo, releia a timeline: o Juliano edita entre uma chamada e outra (em 13/11 ele tirou 3,6 s e o primeiro script abriu o vão no lugar errado).

## 14/11/2026 (leva Hyrox/Netão/GaryVee/a16z)
- `$.evalFile` de .jsx num caminho com acento ("Vídeos") passou a dar `IOError: File or folder does not exist` no meio da sessão, com `File.exists` = true. Guarde os .jsx gerados no scratchpad (caminho ASCII) e rode de lá. `eval()` dentro do execute_extendscript é barrado pelo Bridge ("Script validation failed").
- Premiere 27: o **Motion já tem Crop Left/Top/Right/Bottom** (propriedades do próprio Motion, em %). Use isso em vez de adicionar o efeito Crop pelo QE (o `addVideoEffect` do Crop não pegou).
- Vídeo de YouTube com tarja preta embutida: `ffmpeg -vf cropdetect` dá a área útil; escala pela área útil e Crop Top/Bottom no Motion.

## Aprendido em 15/11/2026 (Vivi, cartelas novas e sequência vertical de cortes)
- **`razor_timeline_at_time` erra em sequência clonada de 24 fps e passada para 30 fps** (`setSettings`): ele corta em `tempo × 0,8`, mesmo informando o timecode certo. Compense passando `tempo × 1,25` e confira as bordas com uma listagem dos clipes. As bordas ficam presas na grade da mídia aninhada (até ~0,13 s de diferença): ative os trechos com tolerância de 0,2 s.
- `open_project` num .prproj de outra versão cria uma cópia `Nome_1.prproj` (o original fica intacto) e devolve "did not activate", mas o projeto abre. Confira com `app.projects`.
- Projeto antigo com mídia em `Documents/deNoise/...`: troque os caminhos no XML (gunzip/gzip) para os brutos da leva antes de abrir, e não aparece o Link Media.
- Cor de `.mogrt` lida por `getValue()`: canais = bytes altos de cada 16 bits (A,R,G,B). Para copiar a cor do fundo para o logo, use `setColorValue(255,r,g,b,true)`.
- Com vários projetos abertos, `app.projects[i].save()` só grava de fato o projeto **ativo** (o outro volta sem erro e o arquivo não muda). Ative o projeto (`openSequence` de uma sequência dele) antes de `app.project.save()` e confira a data do arquivo.
