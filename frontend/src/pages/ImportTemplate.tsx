/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */

/**
 * ImportTemplate - 导入文档自动生成模板规则
 * 上传已排版文档 → 自动提取格式 → 预览 → 保存为自定义规则
 */
import { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Loader2, CheckCircle2, Save, Eye, ChevronDown } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/api/client';
import { useToast } from '@/components/ui/toast';

interface FormatSection {
  label: string;
  count: number;
  format: string;
}

interface ExtractResult {
  success: boolean;
  template_name: string;
  document_type: string;
  format_info: Record<string, FormatSection>;
  sections: Record<string, Record<string, any> | null>;
  page_setup: Record<string, any>;
  check_rules_count: number;
  fix_rules_count: number;
  yaml_preview: string;
  yaml_content: Record<string, any>;
}

export default function ImportTemplate() {
  const { success: toastSuccess, error: toastError, warning } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 状态
  const [file, setFile] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [result, setResult] = useState<ExtractResult | null>(null);
  const [templateName, setTemplateName] = useState('');
  const [documentType, setDocumentType] = useState('');
  const [saving, setSaving] = useState(false);
  const [showYaml, setShowYaml] = useState(false);
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);
  const typeInputRef = useRef<HTMLInputElement>(null);
  const blurTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup blur timeout on unmount to prevent setState on unmounted component
  useEffect(() => {
    return () => {
      if (blurTimeoutRef.current) {
        clearTimeout(blurTimeoutRef.current);
        blurTimeoutRef.current = null;
      }
    };
  }, []);

  // 已知文档类型列表（用于下拉建议）
  const KNOWN_TYPES = [
    { value: 'notice', label: '通知' },
    { value: 'command', label: '命令（令）' },
    { value: 'decision', label: '决定' },
    { value: 'announcement', label: '通告' },
    { value: 'bulletin', label: '通报' },
    { value: 'bill', label: '议案' },
    { value: 'report', label: '报告' },
    { value: 'request', label: '请示' },
    { value: 'reply', label: '批复' },
    { value: 'letter', label: '函' },
    { value: 'meeting', label: '会议纪要' },
    { value: 'minutes', label: '纪要' },
    { value: 'resolution', label: '决议' },
    { value: 'instruction', label: '指示' },
    { value: 'regulation', label: '制度' },
    { value: 'communique', label: '公报' },
    { value: 'opinion', label: '意见' },
    { value: 'notice_public', label: '公告' },
    { value: 'summary', label: '总结' },
    { value: 'work_plan', label: '工作方案' },
    { value: 'table_sign', label: '桌签' },
    { value: 'technical_proposal', label: '技术方案' },
  ];

  // 根据输入内容过滤匹配的类型
  const filteredTypes = documentType.trim()
    ? KNOWN_TYPES.filter(t =>
        t.value.includes(documentType.toLowerCase()) ||
        t.label.includes(documentType)
      )
    : KNOWN_TYPES;

  const isSupported = (name: string) => {
    const ext = name.toLowerCase().split('.').pop();
    return ext === 'docx' || ext === 'doc' || ext === 'wps';
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f && isSupported(f.name)) {
      setFile(f);
      setResult(null);
    } else {
      warning('提示', '请选择 .docx、.doc 或 .wps 格式的文档');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f && isSupported(f.name)) {
      setFile(f);
      setResult(null);
    }
  };

  const handleExtract = async () => {
    if (!file) return;
    setExtracting(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const resp = await apiClient.post<ExtractResult>('/api/templates/extract', formData, {
        headers: { 'Content-Type': undefined },
        timeout: 60000,
      });

      setResult(resp);
      setTemplateName(resp.template_name || file.name.replace(/\.\w+$/, ''));
      setDocumentType(resp.document_type || '');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || '格式提取失败';
      toastError('提取失败', String(msg));
    } finally {
      setExtracting(false);
    }
  };

  const handleSave = async () => {
    if (!result || !templateName.trim() || !documentType.trim()) {
      warning('提示', '请填写模板名称和文档类型标识');
      return;
    }

    setSaving(true);
    try {
      await apiClient.post('/api/templates/save-extracted', {
        template_name: templateName.trim(),
        document_type: documentType.trim(),
        yaml_content: result.yaml_content,
      });
      toastSuccess('保存成功', `模板 "${templateName}" 已保存为自定义规则，可用于格式检查和优化`);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || '保存失败';
      toastError('保存失败', String(msg));
    } finally {
      setSaving(false);
    }
  };

  // 格式区段的显示名称和颜色
  const sectionDisplay: Record<string, { label: string; color: string }> = {
    title: { label: '公文标题', color: 'bg-red-50 text-red-700 border-red-200' },
    heading_1: { label: '一级标题', color: 'bg-orange-50 text-orange-700 border-orange-200' },
    heading_2: { label: '二级标题', color: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
    heading_3: { label: '三级标题', color: 'bg-green-50 text-green-700 border-green-200' },
    body: { label: '正文', color: 'bg-blue-50 text-blue-700 border-blue-200' },
    signature: { label: '落款', color: 'bg-purple-50 text-purple-700 border-purple-200' },
    date: { label: '日期', color: 'bg-gray-50 text-gray-700 border-gray-200' },
    page_setup: { label: '页面设置', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
  };

  return (
    <div className="min-h-screen bg-primary-50">
      <PageHeader
        title="导入模板"
        description="从已排版文档自动提取格式规则"
      />

      <div className="max-w-5xl mx-auto p-6 space-y-6">
        {/* 上传区 */}
        <Card>
          <CardContent className="p-6">
            <div
              className="border-2 border-dashed border-primary-200 rounded-xl p-8 text-center cursor-pointer hover:border-accent hover:bg-primary-100 transition-all"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".docx,.doc,.wps"
                className="hidden"
                onChange={handleFileSelect}
              />
              {file ? (
                <div className="flex items-center justify-center gap-3">
                  <FileText className="h-8 w-8 text-accent" />
                  <div className="text-left">
                    <p className="font-medium text-primary-900">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <Button variant="outline" size="sm" className="ml-4" onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                    setResult(null);
                  }}>
                    更换
                  </Button>
                </div>
              ) : (
                <>
                  <Upload className="h-10 w-10 text-primary-300 mx-auto mb-3" />
                  <p className="text-primary-600 font-medium">点击或拖拽上传已排版文档</p>
                  <p className="text-sm text-muted-foreground mt-1">支持 .docx、.doc、.wps 格式</p>
                </>
              )}
            </div>

            <div className="mt-4 flex justify-center">
              <Button
                onClick={handleExtract}
                disabled={!file || extracting}
                className="px-8"
              >
                {extracting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    正在提取格式...
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    提取格式信息
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 格式预览区 */}
        {result && (
          <>
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                  <h3 className="font-semibold text-primary-900">提取到的格式信息</h3>
                  <Badge variant="outline" className="ml-auto">
                    {result.check_rules_count} 条检查规则 / {result.fix_rules_count} 条修复规则
                  </Badge>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(result.format_info).map(([key, info]) => {
                    const display = sectionDisplay[key];
                    if (!display) return null;
                    return (
                      <div
                        key={key}
                        className={`border rounded-lg p-3 ${display.color}`}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-sm">{info.label}</span>
                          {info.count > 0 && key !== 'page_setup' && (
                            <span className="text-xs opacity-70">{info.count} 段</span>
                          )}
                        </div>
                        <p className="text-sm opacity-90">{info.format}</p>
                      </div>
                    );
                  })}
                </div>

                {/* 详细格式表格 */}
                <details className="mt-4">
                  <summary className="text-sm text-muted-foreground cursor-pointer hover:text-primary-700">
                    查看详细格式参数
                  </summary>
                  <div className="mt-3 overflow-x-auto">
                    <table className="w-full text-sm border-collapse">
                      <thead>
                        <tr className="bg-primary-50">
                          <th className="border border-primary-200 px-3 py-2 text-left">区段</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">字体</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">字号</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">对齐</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">缩进</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">行距</th>
                          <th className="border border-primary-200 px-3 py-2 text-left">加粗</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(result.sections).map(([key, sec]) => {
                          if (!sec) return null;
                          const display = sectionDisplay[key];
                          return (
                            <tr key={key}>
                              <td className="border border-primary-200 px-3 py-1.5 font-medium">
                                {display?.label || key}
                              </td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.font || '-'}</td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.size || '-'}</td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.align || '-'}</td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.first_line_indent || '-'}</td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.line_spacing || '-'}</td>
                              <td className="border border-primary-200 px-3 py-1.5">{sec.bold ? '是' : '-'}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </details>

                {/* YAML 预览 */}
                <details className="mt-3" open={showYaml}>
                  <summary
                    className="text-sm text-muted-foreground cursor-pointer hover:text-primary-700"
                    onClick={() => setShowYaml(!showYaml)}
                  >
                    查看生成的 YAML 规则
                  </summary>
                  <pre className="mt-2 p-4 bg-gray-900 text-gray-100 rounded-lg text-xs overflow-auto max-h-96">
                    {result.yaml_preview}
                  </pre>
                </details>
              </CardContent>
            </Card>

            {/* 保存区 */}
            <Card>
              <CardContent className="p-6">
                <h3 className="font-semibold text-primary-900 mb-4">保存为自定义规则</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-primary-700 mb-1.5">
                      模板名称
                    </label>
                    <input
                      type="text"
                      value={templateName}
                      onChange={(e) => setTemplateName(e.target.value)}
                      placeholder="如：XX局通知模板"
                      className="w-full border border-primary-200 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                    />
                  </div>
                  <div className="relative">
                    <label className="block text-sm font-medium text-primary-700 mb-1.5">
                      文档类型标识
                    </label>
                    <div className="relative">
                      <input
                        ref={typeInputRef}
                        type="text"
                        value={documentType}
                        onChange={(e) => {
                          setDocumentType(e.target.value);
                          setShowTypeDropdown(true);
                        }}
                        onFocus={() => setShowTypeDropdown(true)}
                        onBlur={() => {
                          blurTimeoutRef.current = setTimeout(() => setShowTypeDropdown(false), 200);
                        }}
                        placeholder="输入或选择文档类型"
                        className="w-full border border-primary-200 rounded-md px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-accent"
                      />
                      <ChevronDown
                        className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-primary-400 cursor-pointer"
                        onClick={() => {
                          setShowTypeDropdown(!showTypeDropdown);
                          typeInputRef.current?.focus();
                        }}
                      />
                    </div>
                    {/* 下拉建议列表 */}
                    {showTypeDropdown && filteredTypes.length > 0 && (
                      <div className="absolute z-50 w-full mt-1 bg-white border border-primary-200 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                        {filteredTypes.map(t => (
                          <div
                            key={t.value}
                            className="px-3 py-2 text-sm cursor-pointer hover:bg-primary-50 flex items-center justify-between"
                            onMouseDown={(e) => {
                              e.preventDefault();
                              setDocumentType(t.value);
                              setShowTypeDropdown(false);
                            }}
                          >
                            <span className="font-medium">{t.label}</span>
                            <span className="text-xs text-muted-foreground">{t.value}</span>
                          </div>
                        ))}
                      </div>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      可下拉选择已有类型，也可手动输入新类型标识
                    </p>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <Button onClick={handleSave} disabled={saving} className="px-6">
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        保存中...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        保存规则
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </div>
  );
}
