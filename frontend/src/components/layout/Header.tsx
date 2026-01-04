import { Box } from 'lucide-react';

export function Header() {
  return (
    <header className="glass border-b border-white/10">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Box className="w-8 h-8 text-primary-400" />
            <h1 className="text-2xl font-bold gradient-text">
              TRELLIS 3D Generator
            </h1>
          </div>
          <nav className="flex items-center gap-4">
            <a
              href="https://github.com/microsoft/TRELLIS"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-400 hover:text-white transition-colors"
            >
              GitHub
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}
