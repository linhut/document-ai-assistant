/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
﻿/**
 * Rules - 规则管理页面
 * 支持按来源层级查看：官方规则、单位规则、用户规则
 */
import { useState, useEffect } from 'react';
import {
  FileCode, Eye, Loader2, Upload, Download, Trash2,
  Layers, BookOpen, Building2, User, Plus
} from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { apiClient } from '@/api/client';
import { useToast } from '@/components/ui/toast';

interface RuleItem {
  key: string;
  name: string;
  source_type: 'official' | 'custom' | 'user';
  path: string;
  size: number;
  enabled: boolean;
}

const sourceLabels: Record<string, string> = {
  official: '官方',
  custom: '单位',
  user: '用户',
};

const sourceIcons: Record<string, React.ReactNode> = {
  official: <BookOpen className="h-4 w-4" />,
  custom: <Building2 className="h-4 w-4" />,
  user: <User className="h-4 w-4" />,
};

const sourceColors: Record<string, string> = {
  official: 'bg-status-info-bg text-status-info',
  custom: 'bg-primary-100 text-primary-500',
  user: 'bg-status-warning-bg text-status-warning',
};

export default function Rules() {
  const { error: showError, warning, confirm } = useToast();
  const [rules, setRules] = useState<RuleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [sourceFilter, setSourceFilter] = useState('all');
  const [selectedRule, setSelectedRule] = useState<any>(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [importOpen, setImportOpen] = useState(false);
  const [importKey, setImportKey] = useState('');
  const [importYamlText, setImportYamlText] = useState('');
  const [editingRule, setEditingRule] = useState<RuleItem | null>(null);
  const [editYamlText, setEditYamlText] = useState('');

  useEffect(() => {
    const controller = new AbortController();
    loadRules(controller.signal);
    return () => controller.abort();
  }, [sourceFilter]);

  const loadRules = async (signal?: AbortSignal) => {
    setLoading(true);
    try {
      const response = await apiClient.get<{ rules?: RuleItem[] }>(`/api/rules/?source=${sourceFilter}`, { signal });
      if (!signal?.aborted) {
        setRules(response.rules || []);
      }
    } catch (error: any) {
      if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED') return;
      console.error('Load rules error:', error);
    } finally {
      if (!signal?.aborted) {
        setLoading(false);
      }
    }
  };

  const handleViewRule = async (rule: RuleItem) => {
    try {
      const response = await apiClient.get<Record<string, unknown> & { content?: unknown }>(`/api/rules/${rule.key}?source_type=${rule.source_type}`);
      setSelectedRule({ ...response, source_type: rule.source_type });
      setDetailOpen(true);
    } catch (error) {
      console.error('Load rule details error:', error);
    }
  };

  const handleDelete = async (rule: RuleItem) => {
    if (!await confirm('确认', `确认删除规则 "${rule.name}"?`)) return;
    try {
      await apiClient.delete(`/api/rules/${rule.key}?source_type=${rule.source_type}`);
      loadRules();
    } catch (error) {
      console.error('Delete rule error:', error);
    }
  };

  const handleImport = async () => {
    if (!importKey.trim() || !importYamlText.trim()) {
      warning('提示', '请填写规则KEY和YAML内容');
      return;
    }
    try {
      await apiClient.post('/api/rules/import', {
        key: importKey.trim(),
        yaml_text: importYamlText,
        source_type: 'user',
      });
      setImportOpen(false);
      setImportKey('');
      setImportYamlText('');
      loadRules();
    } catch (error: any) {
      showError('错误', '导入失败: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleExport = async (rule: RuleItem) => {
    try {
      const response = await apiClient.post<{ yaml_text: string }>('/api/rules/export', {
        key: rule.key,
        source_type: rule.source_type,
      });
      const blob = new Blob([response.yaml_text], { type: 'text/yaml' });
      const url = URL.createObjectURL(blob);
      try {
        const a = document.createElement('a');
        a.href = url;
        a.download = `${rule.key}.yaml`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      } finally {
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export error:', error);
    }
  };

  const handleEnableToggle = async (rule: RuleItem) => {
    try {
      await apiClient.put(`/api/rules/${rule.key}`, {
        source_type: rule.source_type,
        content: selectedRule?.content || { enabled: !rule.enabled },
      });
      loadRules();
    } catch (error) {
      console.error('Toggle error:', error);
    }
  };

  if (loading) {
    return (
      <div className="w-full bg-primary-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  return (
    <div className="w-full bg-primary-50">
      <PageHeader
        title="规则管理"
        description={`当前共 ${rules.length} 个规则 (${sourceFilter === 'all' ? '全部' : sourceLabels[sourceFilter]})`}
      />

      <div className="p-4 md:p-6 lg:p-8 w-full">
        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
          <Tabs value={sourceFilter} onValueChange={setSourceFilter} className="w-auto">
            <TabsList>
              <TabsTrigger value="all"><Layers className="h-4 w-4 mr-1" />全部</TabsTrigger>
              <TabsTrigger value="official"><BookOpen className="h-4 w-4 mr-1" />官方</TabsTrigger>
              <TabsTrigger value="custom"><Building2 className="h-4 w-4 mr-1" />单位</TabsTrigger>
              <TabsTrigger value="user"><User className="h-4 w-4 mr-1" />用户</TabsTrigger>
            </TabsList>
          </Tabs>
          <Button variant="outline" onClick={() => setImportOpen(true)}>
            <Upload className="h-4 w-4 mr-2" />导入规则
          </Button>
        </div>

        {/* Rules Grid */}
        {rules.length === 0 ? (
          <Card className="border-primary-200">
            <CardContent className="p-12 text-center text-primary-500">
              <FileCode className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg">暂无规则文件</p>
              <p className="text-sm mt-2">点击"导入规则"按钮添加 YAML 规则</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid-auto-fill">
            {rules.map((rule) => (
              <Card key={`${rule.source_type}-${rule.key}`} className="border-primary-200 hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {sourceIcons[rule.source_type]}
                      <Badge className={sourceColors[rule.source_type]}>
                        {sourceLabels[rule.source_type]}
                      </Badge>
                    </div>
                    <Badge variant={rule.enabled ? 'default' : 'secondary'}>
                      {rule.enabled ? '启用' : '禁用'}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{rule.name}</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm text-primary-600 mb-4">
                    <p>KEY: {rule.key}</p>
                    <p>大小: {(rule.size / 1024).toFixed(2)} KB</p>
                  </div>
                  <div className="flex gap-2 flex-wrap">
                    <Button variant="outline" size="sm" onClick={() => handleViewRule(rule)}>
                      <Eye className="h-4 w-4 mr-1" />查看
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleExport(rule)}>
                      <Download className="h-4 w-4 mr-1" />导出
                    </Button>
                    {rule.source_type !== 'official' && (
                      <>
                        <Button variant="outline" size="sm" onClick={() => handleEnableToggle(rule)}>
                          {rule.enabled ? '禁用' : '启用'}
                        </Button>
                        <Button variant="outline" size="sm" className="text-status-error" onClick={() => handleDelete(rule)}>
                          <Trash2 className="h-4 w-4 mr-1" />删除
                        </Button>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Rule Detail Dialog */}
        <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
          <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                规则详情
                {selectedRule?.source_type && (
                  <Badge className={sourceColors[selectedRule.source_type]}>
                    {sourceLabels[selectedRule.source_type]}
                  </Badge>
                )}
              </DialogTitle>
            </DialogHeader>
            {selectedRule?.content ? (
              <div className="space-y-4">
                <div className="text-sm space-y-1">
                  <p><b>KEY:</b> {selectedRule.key}</p>
                  <p><b>类型:</b> {sourceLabels[selectedRule.source_type]}</p>
                  {selectedRule.content.template_name && <p><b>模板:</b> {selectedRule.content.template_name}</p>}
                  {selectedRule.content.document_type && <p><b>文档类型:</b> {selectedRule.content.document_type}</p>}
                </div>
                {selectedRule.content.check_rules && (
                  <div>
                    <h3 className="font-medium mb-2">检查规则 ({selectedRule.content.check_rules.length})</h3>
                    <div className="space-y-2">
                      {selectedRule.content.check_rules.slice(0, 10).map((rule: any, i: number) => (
                        <div key={i} className="p-3 bg-primary-50 rounded text-sm">
                          <span className="font-medium">{rule.name}</span>
                          <span className="text-xs ml-2 text-primary-600">{rule.message}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {selectedRule.content.fix_rules && (
                  <div>
                    <h3 className="font-medium mb-2">修复规则 ({selectedRule.content.fix_rules.length})</h3>
                    <p className="text-sm text-primary-600">包含 {selectedRule.content.fix_rules.length} 条自动修复规则</p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-status-error py-4">规则加载失败</p>
            )}
          </DialogContent>
        </Dialog>

        {/* Import Rule Dialog */}
        <Dialog open={importOpen} onOpenChange={setImportOpen}>
          <DialogContent className="max-w-xl">
            <DialogHeader>
              <DialogTitle>导入规则</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">规则 KEY</label>
                <Input
                  value={importKey}
                  onChange={(e) => setImportKey(e.target.value)}
                  placeholder="例如: my_custom_rule"
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm font-medium">YAML 内容</label>
                <Textarea
                  value={importYamlText}
                  onChange={(e) => setImportYamlText(e.target.value)}
                  placeholder="# 规则定义...&#10;fix_rules:&#10;  - id: FIX-001&#10;    action: set_font&#10;    target: body&#10;    value: SimHei"
                  className="mt-1 font-mono text-sm"
                  rows={12}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setImportOpen(false)}>取消</Button>
                <Button onClick={handleImport}><Plus className="h-4 w-4 mr-1" />导入</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
