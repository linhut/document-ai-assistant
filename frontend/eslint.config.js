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
    },
    languageOptions: {
      globals: globals.browser,
    },
  },
])
