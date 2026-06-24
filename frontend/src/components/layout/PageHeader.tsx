/**
 * PageHeader - 页面标题栏
 * 响应式：小屏堆叠，大屏横排
 */
import { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
}

export default function PageHeader({ title, description, actions }: PageHeaderProps) {
  return (
    <div className="bg-white border-b border-primary-100 px-4 md:px-6 lg:px-8 py-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl md:text-2xl font-semibold text-primary-900">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-primary-600">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">{actions}</div>}
      </div>
    </div>
  );
}