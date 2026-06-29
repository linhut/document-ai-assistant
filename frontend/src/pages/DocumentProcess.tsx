/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * DocumentProcess - 文档处理页面
 * 选择文档、选择类型、开始检查
 */
import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, Loader2, CheckCircle2, ChevronDown, Eye, ArrowRight } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/api/client';
import { useToast } from '@/components/ui/toast';
import A4PreviewModal from '@/components/A4PreviewModal';

interface DocumentType {
  value: string;
  label: string;
  category: string;
  description: string;
}

export default function DocumentProcess() {
  const navigate = useNavigate();
  const { warning } = useToast();
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [docId, setDocId] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [documentTypes, setDocumentTypes] = useState<DocumentType[]>([]);
  const [typeSearch, setTypeSearch] = useState('');
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);
  const [checkComplete, setCheckComplete] = useState(false);
  const [showA4Preview, setShowA4Preview] = useState(false);
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

  // 根据搜索词过滤类型（支持中文名和英文标识双向匹配）
  const filteredDocTypes = typeSearch.trim()
    ? documentTypes.filter(t =>
        t.value.toLowerCase().includes(typeSearch.toLowerCase()) ||
        t.label.includes(typeSearch)
      )
    : documentTypes;

  // 按分类分组过滤后的类型
  const filteredGovernment = filteredDocTypes.filter(t => t.category === 'government');
  const filteredCommon = filteredDocTypes.filter(t => t.category === 'common');
  const filteredCustom = filteredDocTypes.filter(t => t.category === 'custom');

  // 获取当前选中类型的显示名
  const selectedTypeLabel = documentTypes.find(t => t.value === documentType)?.label;

  // 从后端API动态获取文档类型列表（包含官方+自定义）
  useEffect(() => {
    const controller = new AbortController();

    const loadDocumentTypes = async () => {
      try {
        const response = await apiClient.get<{ templates?: Array<{ id: string; name: string; category?: string; source?: string; description?: string }> }>('/api/templates/list', { signal: controller.signal });
        if (controller.signal.aborted) return;
        const templates = response.templates || [];
        const types: DocumentType[] = templates.map((t) => ({
          value: t.id,
          label: t.name,
          category: t.category || (t.source === 'custom' || t.source === 'user' ? 'custom' : 'government'),
          description: t.description || '',
        }));
        setDocumentTypes(types);
      } catch (error: any) {
        if (error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED') return;
        console.error('Failed to load document types:', error);
        // 回退到基础列表
        setDocumentTypes([
          { value: 'notice', label: '通知', category: 'government', description: '' },
          { value: 'request', label: '请示', category: 'government', description: '' },
          { value: 'report', label: '报告', category: 'government', description: '' },
          { value: 'letter', label: '函', category: 'government', description: '' },
        ]);
      }
    };
    loadDocumentTypes();
    return () => controller.abort();
  }, []);

  const isSupportedFormat = (name: string) => {
    const ext = name.toLowerCase().split('.').pop();
    return ext === 'docx' || ext === 'doc' || ext === 'wps';
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && isSupportedFormat(selectedFile.name)) {
      setFile(selectedFile);
      setErrorMessage('');
    } else {
      warning('提示', '请选择 .docx、.doc 或 .wps 格式的文档');
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && isSupportedFormat(droppedFile.name)) {
      setFile(droppedFile);
      setErrorMessage('');
    }
  };

  const handleStartCheck = async () => {
    if (!file || !documentType) {
      warning('提示', '请先选择文档并选择类型');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setErrorMessage('');

    try {
      // Step 1: Upload document
      setCurrentStep('正在上传文档...');
      setProgress(20);

      const formData = new FormData();
      formData.append('file', file);

      const uploadResponse = await apiClient.post<{ id: number }>('/api/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const uploadedDocId = uploadResponse.id;
      setDocId(uploadedDocId);

      // Step 2: Run format check
      setCurrentStep('正在执行格式检查...');
      setProgress(50);

      await apiClient.post(`/api/check/${uploadedDocId}`, {
        document_type: documentType,
      });

      // Step 3: Complete
      setCurrentStep('检查完成！');
      setProgress(100);
      setCheckComplete(true);
      setIsProcessing(false);

    } catch (error: any) {
      setErrorMessage(error.response?.data?.detail || '处理失败，请重试');
      setIsProcessing(false);
      console.error('Processing error:', error);
    }
  };

  return (
    <div className="w-full bg-primary-50">
      <PageHeader
        title="文档处理"
        description="选择 Word 文档开始智能检查"
      />

      <div className="p-4 md:p-6 lg:p-8 w-full space-y-6">
        {/* Error Message */}
        {errorMessage && (
          <div className="p-4 bg-status-error-bg border border-status-error/20 rounded-lg text-status-error">
            {errorMessage}
          </div>
        )}

        {/* 文件选择区域 */}
        {!file ? (
          <Card
            className="border-2 border-dashed border-primary-200 hover:border-accent hover:bg-accent-light/10 transition-colors cursor-pointer"
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <CardContent className="py-16">
              <div className="text-center">
                <Upload className="mx-auto h-12 w-12 text-primary-300 mb-4" />
                <p className="text-lg text-primary-700 font-medium">
                  拖拽文件到此处
                </p>
                <p className="text-sm text-primary-500 mt-2">
                  或点击选择 Word 文档
                </p>
                <p className="text-xs text-primary-400 mt-4">
                  支持格式：.docx / .doc / .wps | 建议 10MB 以内
                </p>
                <p className="text-xs text-status-warning mt-1">
                  大型文档（超过10MB）建议使用 WPS/Word 插件
                </p>
              </div>
              <input
                id="file-input"
                type="file"
                accept=".docx,.doc,.wps"
                className="hidden"
                onChange={handleFileSelect}
              />
            </CardContent>
          </Card>
        ) : (
          <>
            {/* 已选择文件 */}
            <Card>
              <CardContent className="py-6">
                <div className="flex items-center gap-4">
                  <FileText className="h-10 w-10 text-accent" />
                  <div className="flex-1">
                    <p className="font-medium text-primary-900">{file.name}</p>
                    <p className="text-sm text-primary-500">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setFile(null);
                      setDocumentType('');
                      setProgress(0);
                    }}
                    disabled={isProcessing}
                  >
                    重新选择
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 文档类型选择 — 带搜索的动态下拉 */}
            <Card>
              <CardContent className="py-6">
                <label className="block text-sm font-medium text-primary-700 mb-2">
                  文档类型
                </label>
                <div className="relative">
                  <div className="relative">
                    <input
                      ref={typeInputRef}
                      type="text"
                      value={showTypeDropdown ? typeSearch : (documentType ? `${selectedTypeLabel || ''}（${documentType}）` : '')}
                      onChange={(e) => {
                        setTypeSearch(e.target.value);
                        setShowTypeDropdown(true);
                        // 如果清空了搜索词，也清空选中
                        if (!e.target.value) setDocumentType('');
                      }}
                      onFocus={() => {
                        setTypeSearch('');
                        setShowTypeDropdown(true);
                      }}
                      onBlur={() => {
                        blurTimeoutRef.current = setTimeout(() => setShowTypeDropdown(false), 200);
                      }}
                      placeholder="输入搜索或点击选择文档类型"
                      disabled={isProcessing}
                      className="w-full border border-primary-200 rounded-md px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-accent disabled:opacity-50"
                    />
                    <ChevronDown
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-primary-400 cursor-pointer"
                      onClick={() => {
                        if (!isProcessing) {
                          setShowTypeDropdown(!showTypeDropdown);
                          typeInputRef.current?.focus();
                        }
                      }}
                    />
                  </div>
                  {showTypeDropdown && (
                    <div className="absolute z-50 w-full mt-1 bg-white border border-primary-200 rounded-lg shadow-lg max-h-64 overflow-y-auto">
                      {filteredGovernment.length > 0 && (
                        <>
                          <div className="px-3 py-1.5 text-xs font-medium text-primary-400 bg-primary-50 sticky top-0">政府机关</div>
                          {filteredGovernment.map(t => (
                            <div
                              key={t.value}
                              className={`px-3 py-2 text-sm cursor-pointer hover:bg-primary-50 flex items-center justify-between ${documentType === t.value ? 'bg-accent/10 text-accent' : ''}`}
                              onMouseDown={(e) => { e.preventDefault(); setDocumentType(t.value); setTypeSearch(''); setShowTypeDropdown(false); }}
                            >
                              <span className="font-medium">{t.label}</span>
                              <span className="text-xs text-muted-foreground">{t.value}</span>
                            </div>
                          ))}
                        </>
                      )}
                      {filteredCommon.length > 0 && (
                        <>
                          <div className="px-3 py-1.5 text-xs font-medium text-primary-400 bg-primary-50 sticky top-0">其他常用</div>
                          {filteredCommon.map(t => (
                            <div
                              key={t.value}
                              className={`px-3 py-2 text-sm cursor-pointer hover:bg-primary-50 flex items-center justify-between ${documentType === t.value ? 'bg-accent/10 text-accent' : ''}`}
                              onMouseDown={(e) => { e.preventDefault(); setDocumentType(t.value); setTypeSearch(''); setShowTypeDropdown(false); }}
                            >
                              <span className="font-medium">{t.label}</span>
                              <span className="text-xs text-muted-foreground">{t.value}</span>
                            </div>
                          ))}
                        </>
                      )}
                      {filteredCustom.length > 0 && (
                        <>
                          <div className="px-3 py-1.5 text-xs font-medium text-primary-400 bg-primary-50 sticky top-0">📋 自定义</div>
                          {filteredCustom.map(t => (
                            <div
                              key={t.value}
                              className={`px-3 py-2 text-sm cursor-pointer hover:bg-primary-50 flex items-center justify-between ${documentType === t.value ? 'bg-accent/10 text-accent' : ''}`}
                              onMouseDown={(e) => { e.preventDefault(); setDocumentType(t.value); setTypeSearch(''); setShowTypeDropdown(false); }}
                            >
                              <span className="font-medium">{t.label}</span>
                              <span className="text-xs text-muted-foreground">{t.value}</span>
                            </div>
                          ))}
                        </>
                      )}
                      {filteredDocTypes.length === 0 && (
                        <div className="px-3 py-4 text-sm text-muted-foreground text-center">
                          未找到匹配的文档类型
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* 处理进度 */}
            {isProcessing && (
              <Card>
                <CardContent className="py-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-5 w-5 animate-spin text-accent" />
                      <span className="text-sm text-primary-700">{currentStep}</span>
                    </div>
                    <Progress value={progress} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 检查完成 — 操作入口 */}
            {checkComplete && docId && (
              <Card className="border-status-success/30">
                <CardContent className="py-6">
                  <div className="flex items-center gap-3 mb-4">
                    <CheckCircle2 className="h-6 w-6 text-status-success" />
                    <div>
                      <p className="font-medium text-primary-900">格式检查完成</p>
                      <p className="text-sm text-primary-500">{file?.name}</p>
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <Button className="flex-1" onClick={() => navigate(`/document/check?docId=${docId}&type=${documentType}`)}>
                      <ArrowRight className="h-4 w-4 mr-1.5" />查看检查结果
                    </Button>
                    <Button variant="outline" className="flex-1" onClick={() => setShowA4Preview(true)}>
                      <Eye className="h-4 w-4 mr-1.5" />A4 预览
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* 开始检查按钮 */}
            {!checkComplete && (
              <Button
                className="w-full h-12 text-base"
                onClick={handleStartCheck}
                disabled={!documentType || isProcessing}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    处理中...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="h-5 w-5 mr-2" />
                    开始检查
                  </>
                )}
              </Button>
            )}
          </>
        )}
      </div>

      {/* A4 预览弹窗 */}
      {showA4Preview && docId && (
        <A4PreviewModal
          docId={docId}
          onClose={() => setShowA4Preview(false)}
        />
      )}
    </div>
  );
}
