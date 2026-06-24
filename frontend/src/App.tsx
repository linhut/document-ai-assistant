import { HashRouter, Routes, Route } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import ErrorBoundary from './components/ui/error-boundary';
import Workspace from './pages/Workspace';
import DocumentProcess from './pages/DocumentProcess';
import CheckCenter from './pages/CheckCenter';
import Templates from './pages/Templates';
import TemplateRules from './pages/TemplateRules';
import Rules from './pages/Rules';
import AISettings from './pages/AISettings';
import About from './pages/About';

export default function App() {
  return (
    <HashRouter>
      <AppLayout>
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Workspace />} />
            <Route path="/workspace" element={<Workspace />} />
            <Route path="/document/process" element={<DocumentProcess />} />
            <Route path="/document/check" element={<CheckCenter />} />
            <Route path="/templates" element={<Templates />} />
            <Route path="/templates/:templateId/rules" element={<TemplateRules />} />
            <Route path="/rules" element={<Rules />} />
            <Route path="/settings/ai" element={<AISettings />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </ErrorBoundary>
      </AppLayout>
    </HashRouter>
  );
}
