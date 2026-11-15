---
name: revisao-vivi
description: Revisão V1 → V2 dos vídeos longos da Vivi (canais Separ/SeparAções, Super/Superações e Divorce Stories) a partir das notas do Daniel. Lê a mensagem dele (minutagem + título de cartela, "manter", pedidos soltos e CORTE + minutagem), põe as cartelas novas (.mogrt) por cima das antigas, marca na timeline o que o Juliano resolve, monta a sequência vertical de cortes para Reels/TikTok com a marca d'água do @ do canal e confere tudo em frames. Use sempre que o Juliano colar alterações/revisão do Daniel de um vídeo da Vivi, pedir "troca as cartelas", "cartelas novas", "faz os cortes", "sequência de cortes", "marca d'água do canal" ou a V2 de um vídeo Separ, Super ou Divorce Stories, mesmo que não cite esta skill. Não é a entrega V1 no Trello nem a publicação (upload-historias-divorcio), nem áudios (audios-separ-semana).
---

# Revisão Vivi (notas do Daniel → V2 + cortes)

Trate o Juliano de forma informal, em português. Carregue junto a `premiere-base`: o Bridge, o ExtendScript e as armadilhas técnicas estão lá. Aprovado em 15/11/2026 com Olivia Howell e Carrie (Divorce Stories).

## 0. Descobrir o canal

| Canal | Como reconhecer | Cartelas (.mogrt) | Logo por cima | @ da marca d'água |
|---|---|---|---|---|
| **Separ** (SeparAções) | pasta `02. Vídeos/01. Separ`, entrevista em português, card no board "YOUTUBE HISTÓRIAS DE DIVÓRCIOS" | `Separ_Nome_Vn` + `Separ_Cartela_Vn` | nenhum (o do .mogrt já é Separ) | `@separ.acoes` |
| **Super** (Superações) | pasta `02. Vídeos/02. Super`, nome com "SUPER" na frente, board "SUPERAÇÕES" | `Super_Nome_Vn` + `Super_Cartela_Vn` | nenhum | `@canalsuperacoes` |
| **Divorce Stories** | pasta `02. Vídeos/03. Divorce Stories`, entrevista **em inglês** | `Separ_*` com o logo do .mogrt escondido (Cor do logo = Cor do fundo) | `Logo_Divorce_Stories_roxo.png` na faixa de cima | `@storiesdivorce` |

- Mogrts: `Vivi/00. Assets/Templates/Vivi_Cartelas_Augusto/02_Mogrts/`. Logo DS: `Vivi/00. Assets/Logo Divorce Stories/`. Marcas d'água prontas: `Vivi/00. Assets/Marca dagua/arroba_<@>.png`. Se a pasta da Vivi não estiver neste Mac, use as cópias do repositório `denoise-revisao-vivi` (`assets/mogrts`, `assets/logo-divorce-stories`, `assets/marca-dagua`, `assets/fontes`). O `install.sh` deixa o caminho em `~/.claude/skills/revisao-vivi/assets`.
- **Cor:** se o nome usa a V1, o assunto usa a V2; nome V2 → assunto V3; nome V3 → assunto V1. Divorce Stories até agora: Nome V1 + Cartela V2.
- Se a pasta não deixar claro, pergunte o canal antes de mexer. Super com cartela nova ainda não foi feito: confira o resultado com ele no primeiro.

## 1. Ler as notas do Daniel

Ele anota em cima da V1, sem padrão de minutagem: `5` = ~5 min, `2526` = 25:26, `757` = 7:57, `400` = 4:00, `1:59` = 1:59. Os itens vêm em ordem cronológica, e é ela que desfaz a ambiguidade.

- **Número + título** (`20 - Taken by surprise`): troca o texto da cartela daquele minuto. A minutagem é aproximada, mas só há uma cartela por perto. É ~90% dos pedidos.
- **Número + "manter"**: a cartela fica com o título atual, no modelo novo. Cartela que ele **não cita** também fica com o título atual, e você avisa.
- **"Colocar cartelas novas"**: todas viram o modelo novo, inclusive a de nome.
- **Qualquer outra coisa** (delay, nitidez do rosto, som metálico, bipar palavra, tempo do fade, tirar frames do final, trocar a primeira frase): **não resolva**. Vira um marcador na sequência, no minuto dele, com o pedido escrito. O Juliano faz.
- **CORTE + número**: é onde começa um corte para Reels/TikTok. O texto ao lado só dá a pista do assunto e não entra no vídeo.

Antes de mexer, mostre uma tabela (minuto real da cartela → pedido → o que vai fazer) e as dúvidas.

## 2. Ler o projeto (sem abrir o Premiere)

