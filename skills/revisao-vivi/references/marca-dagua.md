# Marca d'água do @ (TikTok/Reels da Vivi)

Copiada dos TikToks entregues do Separ (ex.: `Histórias de Divórcio/2027/01. Janeiro/KAREN REIS/tiktoks/`): @ em branco a ~70%, centralizado na horizontal, logo abaixo do queixo, fixo durante o corte.

PNGs prontos em `Vivi/00. Assets/Marca dagua/`: `arroba_separ.acoes.png`, `arroba_canalsuperacoes.png` e `arroba_storiesdivorce.png` (1080×1920, transparente, texto centrado em y ≈ 1400).

Para gerar um @ novo (fonte em `Templates/Vivi_Cartelas_Augusto/03_Fontes/Poppins`, copie para um caminho sem espaço antes):

```bash
~/.local/bin/ffmpeg -f lavfi -i "color=c=black@0.0:s=1080x1920,format=rgba" -frames:v 1 \
  -vf "drawtext=fontfile=pm.ttf:text='@NOVO':fontsize=58:fontcolor=white@0.7:x=(w-text_w)/2:y=1375" arroba_NOVO.png
```

Na timeline: Position Y = `0,5 + (y_alvo − 1400) / 1920`, com y_alvo um pouco abaixo do queixo (Olivia 0,425; Carrie 0,401 e 0,432 no corte mais próximo). Prefira cair em roupa a cair em pele clara: perde contraste.
