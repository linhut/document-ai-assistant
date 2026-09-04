; (c) 2026 Jose AI (https://www.linhut.cn)
; https://github.com/linhut/document-ai-assistant
; Licensed under the MIT License. See the LICENSE file for details.

; 自定义 NSIS 安装脚本
; 在欢迎页面显示版权信息

!macro customHeader
  ; 欢迎页面下方添加版权说明
  !define MUI_WELCOMEPAGE_TEXT "Setup will guide you through the installation of $(^NameDA).$\r$\n$\r$\nVersion 1.5.3$\r$\n$\r$\nCopyright (c) 2026 Jose AI - www.linhut.cn$\r$\n$\r$\nClick Next to continue."
!macroend
