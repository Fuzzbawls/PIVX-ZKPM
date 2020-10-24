; Helper defines. PRODUCT_VERSION is parsed by reading src/version.txt.
!searchparse /file src/ZkParamsWizard/version.txt `"number": "` VER_MAJOR `.` VER_MINOR `.` VER_REV `"`
!searchparse /file src/ZkParamsWizard/version.txt `"tag": "` VER_TAG `"`
!define PRODUCT_NAME "ZkParamsWizard"
!define PRODUCT_VERSION "${VER_MAJOR}.${VER_MINOR}.${VER_REV}${VER_TAG}"
!define PRODUCT_PUBLISHER "PIVX"
!define PRODUCT_WEB_SITE "https://github.com/PIVX-Project/PIVX-zKPW"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\ZkParamsWizard.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor /SOLID lzma

; MUI 1.67 compatible ------
!include "MUI.nsh"
!include "x64.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "img\zkpw.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\ZkParamsWizard.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; Reserve files
!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS

; MUI end ------

Name "${PRODUCT_NAME}"
OutFile "ZkParamsWizard-v${PRODUCT_VERSION}-Win64-Setup.exe"
InstallDir "$PROGRAMFILES64\ZkParamsWizard"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  File /r "ZkParamsWizard-v${PRODUCT_VERSION}-Win64\*.*"

  CreateDirectory "$SMPROGRAMS\ZkParamsWizard"
  CreateShortCut "$SMPROGRAMS\ZkParamsWizard\ZkParamsWizard.lnk" "$INSTDIR\ZkParamsWizard.exe"
  CreateShortCut "$DESKTOP\ZkParamsWizard.lnk" "$INSTDIR\ZkParamsWizard.exe"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\SPMT\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\SPMT\Uninstall.lnk" "$INSTDIR\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\ZkParamsWizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\ZkParamsWizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove $(^Name) and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\ZkParamsWizard.exe"

  Delete "$SMPROGRAMS\ZkParamsWizard\Uninstall.lnk"
  Delete "$SMPROGRAMS\ZkParamsWizard\Website.lnk"
  Delete "$DESKTOP\ZkParamsWizard.lnk"
  Delete "$SMPROGRAMS\ZkParamsWizard\ZkParamsWizard.lnk"

  RMDir "$SMPROGRAMS\ZkParamsWizard"
  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

# Installer functions
Function .onInit
    InitPluginsDir
    ${If} ${RunningX64}
      ; disable registry redirection (enable access to 64-bit portion of registry)
      SetRegView 64
    ${Else}
      MessageBox MB_OK|MB_ICONSTOP "Cannot install ZkParamsWizard on a 32-bit system."
      Abort
    ${EndIf}
FunctionEnd