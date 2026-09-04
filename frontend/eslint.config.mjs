// (c) 2026 Jose AI (https://www.linhut.cn)
// https://github.com/linhut/document-ai-assistant
// Licensed under the MIT License. See the LICENSE file for details.

import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import tseslint from 'typescript-eslint'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.recommended,
    ],
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      // API 边界处使用 any 是合理的（后端响应类型不确定）
      '@typescript-eslint/no-explicit-any': 'off',
      // shadcn/ui 组件和 hooks 文件大量导出非组件，禁用此规则
      'react-refresh/only-export-components': 'off',
      // 注：react-hooks 7.x 的 immutability / set-state-in-effect / refs /
      // static-components 四条规则已通过代码重构满足（loadXxx 函数上移到
      // useEffect 之前、URL 参数改为渲染期调整状态、ref 写入移入 effect、
      // 渲染期创建的组件改为模块级组件传 props），不再需要关闭。
    },
    languageOptions: {
      globals: globals.browser,
    },
  },
])
