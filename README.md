# deNoise · Revisão Vivi (skill para Claude Code)

Skill da **deNoise Studio** que faz a revisão V1 → V2 dos vídeos longos da Vivi (**Separ**, **Super** e **Divorce Stories**) no **Adobe Premiere Pro** pelo Claude Code, a partir das notas do Daniel:

- lê a mensagem do Daniel (minutagem + título de cartela, "manter", pedidos soltos e `CORTE` + minutagem);
- põe as **cartelas novas** (.mogrt) por cima das antigas, com o texto certo, a cor certa e o logo do canal;
- deixa um **marcador** na timeline para tudo o que o editor resolve na mão (delay, som, bip, fade, frames do final…);
- monta a **sequência vertical de cortes** para Reels/TikTok (no mínimo 6: os do Daniel e, se faltar, a skill escolhe outros por gancho; ~3 min cada, a minutagem do vídeo não muda) com a **marca d'água do @** do canal logo abaixo do queixo;
- confere tudo exportando frames, e não salva o projeto sem você pedir.

| Skill | O que faz |
|---|---|
| `skills/revisao-vivi` | O fluxo da revisão, a tabela de canais (mogrts, logo e @ de cada um) e os assets (`assets/`) |
| `skills/premiere-base` | A base técnica: conectar no Premiere pelo MCP Bridge, ExtendScript, dump/transcrição do `.prproj`, detecção de rosto e as armadilhas conhecidas do Bridge (`references/tecnico.md`) |

## Requisitos

- **macOS** (os scripts usam Swift/Vision)
- **Adobe Premiere Pro** (testado no 27)
- **Claude Code** instalado e logado
- Xcode Command Line Tools, Node 20+, `ffmpeg` e `whisper.cpp`: o `install.sh` cuida disso (o modelo do whisper tem ~550 MB)

## Instalar

```bash
git clone https://github.com/julianogarrett/denoise-revisao-vivi.git ~/denoise-revisao-vivi
cd ~/denoise-revisao-vivi && ./install.sh
```

O script liga as duas skills em `~/.claude/skills/` (é um link para o repositório, então `git pull` atualiza), instala `ffmpeg`, `whisper-cli` e o modelo de transcrição, copia a fonte Poppins e instala/registra o MCP Bridge do Premiere.

Depois, à mão:
1. Feche e abra o Premiere. **Window › Extensions › MCP Bridge (CEP)** → **Start Bridge**.
2. Abra uma **sessão nova** do Claude Code e peça: `roda verify_premiere_connection, sem mudar nada`.

## Usar

Abra o projeto do vídeo no Premiere (ou só diga onde está o `.prproj`), cole as notas do Daniel e peça, por exemplo:

> Revisão da Olivia Howell (Divorce Stories). Pode rodar ExtendScript nesta sessão.
>
> *(cole aqui a mensagem do Daniel)*

A skill primeiro mostra uma tabela do que entendeu e as dúvidas. Depois faz as cartelas, depois os cortes, e mostra frames de cada etapa.

## Assets incluídos (`skills/revisao-vivi/assets/`)

- `mogrts/`: cartelas Separ e Super, nome e assunto, nas 3 cores (V1, V2, V3)
- `logo-divorce-stories/`: logo provisório do Divorce Stories (roxo, branco, laranja)
- `marca-dagua/`: `@separ.acoes`, `@canalsuperacoes` e `@storiesdivorce` (PNG 1080×1920 transparente)
- `fontes/`: Poppins Medium/Bold (licença OFL)

Se a pasta da deNoise (`00. Clientes/01. Ongoing/Vivi/00. Assets`) existir no Mac, a skill usa a de lá; senão, usa estas cópias.

## O que NÃO está aqui

- Brutos, projetos e renders dos vídeos (ficam no Drive da Vivi / na pasta da deNoise).
- A música e o SFX das cartelas (`MUSICA_cartelas_divorcio.mp3`): a skill não mexe neles, eles já estão no projeto.

## Regras que a skill segue

- V1/A1 são do editor: a skill não corta nem apaga nada na sequência original, trabalha em cópias (`_BACKUP_antes_cartelas`, `v02 cartelas`, `<Nome>_tiktok`).
- Cartela antiga é **desativada**, nunca apagada. Nenhum arquivo é apagado.
- **Não salva o projeto** sem pedido.
- Não ouve áudio: sempre diz o que precisa ser conferido de ouvido.
