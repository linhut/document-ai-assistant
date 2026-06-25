/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * TemplateRules - 模板规则编辑页面
 * 编辑指定模板的检查和修复规则
 */
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Save, Plus, Trash2, Loader2 } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { apiClient } from '@/api/client';
import { useToast } from '@/components/ui/toast';

interface CheckRule {
  id: string;
  name: string;
  severity: 'P0' | 'P1' | 'P2';
  field: string;
  expected: string;
  message: string;
}

export default function TemplateRules() {
  const { templateId } = useParams<{ templateId: string }>();
  const navigate = useNavigate();
  const { success, error: showError, info, confirm } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [template, setTemplate] = useState<any>(null);
  const [rules, setRules] = useState<CheckRule[]>([]);

  useEffect(() => {
    loadTemplateRules();
  }, [templateId]);

  const loadTemplateRules = async () => {
    try {
      const response = await apiClient.get(`/api/templates/${templateId}`);
      setTemplate(response);
      if (response.rules?.check_rules) {
        setRules(response.rules.check_rules);
      }
    } catch (error) {
      console.error('Load template rules error:', error);
    } finally {
      setLoading(false);
    }
  };

  const addRule = () => {
    const newRule: CheckRule = {
      id: `CHK-${String(rules.length + 1).padStart(3, '0')}`,
      name: '新规则',
      severity: 'P1',
      field: '',
      expected: '',
      message: ''
    };
    setRules([...rules, newRule]);
  };

  const updateRule = (index: number, field: keyof CheckRule, value: string) => {
    const updated = [...rules];
    updated[index] = { ...updated[index], [field]: value };
    setRules(updated);
  };

  const removeRule = async (index: number) => {
    if (await confirm('确认', '确定要删除此规则吗？')) {
      setRules(rules.filter((_, i) => i !== index));
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // TODO: 实现保存规则API
      info('提示', '规则保存功能将在后续版本实现');
      // await apiClient.put(`/api/templates/${templateId}/rules`, { check_rules: rules });
      // success('成功', '规则保存成功！');
    } catch (error: any) {
      showError('错误', '保存失败：' + (error.response?.data?.detail || '请重试'));
    } finally {
      setSaving(false);
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
        title={`编辑规则：${template?.rules?.template_name || templateId}`}
        description="配置文档格式检查规则"
        actions={
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => navigate('/templates')}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              返回
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving}
            >
              <Save className="h-4 w-4 mr-2" />
              {saving ? '保存中...' : '保存'}
            </Button>
          </div>
        }
      />

      <div className="p-4 md:p-6 lg:p-8 w-full space-y-6">
        {/* 模板信息 */}
        <Card>
          <CardHeader>
            <CardTitle>模板信息</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-muted-foreground">模板名称：</span>
              <span className="font-medium">{template?.rules?.template_name}</span>
            </div>
            <div>
              <span className="text-muted-foreground">文档类型：</span>
              <span className="font-medium">{template?.rules?.document_type}</span>
            </div>
            <div>
              <span className="text-muted-foreground">当前规则数：</span>
              <span className="font-medium">{rules.length} 条</span>
            </div>
          </CardContent>
        </Card>

        {/* 规则列表 */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">检查规则</h2>
            <Button onClick={addRule} variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              添加规则
            </Button>
          </div>

          {rules.map((rule, index) => (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <Label>规则ID</Label>
                    <Input
                      value={rule.id}
                      onChange={(e) => updateRule(index, 'id', e.target.value)}
                      placeholder="CHK-001"
                    />
                  </div>
                  <div>
                    <Label>规则名称</Label>
                    <Input
                      value={rule.name}
                      onChange={(e) => updateRule(index, 'name', e.target.value)}
                      placeholder="例如：标题字体检查"
                    />
                  </div>
                  <div>
                    <Label>严重程度</Label>
                    <select
                      className="w-full border border-primary-200 rounded-md px-3 py-2 bg-white text-sm focus:outline-none focus:ring-1 focus:ring-accent"
                      value={rule.severity}
                      onChange={(e) => updateRule(index, 'severity', e.target.value as any)}
                    >
                      <option value="P0">P0 - 必须修复</option>
                      <option value="P1">P1 - 建议修复</option>
                      <option value="P2">P2 - 可选修复</option>
                    </select>
                  </div>
                  <div>
                    <Label>检查字段</Label>
                    <select
                      className="w-full border border-primary-200 rounded-md px-3 py-2 bg-white text-sm focus:outline-none focus:ring-1 focus:ring-accent"
                      value={rule.field}
                      onChange={(e) => updateRule(index, 'field', e.target.value)}
                    >
                      <option value="">请选择字段</option>
                      <optgroup label="标题相关">
                        <option value="title.font">标题字体</option>
                        <option value="title.size">标题字号</option>
                        <option value="title.align">标题对齐</option>
                        <option value="title.bold">标题加粗</option>
                        <option value="title.color">标题颜色</option>
                      </optgroup>
                      <optgroup label="正文相关">
                        <option value="body.font">正文字体</option>
                        <option value="body.size">正文字号</option>
                        <option value="body.align">正文对齐</option>
                        <option value="body.first_line_indent">正文首行缩进</option>
                        <option value="body.line_spacing">正文行距</option>
                      </optgroup>
                      <optgroup label="落款相关">
                        <option value="signature.align">落款对齐</option>
                        <option value="signature.font">落款字体</option>
                        <option value="signature.size">落款字号</option>
                      </optgroup>
                      <optgroup label="页面设置">
                        <option value="page.margin_top">上边距</option>
                        <option value="page.margin_bottom">下边距</option>
                        <option value="page.margin_left">左边距</option>
                        <option value="page.margin_right">右边距</option>
                      </optgroup>
                    </select>
                  </div>
                  <div>
                    <Label>期望值</Label>
                    <Input
                      value={rule.expected}
                      onChange={(e) => updateRule(index, 'expected', e.target.value)}
                      placeholder="例如：方正小标宋简体"
                    />
                  </div>
                  <div className="col-span-2">
                    <Label>提示信息</Label>
                    <Input
                      value={rule.message}
                      onChange={(e) => updateRule(index, 'message', e.target.value)}
                      placeholder="例如：标题应使用方正小标宋简体"
                    />
                  </div>
                  <div className="col-span-2 flex justify-end">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => removeRule(index)}
                      className="text-status-error hover:text-status-error hover:bg-status-error-bg"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      删除规则
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {rules.length === 0 && (
            <Card>
              <CardContent className="py-12 text-center text-muted-foreground">
                <p>暂无规则，点击"添加规则"开始配置</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
