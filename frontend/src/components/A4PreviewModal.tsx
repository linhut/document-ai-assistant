/**
 * A4PreviewModal - A4 预览弹窗
 * 在校审中心内以弹窗形式展示 A4 排版预览
 * 随文档优化状态动态刷新
 */
import { useState, useEffect } from 'react';
import { X, ZoomIn, ZoomOut, RefreshCw, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { apiClient, downloadFile } from '@/api/client';

interface DocParagraph {
  text: string;
  role?: string;
  is_heading: boolean;
  heading_level?: number;
  format: {
    alignment?: string;
    first_line_indent_pt?: number;
    font_name?: string;
    font_size_pt?: number;
    line_spacing_pt?: number;
  };
}

interface A4PreviewModalProps {
  docId: number;
  refreshKey?: number;    // 每次优化后 +1 触发刷新
  onClose: () => void;
}

const FONT_MAP: Record<string, string> = {
  '方正小标宋简体': '"方正小标宋简体", "FZXiaoBiaoSong-B05S", serif',
  '方正小标宋_GBK': '"方正小标宋简体", "FZXiaoBiaoSong-B05S", serif',
  '黑体': '"黑体", "SimHei", sans-serif',
  '楷体_GB2312': '"楷体_GB2312", "KaiTi", serif',
  '楷体': '"楷体", "KaiTi", serif',
  '仿宋_GB2312': '"仿宋_GB2312", "FangSong", serif',
  '仿宋': '"仿宋", "FangSong", serif',
  '宋体': '"宋体", "SimSun", serif',
};

function getFontFamily(name?: string): string {
  if (!name) return '"仿宋_GB2312", "FangSong", serif';
  return FONT_MAP[name] || `"${name}", serif`;
}

export default function A4PreviewModal({ docId, refreshKey, onClose }: A4PreviewModalProps) {
  const [paragraphs, setParagraphs] = useState<DocParagraph[]>([]);
  const [pageSetup, setPageSetup] = useState({ margin_top_mm: 37, margin_bottom_mm: 35, margin_left_mm: 28, margin_right_mm: 26 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(80);

  useEffect(() => {
    loadData();
  }, [docId, refreshKey]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const resp = await apiClient.get(`/api/documents/${docId}/preview`);
      setParagraphs(resp.paragraphs || []);
      setPageSetup(resp.page_setup || pageSetup);
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.message || '预览加载失败';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  /* 按 role 分离结构 */
  const title = paragraphs.find(p => p.role === 'title' || (p.is_heading && p.heading_level === 0));
  const recipient = paragraphs.find(p => p.role === 'recipient');
  const body = paragraphs.filter(p =>
    p.role === 'body' || p.role === 'attachment' ||
    (p.is_heading && p.heading_level && p.heading_level >= 1 && p.role !== 'title')
  );
  const signature = paragraphs.find(p => p.role === 'signature');
  const date = paragraphs.find(p => p.role === 'date');

  /* 渲染单个段落 */
  const renderP = (p: DocParagraph, key: number) => {
    const fs = p.format.font_size_pt || 16;
    const ff = getFontFamily(p.format.font_name);
    const lh = p.format.line_spacing_pt ? `${p.format.line_spacing_pt}pt` : '29pt';
    const indent = p.format.first_line_indent_pt ? `${p.format.first_line_indent_pt}pt` : undefined;
    let align: string = p.format.alignment || 'left';
    if (align === 'justify') align = 'justify';

    const style: React.CSSProperties = {
      fontSize: `${fs}pt`, fontFamily: ff, lineHeight: lh,
      textAlign: align as any, textIndent: indent,
      margin: 0, padding: 0,
    };

    // 标题级别覆盖
    if (p.is_heading && p.heading_level === 0) {
      Object.assign(style, { fontSize: '22pt', fontFamily: '"方正小标宋简体", serif', textAlign: 'center', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 1) {
      Object.assign(style, { fontFamily: '"黑体", "SimHei", sans-serif', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 2) {
      Object.assign(style, { fontFamily: '"楷体_GB2312", "KaiTi", serif', textIndent: '0' });
    } else if (p.is_heading && p.heading_level === 3) {
      Object.assign(style, { fontFamily: '"仿宋_GB2312", "FangSong", serif', fontWeight: 'bold' });
    }

    return <p key={key} style={style}>{p.text || ' '}</p>;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div
        className="bg-white rounded-xl shadow-2xl flex flex-col max-h-[95vh] overflow-hidden"
        style={{ width: '90vw', maxWidth: '900px' }}
        onClick={e => e.stopPropagation()}
      >
        {/* 标题栏 */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-primary-100 bg-primary-50">
          <div className="flex items-center gap-2">
            <span className="font-medium text-primary-900">A4 预览</span>
            <span className="text-xs text-primary-500">GB/T 9704 标准排版</span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={() => loadData()} title="刷新">
              <RefreshCw className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-xs text-muted-foreground w-10 text-center">{zoom}%</span>
            <Button variant="ghost" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => downloadFile(`/api/optimize/${docId}/download`, `optimized_${docId}.docx`)} title="下载">
              <Download className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* A4 内容区 */}
        <div className="flex-1 overflow-auto bg-gray-200 p-6">
          {loading ? (
            <div className="text-center py-20 text-muted-foreground">加载中...</div>
          ) : error ? (
            <div className="text-center py-20">
              <p className="text-red-500 mb-3">{error}</p>
              <Button variant="outline" size="sm" onClick={() => loadData()}>重试</Button>
            </div>
          ) : paragraphs.length === 0 ? (
            <div className="text-center py-20 text-muted-foreground">
              <p>暂无预览内容</p>
              <p className="text-xs mt-1">请先上传并优化文档</p>
            </div>
          ) : (
            <div
              style={{
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top center',
              }}
            >
              <div style={{
                width: '210mm',
                minHeight: '297mm',
                padding: `${pageSetup.margin_top_mm}mm ${pageSetup.margin_right_mm}mm ${pageSetup.margin_bottom_mm}mm ${pageSetup.margin_left_mm}mm`,
                background: 'white',
                boxShadow: '0 2px 16px rgba(0,0,0,0.2)',
                margin: '0 auto',
                position: 'relative',
                fontFamily: '"仿宋_GB2312", "FangSong", serif',
                fontSize: '16pt',
                lineHeight: '29pt',
                color: '#000',
              }}>
                {title && renderP(title, -1)}
                {recipient && renderP(recipient, -2)}
                {body.map((p, i) => renderP(p, i))}

                {(signature || date) && (
                  <div style={{ marginTop: '3em' }}>
                    {signature && renderP({ ...signature, format: { ...signature.format, alignment: 'right' } }, -3)}
                    {date && renderP({ ...date, format: { ...date.format, alignment: 'right' } }, -4)}
                  </div>
                )}

                {/* 页码 */}
                <div style={{
                  position: 'absolute',
                  bottom: `${pageSetup.margin_bottom_mm - 8}mm`,
                  left: 0, right: 0,
                  textAlign: 'center',
                  fontSize: '10pt',
                  fontFamily: '"Times New Roman", serif',
                  color: '#000',
                }}>
                  — 1 —
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
