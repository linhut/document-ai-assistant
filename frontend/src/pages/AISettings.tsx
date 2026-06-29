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
import { Sparkles, Lock, CheckCircle2, Loader2, RefreshCw, Wifi, WifiOff } from 'lucide-react';
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
import { notifyAIConfigChanged } from '@/lib/ai-status';

interface ProviderInfo {
  value: string;      // DB 存储 key（custom 服务用 "custom:<服务名>" 格式确保唯一）
  providerType: string; // 实际后端 provider 类型（openai/deepseek/claude/ollama/custom）
  label: string;
  defaultUrl: string;
  defaultModel: string;
}

const PROVIDERS: ProviderInfo[] = [
  { value: 'openai', providerType: 'openai', label: 'OpenAI', defaultUrl: 'https://api.openai.com/v1', defaultModel: 'gpt-4o-mini' },
  { value: 'deepseek', providerType: 'deepseek', label: 'DeepSeek', defaultUrl: 'https://api.deepseek.com/v1', defaultModel: 'deepseek-chat' },
  { value: 'claude', providerType: 'claude', label: 'Claude (Anthropic)', defaultUrl: 'https://api.anthropic.com', defaultModel: 'claude-sonnet-4-20250514' },
  { value: 'custom:aliyun_qwen', providerType: 'custom', label: '阿里云百炼 (Qwen)', defaultUrl: 'https://dashscope.aliyuncs.com/compatible-mode/v1', defaultModel: 'qwen-turbo' },
  { value: 'custom:zhipu_glm', providerType: 'custom', label: '智谱 AI (GLM)', defaultUrl: 'https://open.bigmodel.cn/api/paas/v4', defaultModel: 'glm-4-flash' },
  { value: 'custom:moonshot_kimi', providerType: 'custom', label: '月之暗面 (Kimi)', defaultUrl: 'https://api.moonshot.cn/v1', defaultModel: 'moonshot-v1-8k' },
  { value: 'custom:minimax', providerType: 'custom', label: 'MiniMax', defaultUrl: 'https://api.minimax.chat/v1', defaultModel: 'MiniMax-Text-01' },
  { value: 'custom:tencent_hunyuan', providerType: 'custom', label: '腾讯混元', defaultUrl: 'https://api.hunyuan.cloud.tencent.com/v1', defaultModel: 'hunyuan-lite' },
  { value: 'custom:baidu_qianfan', providerType: 'custom', label: '百度千帆', defaultUrl: 'https://qianfan.baidubce.com/v2', defaultModel: 'ernie-speed-8k' },
  { value: 'custom:volcengine_ark', providerType: 'custom', label: '火山方舟 (Ark)', defaultUrl: 'https://ark.cn-beijing.volces.com/api/v3', defaultModel: 'doubao-1.5-pro-32k' },
  { value: 'custom:doubao', providerType: 'custom', label: '豆包 (Doubao)', defaultUrl: 'https://ark.cn-beijing.volces.com/api/v3', defaultModel: 'doubao-1.5-pro-32k' },
  { value: 'custom:lingyiwanwu_yi', providerType: 'custom', label: '零一万物 (Yi)', defaultUrl: 'https://api.lingyiwanwu.com/v1', defaultModel: 'yi-lightning' },
  { value: 'custom:sensenova', providerType: 'custom', label: '商汤 SenseNova', defaultUrl: 'https://api.sensenova.cn/v1', defaultModel: 'SenseChat-5' },
  { value: 'custom:tiangong_skywork', providerType: 'custom', label: '天工 Skywork', defaultUrl: 'https://api.tiangong.cn/v1', defaultModel: 'skywork-mega' },
  { value: 'custom:openrouter', providerType: 'custom', label: 'OpenRouter', defaultUrl: 'https://openrouter.ai/api/v1', defaultModel: 'openai/gpt-4o-mini' },
  { value: 'custom:siliconflow', providerType: 'custom', label: 'SiliconFlow', defaultUrl: 'https://api.siliconflow.cn/v1', defaultModel: 'Qwen/Qwen2.5-7B-Instruct' },
  { value: 'custom:xiaomi_mimo_openai', providerType: 'custom', label: '小米 MiMo (OpenAI)', defaultUrl: 'https://api.xiaomimimo.com/v1', defaultModel: 'MiMo-7B' },
  { value: 'custom:xiaomi_mimo_anthropic', providerType: 'custom', label: '小米 MiMo (Anthropic)', defaultUrl: 'https://api.xiaomimimo.com/anthropic', defaultModel: 'MiMo-7B' },
  { value: 'custom:xiaomi_mimo_tp_cn_openai', providerType: 'custom', label: '小米 MiMo Token Plan CN (OpenAI)', defaultUrl: 'https://token-plan-cn.xiaomimimo.com/v1', defaultModel: 'MiMo-7B' },
  { value: 'custom:xiaomi_mimo_tp_cn_anthropic', providerType: 'custom', label: '小米 MiMo Token Plan CN (Anthropic)', defaultUrl: 'https://token-plan-cn.xiaomimimo.com/anthropic', defaultModel: 'MiMo-7B' },
  { value: 'custom:xunfei_spark', providerType: 'custom', label: '讯飞星火', defaultUrl: 'https://spark-api-open.xf-yun.com/v1', defaultModel: 'generalv3.5' },
  { value: 'ollama', providerType: 'ollama', label: 'Ollama (本地)', defaultUrl: 'http://localhost:11434/v1', defaultModel: 'qwen2.5:7b' },
  { value: 'custom:default', providerType: 'custom', label: '自定义 (OpenAI 兼容)', defaultUrl: 'https://cpa.linhut.cn/v1', defaultModel: 'gpt-4o-mini' },
];

