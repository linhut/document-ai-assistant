/**
 * Toast 通知系统
 * 替代原生 alert()/confirm()，提供非阻塞式反馈
 */
import { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { X, CheckCircle2, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { cn } from '@/lib/utils';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextValue {
  toast: (opts: Omit<Toast, 'id'>) => void;
  success: (title: string, message?: string) => void;
  error: (title: string, message?: string) => void;
  warning: (title: string, message?: string) => void;
  info: (title: string, message?: string) => void;
  confirm: (title: string, message: string) => Promise<boolean>;
}

const ToastContext = createContext<ToastContextValue | null>(null);

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}

const ICONS: Record<ToastType, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
};

const COLORS: Record<ToastType, { bg: string; border: string; icon: string }> = {
  success: { bg: 'bg-status-success-bg', border: 'border-status-success/30', icon: 'text-status-success' },
  error: { bg: 'bg-status-error-bg', border: 'border-status-error/30', icon: 'text-status-error' },
  warning: { bg: 'bg-status-warning-bg', border: 'border-status-warning/30', icon: 'text-status-warning' },
  info: { bg: 'bg-status-info-bg', border: 'border-status-info/30', icon: 'text-status-info' },
};

function ToastItem({ toast: t, onDismiss }: { toast: Toast; onDismiss: (id: string) => void }) {
  const [exiting, setExiting] = useState(false);
  const Icon = ICONS[t.type];
  const colors = COLORS[t.type];

  useEffect(() => {
    const dur = t.duration ?? 4000;
    const timer = setTimeout(() => setExiting(true), dur - 200);
    const remove = setTimeout(() => onDismiss(t.id), dur);
    return () => { clearTimeout(timer); clearTimeout(remove); };
  }, [t.id, t.duration, onDismiss]);

  return (
    <div className={cn(
      'flex items-start gap-3 p-4 rounded-lg border shadow-lg min-w-[320px] max-w-[420px]',
      colors.bg, colors.border,
      exiting ? 'toast-exit' : 'toast-enter',
    )}>
      <Icon className={cn('h-5 w-5 flex-shrink-0 mt-0.5', colors.icon)} />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-foreground">{t.title}</p>
        {t.message && <p className="text-xs text-muted-foreground mt-1">{t.message}</p>}
      </div>
      <button onClick={() => onDismiss(t.id)} className="p-0.5 hover:bg-black/5 rounded">
        <X className="h-4 w-4 text-muted-foreground" />
      </button>
    </div>
  );
}

/* 确认对话框 */
interface ConfirmState {
  title: string;
  message: string;
  resolve: (value: boolean) => void;
}

function ConfirmDialog({ state, onClose }: { state: ConfirmState; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50" onClick={() => { state.resolve(false); onClose(); }}>
      <div className="bg-card rounded-xl shadow-2xl border border-border p-6 max-w-md w-full mx-4" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-semibold text-foreground">{state.title}</h3>
        <p className="text-sm text-muted-foreground mt-2">{state.message}</p>
        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={() => { state.resolve(false); onClose(); }}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-primary-50 transition-colors"
          >
            取消
          </button>
          <button
            onClick={() => { state.resolve(true); onClose(); }}
            className="px-4 py-2 text-sm rounded-lg bg-accent text-white hover:bg-accent-hover transition-colors"
          >
            确认
          </button>
        </div>
      </div>
    </div>
  );
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const [confirmState, setConfirmState] = useState<ConfirmState | null>(null);

  const dismiss = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  const toast = useCallback((opts: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).slice(2, 9);
    setToasts(prev => [...prev, { ...opts, id }]);
  }, []);

  const api: ToastContextValue = {
    toast,
    success: (title, message) => toast({ type: 'success', title, message }),
    error: (title, message) => toast({ type: 'error', title, message }),
    warning: (title, message) => toast({ type: 'warning', title, message }),
    info: (title, message) => toast({ type: 'info', title, message }),
    confirm: (title, message) => new Promise<boolean>(resolve => {
      setConfirmState({ title, message, resolve });
    }),
  };

  return (
    <ToastContext.Provider value={api}>
      {children}
      {/* Toast 容器 */}
      <div className="fixed top-4 right-4 z-[90] flex flex-col gap-2">
        {toasts.map(t => <ToastItem key={t.id} toast={t} onDismiss={dismiss} />)}
      </div>
      {/* 确认对话框 */}
      {confirmState && <ConfirmDialog state={confirmState} onClose={() => setConfirmState(null)} />}
    </ToastContext.Provider>
  );
}
