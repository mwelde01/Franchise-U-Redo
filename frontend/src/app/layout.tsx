import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Podcast Manager',
  description: 'AI-powered podcast storage and summarization',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <a href="/" className="flex items-center space-x-2">
                <svg className="w-8 h-8 text-primary-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                </svg>
                <span className="text-xl font-bold text-gray-900">Podcast Manager</span>
              </a>

              <div className="flex items-center space-x-6">
                <a href="/" className="text-gray-700 hover:text-primary-600 transition">
                  Episodes
                </a>
                <a href="/search" className="text-gray-700 hover:text-primary-600 transition">
                  Search
                </a>
                <a href="/upload" className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition">
                  Upload
                </a>
              </div>
            </div>
          </div>
        </nav>

        <main className="min-h-screen bg-gray-50">
          {children}
        </main>

        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="container mx-auto px-4 py-6 text-center text-gray-600 text-sm">
            <p>Podcast Storage & Summarization System</p>
            <p className="mt-1">Powered by Claude API</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
