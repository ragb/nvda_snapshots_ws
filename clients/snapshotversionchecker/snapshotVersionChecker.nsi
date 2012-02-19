;Inclui Modern UI e DockShortcut
!include "MUI2.nsh"

;--------------------------------
;Informacoes gerais

;Nome do arquivo de saida
Name "Verificar Versões Snapshot"
OutFile "snapshotVersionChecker.exe"

;Pasta de instalacao padrao
InstallDir "$APPDATA\NVDA\globalPlugins\"

;Texto que aparece quando se selecciona o caminho:
DirText "Por defeito o plugin será colocado na pasta do NVDA instalável. Se pretender adicionar estes ficheiros a uma versão portátil, seleccione o caminho dessa versão."

;--------------------------------
;Configuracoes da interface

!define MUI_ABORTWARNING
;--------------------------------
;Paginas do instalador

;paginas de instalacao
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

;--------------------------------
;Idioma

!insertmacro MUI_LANGUAGE "Portuguese"

;--------------------------------
;Secoes da instalacao

Section "-Instalacao completa" Instalacao
SetOutPath "$INSTDIR"
File /r "C:\Users\Diogo\Documents\My Dropbox\NVDA\Global Plugins\snapshotVersionChecker\snapshotVersionChecker"
SectionEnd

