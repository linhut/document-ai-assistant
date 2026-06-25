/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * AISettings - AI 配置页面
 * 支持多 Provider、获取模型列表、连接测试、脱敏 API Key
 */
import { useState, useEffect } from 'react';
import { Sparkles, Lock, CheckCircle2, Loader2, RefreshCw } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { apiClient } from '@/api/client';

interface ProviderInfo {
  value: string;
  label: string;
  defaultUrl: string;
  defaultModel: string;
}

const PROVIDERS: ProviderInfo[] = [
  { value: 'openai', label: 'OpenAI', defaultUrl: 'https://api.openai.com/v1', defaultModel: 'gpt-4o-mini' },
  { value: 'deepseek', label: 'DeepSeek', defaultUrl: 'https://api.deepseek.com/v1', defaultModel: 'deepseek-chat' },
  { value: 'claude', label: 'Claude (Anthropic)', defaultUrl: 'https://api.anthropic.com', defaultModel: 'claude-sonnet-4-20250514' },
  { value: 'custom', label: '阿里云百炼 (Qwen)', defaultUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModel: 'qwen-turbo' },
  { value: 'custom', label: '智谱 AI (GLM)', defaultUrl: 'https://open.bigmodel.cn/api/paas/v4', defaultModel: 'glm-4-flash' },
  { value: 'custom', label: '月之暗面 (Kimi)', defaultUrl: 'https://api.moonshot.cn/v1', defaultModel: 'moonshot-v1-8k' },
  { value: 'custom', label: 'MiniMax', defaultUrl: 'https://api.minimax.chat/v1', defaultModel: 'MiniMax-Text-01' },
  { value: 'custom', label: '腾讯混元', defaultUrl: 'https://api.hunyuan.cloud.tencent.com/v1', defaultModel: 'hunyuan-lite' },
  { value: 'custom', label: '百度千帆', defaultUrl: 'https://qianfan.baidubce.com/v2', defaultModel: 'ernie-speed-8k' },
  { value: 'custom', label: '火山方舟 (Ark)', defaultUrl: 'https://ark.cn-beijing.volces.com/api/v3', defaultModel: 'doubao-1.5-pro-32k' },
  { value: 'custom', label: '豆包 (Doubao)', defaultUrl: 'https://ark.cn-beijing.volces.com/api/v3', defaultModel: 'doubao-1.5-pro-32k' },
  { value: 'custom', label: '零一万物 (Yi)', defaultUrl: 'https://api.lingyiwanwu.com/v1', defaultModel: 'yi-lightning' },
  { value: 'custom', label: '商汤 SenseNova', defaultUrl: 'https://api.sensenova.cn/v1', defaultModel: 'SenseChat-5' },
  { value: 'custom', label: '天工 Skywork', defaultUrl: 'https://api.tiangong.cn/v1', defaultModel: 'skywork-mega' },
  { value: 'custom', label: 'OpenRouter', defaultUrl: 'https://openrouter.ai/api/v1', defaultModel: 'openai/gpt-4o-mini' },
  { value: 'custom', label: 'SiliconFlow', defaultUrl: 'https://api.siliconflow.cn/v1', defaultModel: 'Qwen/Qwen2.5-7B-Instruct' },
  { value: 'custom', label: '小米 MiMo (OpenAI)', defaultUrl: 'https://api.xiaomimimo.com/v1', defaultModel: 'MiMo-7B' },
  { value: 'custom', label: '小米 MiMo (Anthropic)', defaultUrl: 'https://api.xiaomimimo.com/anthropic', defaultModel: 'MiMo-7B' },
  { value: 'custom', label: '小米 MiMo Token Plan CN (OpenAI)', defaultUrl: 'https://token-plan-cn.xiaomimimo.com/v1', defaultModel: 'MiMo-7B' },
  { value: 'custom', label: '小米 MiMo Token Plan CN (Anthropic)', defaultUrl: 'https://token-plan-cn.xiaomimimo.com/anthropic', defaultModel: 'MiMo-7B' },
  { value: 'custom', label: '讯飞星火', defaultUrl: 'https://spark-api-open.xf-yun.com/v1', defaultModel: 'generalv3.5' },
  { value: 'ollama', label: 'Ollama (本地)', defaultUrl: 'http://localhost:11434/v1', defaultModel: 'qwen2.5:7b' },
  { value: 'custom', label: '自定义 (OpenAI 兼容)', defaultUrl: 'https://cpa.linhut.cn/v1', defaultModel: 'gpt-4o-mini' },
];

