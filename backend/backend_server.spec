# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 文件 — FastAPI 后端打包配置

打包为 --onedir 模式，生成 backend_server.exe。
静态资源（rules/templates/TTF/data）由 build_backend.py 复制到输出目录。
"""
import os
import glob

block_cipher = None

a = Analysis(
    ['frozen_main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'fastapi.middleware.cors',
        'sqlalchemy',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.orm',
        'sqlalchemy.sql.default_comparator',
        'docx',
        'docx.oxml',
        'docx.oxml.ns',
        'docx.oxml.parser',
        'docx.oxml.text',
        'docx.oxml.text.paragraph',
        'docx.opc',
        'docx.opc.constants',
        'docx.opc.part',
        'docx.enum.text',
        'docx.enum.style',
        'docx.enum.table',
        'docx.shared',
        'httpx',
        'httpx._transports.default',
        'httpx._transports.wsgi',
        'pydantic',
        'pydantic.deprecated',
        'pydantic.deprecated.decorator',
        'pydantic_core',
        'cryptography',
        'cryptography.fernet',
        'cryptography.hazmat',
        'cryptography.hazmat.primitives',
        'cryptography.hazmat.primitives.ciphers',
        'cryptography.hazmat.backends',
        'multipart',
        'multipart.multipart',
        'yaml',
        'aiofiles',
        'email.mime.text',
        'email.mime.multipart',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='backend_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend_server',
)
