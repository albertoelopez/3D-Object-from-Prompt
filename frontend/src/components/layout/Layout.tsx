import { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>
      <footer className="py-4 text-center text-sm text-gray-500">
        <p>Powered by Microsoft TRELLIS • Built with Ollama & Groq</p>
      </footer>
    </div>
  );
}