/**
 * 从 DB key 提取后端 provider 类型
 * "custom:aliyun_qwen" → "custom"
 * "openai" → "openai"
 */
function getBackendProviderType(dbKey: string): string {
  return dbKey.startsWith('custom:') ? 'custom' : dbKey;
}

export default function AISettings() {
  const [provider, setProvider] = useState('custom:default');
  const [selectedLabel, setSelectedLabel] = useState('自定义 (OpenAI 兼容)');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://cpa.linhut.cn/v1');
  const [model, setModel] = useState('gpt-4o-mini');
  const [isConnected, setIsConnected] = useState(false);
  const [isActive, setIsActive] = useState(true);
  const [isTesting, setIsTesting] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isFetchingModels, setIsFetchingModels] = useState(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [apiKeyMasked, setApiKeyMasked] = useState('');
  const [hasSavedKey, setHasSavedKey] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [modelStatuses, setModelStatuses] = useState<Array<{ provider: string; model: string; online: boolean; latency_ms?: number; error?: string }>>([]);

  const currentProvider = PROVIDERS.find(p => p.label === selectedLabel);

  useEffect(() => {
    const controller = new AbortController();
    loadConfig(controller.signal);
    loadDefaultConfig(controller.signal);
    return () => controller.abort();
  }, [provider]);

  // 模型可用性状态轮询（每 60 秒）
  useEffect(() => {
    const controller = new AbortController();
    loadModelStatus(controller.signal);
    const timer = setInterval(() => loadModelStatus(controller.signal), 60000);
    return () => { clearInterval(timer); controller.abort(); };
  }, []);

  const loadDefaultConfig = async (signal?: AbortSignal) => {
    try {
      const resp = await apiClient.get<{ api_key?: string }>('/api/ai/default', { signal });
      if (resp.api_key && !apiKey) {
        setApiKeyMasked(resp.api_key);
      }
    } catch (err: any) {
      if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
      // 默认配置加载失败不影响正常使用
      console.warn('加载默认 AI 配置失败');
    }
  };

  const loadModelStatus = async (signal?: AbortSignal) => {
    try {
      const resp = await apiClient.get<{ statuses?: typeof modelStatuses }>('/api/ai/status', { signal });
      if (resp.statuses) setModelStatuses(resp.statuses);
    } catch (err: any) {
      if (err?.name === 'CanceledError' || err?.code === 'ERR_CANCELED') return;
      // 静默失败
    }
  };

  const loadConfig = async (signal?: AbortSignal) => {
    try {
      interface ConfigResponse {
        exists?: boolean;
        base_url?: string;
        model?: string;
        is_active?: boolean;
        api_key_masked?: string;
        default?: { base_url?: string; model?: string; api_key_masked?: string };
      }
      const response = await apiClient.get<ConfigResponse>(`/api/ai/config/${encodeURIComponent(provider)}`, { signal });
      if (response.exists) {
        setBaseUrl(response.base_url || '');
        setModel(response.model || '');
        setIsConnected(response.is_active ?? true);
        setIsActive(response.is_active ?? true);
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
    } catch (error: any) {
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED') return;
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
      const resp = await apiClient.post<{ success: boolean; models: string[]; count: number; message?: string }>('/api/ai/models', {
        base_url: baseUrl,
        api_key: apiKey || '__saved__',
        provider: getBackendProviderType(provider),
      });
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
      const response = await apiClient.post<{ success: boolean; model?: string; message?: string }>('/api/ai/test', {
        provider: getBackendProviderType(provider),
        api_key: apiKey || '__saved__',
        base_url: baseUrl,
        model,
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
      const response = await apiClient.post<{ success: boolean }>('/api/ai/config', {
        provider,                 // 完整 DB key（如 "custom:aliyun_qwen"）
        api_key: apiKey || '',    // 空则保留已保存的密钥
        base_url: baseUrl,
        model,
        is_active: true,          // 保存时自动启用
      });
      if (response.success) {
        setSuccessMessage('配置已保存并启用！');
        setIsConnected(true);
        setIsActive(true);
        notifyAIConfigChanged(); // 通知全局刷新 AI 状态
        if (apiKey) {
          setApiKey('');
          setHasSavedKey(true);
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
    setIsActive(true);
    setHasSavedKey(false);
    setApiKeyMasked('');
    setApiKey('');
    setErrorMessage('');
    setSuccessMessage('');
  };

  const handleToggleActive = async (newState: boolean) => {
    setIsActive(newState);
    setIsConnected(newState);
    try {
      await apiClient.post('/api/ai/config', {
        provider,
        is_active: newState,
      });
      notifyAIConfigChanged(); // 通知全局刷新 AI 状态
    } catch {
      setIsActive(!newState);
      setIsConnected(!newState);
      console.error('切换 AI 状态失败');
    }
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
                <Badge variant={isActive ? 'default' : 'secondary'}>
                  {isActive ? '✓ 已启用' : '已禁用'}
                </Badge>
                <span title={isActive ? '点击禁用 AI 服务' : '点击启用 AI 服务'}>
                  <Switch
                    checked={isActive}
                    onCheckedChange={handleToggleActive}
                  />
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 模型可用性状态 */}
        {modelStatuses.length > 0 && (
          <Card className="border-primary-200">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">模型可用性监控</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => loadModelStatus()} className="h-6 px-2">
                  <RefreshCw className="h-3 w-3" />
                </Button>
              </div>
              <CardDescription>每 60 秒自动检测，实时反映模型连接状态</CardDescription>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                {modelStatuses.map((s, i) => (
                  <div key={i} className="flex items-center justify-between py-1.5 px-2 bg-primary-50 rounded text-xs">
                    <div className="flex items-center gap-2">
                      {s.online
                        ? <Wifi className="h-3.5 w-3.5 text-status-success" />
                        : <WifiOff className="h-3.5 w-3.5 text-red-400" />
                      }
                      <span className="font-medium text-primary-700">{s.provider}</span>
                      <span className="text-primary-400">{s.model}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {s.online && <span className="text-primary-400">{s.latency_ms}ms</span>}
                      <Badge variant={s.online ? 'default' : 'destructive'} className="text-[10px] px-1.5 py-0">
                        {s.online ? '在线' : s.error || '离线'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

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
                    <SelectItem key={p.value} value={p.label}>
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
                    setApiKey(e.target.value === '••••••••••••••••' ? '' : e.target.value);
                  }}
                  onFocus={() => {
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
            <p>• 保存配置时自动启用该 AI 服务，可通过开关手动禁用</p>
            <p className="text-xs text-primary-400 mt-2 pt-2 border-t border-primary-200">
              如需测试KEY，请联系管理员获取
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
