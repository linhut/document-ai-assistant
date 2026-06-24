/**
 * downloadTemplate handler — 使用统一的 downloadFile 辅助函数。
 * 此文件保留兼容性，推荐直接在页面中使用 downloadFile()。
 */
import { downloadFile } from '@/api/client';

interface TemplateInfo {
  id: string;
  name: string;
}

export function handleDownloadTemplate(template: TemplateInfo): void {
  downloadFile(`/api/template/download/${template.id}`, `${template.name}模板.docx`);
}