1. Ache o `.prproj` na pasta do vídeo. Se estiver no Downloads ou com mídia em `Documents/deNoise/...`, mova para `00. Projeto`, troque os caminhos no XML para `01. Brutos` (passo a passo na `premiere-base`) e registre no `99. _Revisar/movimentos.csv`. O original vai para o `99. Temp` da pasta.
2. `dump_prproj.py` na sequência de edição. Nela, a cartela antiga = Color Matte + Graphic nas faixas V4–V6, e a V1 tem um **vão** embaixo de cada cartela.
3. Texto das cartelas antigas: frames do render da V1 (`03. Renders`) ou `exportAsMediaDirect` curto. O `InstanceName` do XML às vezes é só o nome da camada.

## 3. Cartelas novas (sequência "<nome> v02 cartelas")

1. Clone a sequência duas vezes: `_BACKUP_antes_cartelas` e ` v02 cartelas`. Trabalhe na v02 e crie 2 faixas de vídeo no topo.
2. Para cada cartela, `importMGT` em ordem cronológica, numa faixa vazia, com 5,042 s (a duração do .mogrt). **O fim da cartela nova = o fim do vão da V1.**
3. Textos: `Texto` (assunto) ou `Nome / Idade / Profissão / Cidade` (nome), trocando `textEditValue` e `fontTextRunLength` no JSON. Quebra de linha com `\r` em 2 linhas equilibradas. `Tamanho do texto` = 45. Na V1, idade e profissão costumam estar como placeholder ("X anos . Profissão"): use `XX years old / Profession` (ou o equivalente em português) e marque.
4. Divorce Stories: `Cor do logo` = `Cor do fundo` (`setColorValue`) e o PNG do logo na faixa de cima, só nas cartelas de assunto: Position 0,229 / 0,115, Scale 15,6, opacidade 0→100 em 1 s e 100→0 no último 1 s, com ease.
5. **Desative** as cartelas antigas (matte + graphic). Não apague nada e não mexa na música das cartelas.
6. Marcadores: um por pedido do Daniel que não é cartela, mais um em cada saída de cartela (o vão da V1 mostra ~5 frames de preto; na Camille o Juliano estendeu a V1 por baixo, e isso é com ele).
7. Confira exportando 0,5 s de cada cartela e olhando os frames.

## 4. Sequência de cortes (sequência "<nome> Cortes vertical")

1. Clone a v02 → 1080×1920, **mantendo o fps da original** (24 serve). Se mudar o fps, o `razor_timeline_at_time` corta em `tempo × fps_novo/fps_velho` (24→30: compense com × 1,25).
2. **A minutagem não muda**: o vídeo inteiro fica no lugar e desativado, inclusive as cartelas. Nada é removido nem empurrado.
3. V1 com Scale 177,78 e Position X para centralizar o rosto (detecte com `rostos.swift` nos frames: `X = 0,5 − (rosto_x − 0,5) × 3,16`). O rosto tem que aparecer **inteiro**. Bruto do Meet às vezes vem deitado: confira o frame da **timeline**, não o do arquivo.
4. Cada corte começa no gancho marcado (na borda de frase mais próxima, sem conversa de bastidor) e segue o assunto até fechar com **~3 min**. É um bloco contínuo: não se tira nada do meio. Termine no fim de uma ideia, nunca no meio da frase. Se o próximo corte começa antes, termine onde ele começa ou aceite uma sobreposição e avise.
5. Para escolher as bordas você precisa da transcrição com tempo por palavra. Use `transcricao.py` no .prproj e, se não houver, rode whisper.cpp no bruto: `whisper-cli` do Homebrew (`brew install whisper-cpp`) ou o de `03. Testes/Teste IA local 2026-10-21/downloads/whisper.cpp/.../build/bin/`, modelo `ggml-large-v3-turbo-q5_0.bin` (em `~/.local/share/whisper/` ou na mesma pasta de testes), com `-ojf` num WAV mono de 16 kHz e mapeie para a timeline pelos in/out da A1.
6. Corte V1/A1 nas bordas (`razor_timeline_at_time`), ative só os pedaços de dentro (tolerância 0,2 s) e confira a duração ativa de cada corte.
7. Marcador com duração em cada corte: `Corte N - <frase do Daniel>`, com "Daniel marcou mm:ss" e o porquê de qualquer desvio no comentário.
8. **Marca d'água:** o `arroba_<@>.png` do canal numa faixa nova no topo, por cima de cada corte. Fica **logo abaixo do queixo** da pessoa e muda de altura de vídeo para vídeo: meça o queixo nos frames e ajuste a Position Y (texto no PNG centrado em y = 1400). Branco a 70%, Poppins Medium 58. Para um @ novo, gere com ffmpeg `drawtext` como em `references/marca-dagua.md`.

## 5. Fechar

- Mostre as cartelas novas em frames, a tabela dos cortes (início, fim, duração, desvios) e os frames verticais com o @.
- Diga o que não conferiu (o áudio dos cortes, os bips, o som).
- **Não salve** sem ele pedir. Avise que abrir projeto antigo cria um `_1.prproj` e que o original fica intacto.
