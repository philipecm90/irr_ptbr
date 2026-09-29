# Incursion Red River — Tradução PT-BR

Tradução para português brasileiro do jogo **Incursion Red River** (Unreal Engine 5.6),
mantendo termos militares e de nicho (Red Dot, calibres, marcas/modelos, etc.).

Este repositório contém **todo o código-fonte** do instalador e do mod de tradução,
para que qualquer pessoa possa auditar, compilar e verificar que não há código malicioso.

## Como funciona (visão geral)

A tradução usa **duas técnicas**, as mesmas usadas pelas traduções da comunidade (ex.: a coreana):

1. **Patch pak (`_P.pak`)** — um pacote Unreal que sobrescreve textos fixos gravados nos
   assets (menus, widgets, DataTables, DataAssets). O jogo carrega o patch por cima dos
   arquivos originais.
2. **UE4SS + PTTranslator (Lua)** — um mod que injeta código no jogo e intercepta o método
   `SetText` dos widgets em tempo de execução, traduzindo os textos dinâmicos
   (missões, HUD, mensagens, prompts) usando uma tabela `English -> Português`.

Nenhuma das duas técnicas altera os arquivos originais do jogo: o patch é **aditivo** e o
Lua apenas substitui o texto exibido em memória.

## O que o instalador faz

- Detecta a pasta do jogo (Steam ou cópia local) ou permite selecionar manualmente.
- Faz **backup** de qualquer arquivo que venha a ser sobrescrito em
  `<pasta do jogo>\_IRRPTBR_backup\` (com manifest e SHA-1).
- Copia os arquivos do mod:
  - `Test_C/Content/Paks/pakchunk999-IRRPTBR_P.pak`
  - `Test_C/Binaries/Win64/dwmapi.dll` (proxy do UE4SS)
  - `Test_C/Binaries/Win64/ue4ss/**` (UE4SS + `PTTranslator`)
- Permite **desinstalar / restaurar** o idioma original.

## Estrutura do repositório

```
installer/IRR_PTBR_Installer.py   # instalador (Python + tkinter; empacotado com PyInstaller)
ue4ss-mod/PTTranslator/main.lua   # hook de runtime (SetText) e padrões de tradução
ue4ss-mod/PTTranslator/translations.lua  # tabela English -> Português
tools/                            # scripts de build (extração/tradução/repack dos paks)
```

## Compilar o instalador (opcional)

O executável é apenas um empacotamento do `installer/IRR_PTBR_Installer.py` (Python 3 + tkinter)
com o conteúdo do mod embutido via PyInstaller:

```bat
pyinstaller --onefile --windowed --uac-admin ^
  --name IRR_PTBR_Installer ^
  --add-data "payload;payload" ^
  IRR_PTBR_Installer.py
```

O `payload\` contém exatamente os arquivos listados em "O que o instalador faz".
Como o código é público, qualquer um pode conferir que o `.exe` só copia/restaura arquivos.

## Instalação manual (sem o `.exe`)

1. Feche o jogo.
2. Extraia `Incursion_Red_River_PTBR_v1_Manual.zip` na pasta raiz do jogo
   (a que contém `Test_C`), mesclando quando solicitado. (Alternativa:
   copie o conteúdo da pasta `payload\` para dentro da pasta do jogo).
3. Para desinstalar, remova:
   - `Test_C/Content/Paks/pakchunk999-IRRPTBR_P.pak`
   - `Test_C/Binaries/Win64/dwmapi.dll`
   - `Test_C/Binaries/Win64/ue4ss/`

## Privacidade e segurança

- **Não há telemetria, rede, coleta de dados, persistência ou auto-update.**
- O UE4SS é um projeto de código aberto da comunidade (injetor de mods Lua).
- O único acesso a disco é: ler a pasta do jogo, criar o backup e copiar/remover os arquivos
  do mod (e gerar um `.ini` de configuração de fonte usado pelo UE4SS).

## Créditos

- Mecanismo de runtime (UE4SS + hook de `SetText`) inspirado na tradução coreana
  de **s10th24b** (usada apenas como referência de onde/como traduzir).
- Tradução PT-BR: comunidade.

## Licença

MIT — veja `LICENSE`.
