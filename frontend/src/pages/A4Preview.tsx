/**
 * A4Preview - A4 分页预览页面
 * 从优化后的文档渲染实时 A4 预览
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Loader2, FileText, Download, ZoomIn, ZoomOut } from 'lucide-react';
import PageHeader from '@/components/layout/PageHeader';
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

interface DocData {
  paragraphs: DocParagraph[];
  page_setup: {
    margin_top_mm: number;
    margin_bottom_mm: number;
    margin_left_mm: number;
    margin_right_mm: number;
  };
}

/* GB/T 9704 字号映射 */
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

function getFontFamily(fontName?: string): string {
  if (!fontName) return '"仿宋_GB2312", "FangSong", serif';
  return FONT_MAP[fontName] || `"${fontName}", serif`;
}

export default function A4Preview() {
  const [searchParams] = useSearchParams();
  const docId = searchParams.get('docId');
  const [docData, setDocData] = useState<DocData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [zoom, setZoom] = useState(100);

  useEffect(() => {
    if (docId) loadDocument(parseInt(docId));
  }, [docId]);

  const loadDocument = async (id: number) => {
    try {
      setLoading(true);
      const resp = await apiClient.get(`/api/documents/${id}/preview`);
      setDocData(resp);
    } catch {
      setError('无法加载文档预览');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-primary-50">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (error || !docData) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-primary-50">
        <div className="text-center">
          <FileText className="h-12 w-12 text-primary-300 mx-auto mb-3" />
          <p className="text-muted-foreground">{error || '无文档数据'}</p>
        </div>
      </div>
    );
  }

  const { paragraphs, page_setup } = docData;

  if (paragraphs.length === 0) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-primary-50">
        <div className="text-center">
          <FileText className="h-12 w-12 text-primary-300 mx-auto mb-3" />
          <p className="text-muted-foreground">文档无段落内容</p>
          <p className="text-xs text-muted-foreground mt-1">请确认文档已正确上传并优化</p>
        </div>
      </div>
    );
  }

  /* 分离结构元素 */
  const titlePara = paragraphs.find(p => p.role === 'title' || (p.is_heading && p.heading_level === 0));
  const recipientPara = paragraphs.find(p => p.role === 'recipient');
  const bodyParas = paragraphs.filter(p =>
    p.role === 'body' || p.role === 'attachment' ||
    (p.is_heading && p.heading_level && p.heading_level >= 1)
  );
  const signaturePara = paragraphs.find(p => p.role === 'signature');
  const datePara = paragraphs.find(p => p.role === 'date');

  /* A4 页面样式 */
  const pageStyle: React.CSSProperties = {
    width: '210mm',
    minHeight: '297mm',
    padding: `${page_setup.margin_top_mm}mm ${page_setup.margin_right_mm}mm ${page_setup.margin_bottom_mm}mm ${page_setup.margin_left_mm}mm`,
    background: 'white',
    boxShadow: '0 2px 12px rgba(0,0,0,0.15)',
    margin: '0 auto 20px',
    position: 'relative',
    overflow: 'hidden',
  };

  const renderParagraph = (p: DocParagraph, idx: number) => {
    const fontSize = p.format.font_size_pt || 16;
    const fontFamily = getFontFamily(p.format.font_name);
    const lineHeight = p.format.line_spacing_pt ? `${p.format.line_spacing_pt}pt` : '29pt';
    const indent = p.format.first_line_indent_pt ? `${p.format.first_line_indent_pt}pt` : undefined;
    const align = p.format.alignment === 'justify' ? 'justify' : p.format.alignment === 'center' ? 'center' : p.format.alignment === 'right' ? 'right' : 'left';

    const style: React.CSSProperties = {
      fontSize: `${fontSize}pt`,
      fontFamily,
      lineHeight,
      textAlign: align as any,
      textIndent: indent,
      marginBottom: '0',
      marginTop: '0',
    };

    if (p.is_heading && p.heading_level === 0) {
      style.fontSize = '22pt';
      style.fontFamily = '"方正小标宋简体", serif';
      style.textAlign = 'center';
      style.textIndent = '0';
    } else if (p.is_heading && p.heading_level === 1) {
      style.fontFamily = '"黑体", "SimHei", sans-serif';
      style.textIndent = '0';
    } else if (p.is_heading && p.heading_level === 2) {
      style.fontFamily = '"楷体_GB2312", "KaiTi", serif';
      style.textIndent = '0';
    }

    return <p key={idx} style={style}>{p.text || ' '}</p>;
  };

  return (
    <div className="w-full bg-primary-50 min-h-screen">
      <PageHeader
        title="A4 预览"
        description="GB/T 9704 标准排版预览"
        actions={
          <div className="flex gap-2 items-center">
            <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.max(50, z - 10))}>
              <ZoomOut className="h-4 w-4" />
            </Button>
            <span className="text-sm text-muted-foreground w-12 text-center">{zoom}%</span>
            <Button variant="outline" size="sm" onClick={() => setZoom(z => Math.min(150, z + 10))}>
              <ZoomIn className="h-4 w-4" />
            </Button>
            {docId && (
              <Button variant="outline" size="sm" onClick={() => downloadFile(`/api/optimize/${docId}/download`, `preview_${docId}.docx`)}>
                <Download className="h-4 w-4 mr-1" />下载
              </Button>
            )}
          </div>
        }
      />

      <div className="p-8" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }}>
        <div style={pageStyle}>
          {/* 正文内容 */}
          <div>
            {titlePara && renderParagraph(titlePara, -1)}
            {recipientPara && renderParagraph(recipientPara, -2)}
            {bodyParas.map((p, i) => renderParagraph(p, i))}

            {/* 落款区 */}
            {(signaturePara || datePara) && (
              <div style={{ marginTop: '2em' }}>
                {signaturePara && (
                  <p style={{
                    fontSize: '16pt',
                    fontFamily: '"仿宋_GB2312", serif',
                    textAlign: 'right',
                    lineHeight: '29pt',
                  }}>
                    {signaturePara.text}
                  </p>
                )}
                {datePara && (
                  <p style={{
                    fontSize: '16pt',
                    fontFamily: '"仿宋_GB2312", serif',
                    textAlign: 'right',
                    lineHeight: '29pt',
                  }}>
                    {datePara.text}
                  </p>
                )}
              </div>
            )}
          </div>

          {/* 页码 */}
          <div style={{
            position: 'absolute',
            bottom: `${page_setup.margin_bottom_mm - 10}mm`,
            left: 0,
            right: 0,
            textAlign: 'center',
            fontSize: '10pt',
            fontFamily: '"Times New Roman", serif',
          }}>
            — 1 —
          </div>
        </div>
      </div>
    </div>
  );
}
