/*
 * This file is part of the Official Document AI Assistant.
 * (c) 2026 Jose AI (https://www.linhut.cn)
 * Licensed under the MIT License. See the LICENSE file for details.
 */
/**
 * About - 关于页面（优化宽度布局）
 */
import { useState, useEffect } from 'react';
import { FileText, Mail, ExternalLink, Download, FileType, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { apiClient, downloadFile } from '@/api/client';

interface FontInfo {
  filename: string;
  display_name: string;
  size_kb: number;
  description: string;
}

function parseVersion(ver: string): number[] {
  return ver.replace(/^v/, '').split('.').map(Number);
}

function isNewer(latest: string, current: string): boolean {
  const lv = parseVersion(latest);
  const cv = parseVersion(current);
  for (let i = 0; i < Math.max(lv.length, cv.length); i++) {
    const a = lv[i] || 0;
    const b = cv[i] || 0;
    if (a > b) return true;
    if (a < b) return false;
  }
  return false;
}

export default function About() {
  const [fonts, setFonts] = useState<FontInfo[]>([]);
  const [latestVersion, setLatestVersion] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const [checkError, setCheckError] = useState(false);

  useEffect(() => {
    loadFonts();
    checkNewVersion();
  }, []);

  const checkNewVersion = async () => {
    setChecking(true);
    setCheckError(false);
    try {
      const resp = await fetch(
        'https://api.github.com/repos/linhut/document-ai-assistant/releases/latest',
        { signal: AbortSignal.timeout(8000) }
      );
      if (resp.ok) {
        const data = await resp.json();
        setLatestVersion(data.tag_name || '');
      } else {
        setCheckError(true);
      }
    } catch {
      setCheckError(true);
    } finally {
      setChecking(false);
    }
  };

  const hasNewVersion = latestVersion && isNewer(latestVersion, __APP_VERSION__);

  useEffect(() => {
    loadFonts();
  }, []);

  const loadFonts = async () => {
    try {
      const resp = await apiClient.get<{ fonts?: FontInfo[] }>('/api/settings/fonts');
      setFonts(resp.fonts || []);
    } catch (error) {
      console.error('Load fonts error:', error);
    }
  };

  const handleDownloadFont = (font: FontInfo) => {
    downloadFile(`/api/settings/fonts/download/${font.filename}`, font.filename);
  };

  const features = [
    { icon: '🔒', title: '本地运行', description: '数据不上传云端，保障公文安全' },
    { icon: '⚡', title: '一键检测', description: '自动检测格式问题，提升效率' },
    { icon: '🤖', title: 'AI 增强', description: '支持多家大模型智能分析' },
    { icon: '📝', title: '规则驱动', description: '易于扩展与维护配置规则' },
    { icon: '🎨', title: '界面美观', description: '专业桌面应用体验' },
    { icon: '📚', title: '22种文种', description: '覆盖全部法定公文文种' },
  ];

  const techStack = [
    { name: 'Electron', description: '桌面容器', icon: '⚛️' },
    { name: 'React', description: 'UI 框架', icon: '⚛️' },
    { name: 'Python', description: '核心引擎', icon: '🐍' },
    { name: 'FastAPI', description: 'API 服务', icon: '⚡' },
    { name: 'python-docx', description: 'Word 处理', icon: '📄' },
    { name: 'SQLite', description: '本地数据库', icon: '💾' },
  ];

  return (
    <div className="w-full bg-primary-50">
      <PageHeader
        title="关于"
        description="软件信息与许可证"
      />

      <div className="p-4 md:p-6 lg:p-8 w-full space-y-6">
        {/* 产品信息 */}
        <Card>
          <CardHeader className="text-center pb-4">
            <div className="flex justify-center mb-4">
              <div className="w-20 h-20 bg-accent rounded-2xl flex items-center justify-center">
                <FileText className="h-12 w-12 text-white" />
              </div>
            </div>
            <CardTitle className="text-2xl">AI 公文智能优化助手</CardTitle>
            <CardDescription>一款专业的本地化公文格式检测与优化工具</CardDescription>
            <div className="flex gap-2 justify-center mt-4">
              <Badge variant="default">版本 {__APP_VERSION__}</Badge>
              {checking ? (
                <Badge variant="secondary" className="flex items-center gap-1">
                  <RefreshCw className="h-3 w-3 animate-spin" />
                  检查更新…
                </Badge>
              ) : checkError ? (
                <Badge variant="outline" className="flex items-center gap-1 text-primary-400">
                  <AlertTriangle className="h-3 w-3" />
                  检查失败
                </Badge>
              ) : hasNewVersion ? (
                <Badge variant="destructive" className="flex items-center gap-1 cursor-pointer" onClick={() => window.open('https://github.com/linhut/document-ai-assistant/releases/latest', '_blank')}>
                  <Download className="h-3 w-3" />
                  新版本 {latestVersion}
                </Badge>
              ) : (
                <Badge className="bg-status-success/15 text-status-success flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  已是最新
                </Badge>
              )}
              <Badge variant="secondary">{new Date().toLocaleDateString('zh-CN')}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-center text-primary-700 max-w-3xl mx-auto">
              本软件旨在为政府机关、企事业单位提供公文格式智能检测与优化服务。
              采用本地运行模式，数据不上传云端，保障文档安全。
              支持 22 种法定公文文种，提供一键检测、自动修复、AI 智能分析等功能。
            </p>
          </CardContent>
        </Card>

        {/* 核心特性 */}
        <section>
          <h2 className="text-xl font-semibold text-primary-900 mb-4">核心特性</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feature) => (
              <Card key={feature.title} className="border-primary-200">
                <CardContent className="pt-6">
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="font-semibold text-primary-900 mb-2">{feature.title}</h3>
                  <p className="text-sm text-primary-600">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* 技术栈 */}
        <section>
          <h2 className="text-xl font-semibold text-primary-900 mb-4">技术栈</h2>
          <Card className="border-primary-200">
            <CardContent className="pt-6">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {techStack.map((tech) => (
                  <div key={tech.name} className="text-center">
                    <div className="text-3xl mb-2">{tech.icon}</div>
                    <div className="font-medium text-primary-900">{tech.name}</div>
                    <div className="text-xs text-primary-600">{tech.description}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 作者与许可 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="border-primary-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                作者与许可
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-sm text-primary-600">作者</div>
                <div className="font-medium">Jose AI</div>
              </div>
              <div>
                <div className="text-sm text-primary-600">网站</div>
                <a href="https://www.linhut.cn" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline flex items-center gap-1">
                  www.linhut.cn
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
              <div>
                <div className="text-sm text-primary-600">许可证</div>
                <div className="font-medium">MIT License</div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-primary-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ExternalLink className="h-5 w-5" />
                开源地址
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-sm text-primary-600">GitHub</div>
                <a href="https://github.com/linhut/document-ai-assistant" target="_blank" rel="noopener noreferrer" className="text-accent hover:underline flex items-center gap-1">
                  github.com/linhut/document-ai-assistant
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
              <div className="text-sm text-primary-600 bg-primary-50 p-3 rounded">
                欢迎 Star、Fork、提交 Issue 和 PR
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 参考标准 */}
        <Card className="border-primary-200">
          <CardHeader>
            <CardTitle>参考标准</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-primary-700">
              <li>• GB/T 9704-2012《党政机关公文格式》</li>
              <li>• 国家行政机关公文处理办法</li>
              <li>• 各级政府机关公文规范要求</li>
            </ul>
          </CardContent>
        </Card>

        {/* 公文字体下载 */}
        <Card className="border-primary-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileType className="h-5 w-5" />
              公文标准字体下载
            </CardTitle>
            <CardDescription>
              GB/T 9704 标准要求的公文字体，下载后双击安装即可
            </CardDescription>
          </CardHeader>
          <CardContent>
            {fonts.length === 0 ? (
              <p className="text-sm text-primary-500">暂无可用字体文件</p>
            ) : (
              <div className="space-y-3">
                {fonts.map((font) => (
                  <div
                    key={font.filename}
                    className="flex items-center justify-between p-4 bg-primary-50 rounded-lg border border-primary-100"
                  >
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3">
                        <FileType className="h-8 w-8 text-accent flex-shrink-0" />
                        <div>
                          <p className="font-medium text-primary-900">{font.display_name}</p>
                          <p className="text-sm text-primary-600">{font.description}</p>
                          <p className="text-xs text-primary-400 mt-1">
                            {font.filename} · {font.size_kb} KB
                          </p>
                        </div>
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownloadFont(font)}
                      className="ml-4 flex-shrink-0"
                    >
                      <Download className="h-4 w-4 mr-1" />
                      下载
                    </Button>
                  </div>
                ))}
                <div className="p-3 bg-status-warning-bg border border-status-warning rounded text-sm text-status-warning">
                  <p className="font-medium mb-1">安装说明：</p>
                  <ol className="list-decimal ml-4 space-y-1">
                    <li>下载字体文件（.ttf）</li>
                    <li>双击字体文件，点击「安装」按钮</li>
                    <li>重启 Word/WPS 后即可使用</li>
                  </ol>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* 免责声明 */}
        <Card className="border-primary-200 bg-status-warning-bg">
          <CardHeader>
            <CardTitle className="text-status-warning">免责声明</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-status-warning space-y-2">
            <p>1. 本软件仅供参考，最终公文格式以实际发文机关要求为准。</p>
            <p>2. 使用本软件前请确保已安装所需字体（方正小标宋简体、仿宋_GB2312等）。</p>
            <p>3. 建议在正式发文前人工复核检查结果。</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