export default function AISettings() {
  const [provider, setProvider] = useState('custom');
  const [selectedLabel, setSelectedLabel] = useState('自定义 (OpenAI 兼容)');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://cpa.linhut.cn/v1');
  const [model, setModel] = useState('gpt-4o-mini');
  const [isConnected, setIsConnected] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isFetchingModels, setIsFetchingModels] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [apiKeyMasked, setApiKeyMasked] = useState('');
  const [hasSavedKey, setHasSavedKey] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const currentProvider = PROVIDERS.find(p => p.label === selectedLabel);

  useEffect(() => {
    loadConfig();
    loadDefaultConfig();
  }, [provider]);

  const loadDefaultConfig = async () => {
    try {
      const resp = await apiClient.get('/api/ai/default');
      if (resp.api_key && !apiKey) {
        setApiKeyMasked(resp.api_key);
      }
    } catch {
      // 默认配置加载失败不影响正常使用
      console.warn('加载默认 AI 配置失败');
    }
  };

  const loadConfig = async () => {
    try {
      const response = await apiClient.get(`/api/ai/config/${provider}`);
      if (response.exists) {
        setBaseUrl(response.base_url || '');
        setModel(response.model || '');
        setIsConnected(response.is_active);
        if (response.api_key_masked) {
          setApiKeyMasked(response.api_key_masked);
          setHasSavedKey(true);
        }
      } else if (response.default) {
        // 使用默认配置
        setBaseUrl(response.default.base_url || '');
        setModel(response.default.model || '');
        if (response.default.api_key_masked) {
          setApiKeyMasked(response.default.api_key_masked);
          setHasSavedKey(true);
        }
      }
    } catch (error) {
      console.error('Load config error:', error);
    }
  };

  const handleFetchModels = async () => {
    if (!baseUrl) {
      setErrorMessage('请先填写 Base URL');
      return;
    }
    if (!apiKey && !hasSavedKey) {
      setErrorMessage('请先输入 API Key 或确认已保存的密钥');
      return;
    }
    setIsFetchingModels(true);
    setErrorMessage('');
    try {
      const resp = await apiClient.post('/api/ai/models', { base_url: baseUrl, api_key: apiKey || '__saved__', provider });
      if (resp.success && resp.models.length > 0) {
        setAvailableModels(resp.models);
        setSuccessMessage(`获取到 ${resp.count} 个模型`);
      } else {
        setErrorMessage(resp.message || '未获取到模型列表');
      }
    } catch (error: any) {
      setErrorMessage('获取模型失败：' + (error.response?.data?.message || '请检查配置'));
    } finally {
      setIsFetchingModels(false);
    }
  };

  const handleTestConnection = async () => {
    if (!apiKey && !hasSavedKey) {
      setErrorMessage('请先输入 API Key');
      return;
    }
    setIsTesting(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const response = await apiClient.post('/api/ai/test', {
        provider, api_key: apiKey || '__saved__', base_url: baseUrl, model,
      });
      if (response.success) {
        setIsConnected(true);
        setSuccessMessage(`连接成功！模型：${response.model || model}`);
      } else {
        setErrorMessage(response.message || '连接失败');
        setIsConnected(false);
      }
    } catch (error: any) {
      setErrorMessage(error.response?.data?.message || '连接测试失败');
      setIsConnected(false);
    } finally {
      setIsTesting(false);
    }
  };

  const handleSave = async () => {
    if (!apiKey && !hasSavedKey) {
      setErrorMessage('请先输入 API Key');
      return;
    }
    setIsSaving(true);
    setErrorMessage('');
    setSuccessMessage('');
    try {
      const response = await apiClient.post('/api/ai/config', {
        provider,
        api_key: apiKey || '',  // 空则保留已保存的密钥
        base_url: baseUrl,
        model,
      });
      if (response.success) {
        setSuccessMessage('配置已保存！');
        setIsConnected(true);
        if (apiKey) {
          setApiKey('');
          setHasSavedKey(true);
          // 重新加载以获取新的脱敏 key
          await loadConfig();
        }
      }
    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  const handleProviderChange = (label: string) => {
    const info = PROVIDERS.find(p => p.label === label);
    if (!info) return;
    setSelectedLabel(label);
    setProvider(info.value);
    setBaseUrl(info.defaultUrl);
    setModel(info.defaultModel);
    setAvailableModels([]);
    setIsConnected(false);
    setHasSavedKey(false);
    setApiKeyMasked('');
    setErrorMessage('');
    setSuccessMessage('');
  };

  return (
    <div className="w-full bg-primary-50">
      <PageHeader title="AI 配置" description="配置 AI 服务提供商和模型" />

      <div className="p-4 md:p-6 lg:p-8 w-full space-y-6">
        {/* 状态卡片 */}
        <Card className="border-primary-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-accent" />
                <span className="font-medium text-primary-900">AI 服务状态</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant={isConnected ? 'default' : 'secondary'}>
                  {isConnected ? '✓ 已连接' : '未配置'}
                </Badge>
                <span title={isConnected ? '点击禁用 AI 服务' : '点击启用 AI 服务'}>
                  <Switch
                    checked={isConnected}
                    onCheckedChange={async (newState) => {
                    setIsConnected(newState);
                    try {
                      await apiClient.post('/api/ai/config', {
                        provider,
                        is_active: newState,
                      });
                    } catch {
                      // 失败时回滚状态
                      setIsConnected(!newState);
                      console.error('切换 AI 状态失败');
                    }
                  }}
                />
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 配置卡片 */}
        <Card className="border-primary-200">
          <CardHeader>
            <CardTitle>基础配置</CardTitle>
            <CardDescription>选择 AI 服务提供商并配置参数</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Provider 选择 */}
            <div className="space-y-2">
              <Label>AI 服务商</Label>
              <Select value={selectedLabel} onValueChange={handleProviderChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {PROVIDERS.map((p) => (
                    <SelectItem key={p.label} value={p.label}>
                      {p.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* API Key */}
            <div className="space-y-2">
              <Label className="flex items-center gap-2">
                <Lock className="h-4 w-4" />
                API Key
              </Label>
              <div className="relative">
                <Input
                  type="password"
                  placeholder={hasSavedKey ? '已配置，输入新密钥可替换' : '请输入 API Key'}
                  value={hasSavedKey && !apiKey ? '••••••••••••••••' : apiKey}
                  onChange={(e) => {
                    // 如果是从星号状态开始输入，清除星号，开始接收真实输入
                    if (hasSavedKey && apiKey === '' && e.target.value !== '••••••••••••••••') {
                      // 用户开始输入新密钥
                    }
                    setApiKey(e.target.value === '••••••••••••••••' ? '' : e.target.value);
                  }}
                  onFocus={(e) => {
                    // 聚焦时如果显示的是星号，清空以便输入
                    if (hasSavedKey && !apiKey) {
                      setApiKey('');
                    }
                  }}
                />
                {hasSavedKey && !apiKey && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5 text-status-success" />
                    <span className="text-[10px] text-status-success">已配置</span>
                  </div>
                )}
              </div>
              <p className="text-xs text-primary-500">
                {hasSavedKey ? '输入新密钥将替换已保存的，留空则继续使用已保存的密钥' : 'API Key 将加密存储在本地数据库'}
              </p>
            </div>

            {/* Base URL */}
            <div className="space-y-2">
              <Label>Base URL</Label>
              <Input
                type="url"
                placeholder="https://api.example.com/v1"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
              />
            </div>

            {/* 模型 + 获取模型 */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label>模型</Label>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleFetchModels}
                  disabled={isFetchingModels || !baseUrl || (!apiKey && !hasSavedKey)}
                >
                  {isFetchingModels ? (
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                  ) : (
                    <RefreshCw className="h-3 w-3 mr-1" />
                  )}
                  获取模型
                </Button>
              </div>
              {availableModels.length > 0 ? (
                <Select value={model} onValueChange={setModel}>
                  <SelectTrigger>
                    <SelectValue placeholder="选择模型" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map((m) => (
                      <SelectItem key={m} value={m}>{m}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Input
                  placeholder={`例如：${currentProvider?.defaultModel || 'model-name'}`}
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                />
              )}
            </div>

            {/* 消息 */}
            {errorMessage && (
              <div className="p-3 bg-status-error-bg border border-status-error rounded text-sm text-status-error">
                {errorMessage}
              </div>
            )}
            {successMessage && (
              <div className="p-3 bg-status-success-bg border border-status-success rounded text-sm text-status-success">
                {successMessage}
              </div>
            )}

            {/* 操作按钮 */}
            <div className="flex gap-3">
              <Button
                onClick={handleTestConnection}
                disabled={isTesting || (!apiKey && !hasSavedKey)}
                variant="outline"
                className="flex-1"
              >
                {isTesting ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" />测试中...</>
                ) : (
                  <><CheckCircle2 className="h-4 w-4 mr-2" />测试连接</>
                )}
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving || (!apiKey && !hasSavedKey)}
                className="flex-1"
              >
                {isSaving ? (
                  <><Loader2 className="h-4 w-4 mr-2 animate-spin" />保存中...</>
                ) : '保存配置'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 说明 */}
        <Card className="border-primary-200 bg-primary-50">
          <CardHeader>
            <CardTitle className="text-base">使用说明</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-primary-700 space-y-2">
            <p>• 内置默认配置可用，无需手动配置即可使用基础 AI 功能</p>
            <p>• API Key 使用 Fernet 加密后存储，UI 显示脱敏（如 sk-xxxx****xxxx）</p>
            <p>• 点击「获取模型」自动从 API 端点获取可用模型列表</p>
            <p>• Claude Provider 使用 Anthropic Messages API，需对应的 API Key</p>
            <p>• Ollama 为本地模型，需先在本地安装并启动 Ollama 服务</p>
            <p className="text-xs text-primary-400 mt-2 pt-2 border-t border-primary-200">
              提供自建测试KEY：sk-1yTKb4Hxh7Cn5y5Xi
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}