import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BandaWeb3 - Podcast Web3 en Español",
  description: "Conversaciones sobre Web3, Blockchain y el futuro descentralizado",
  openGraph: {
    title: "BandaWeb3 - Podcast Web3 en Español",
    description: "Conversaciones sobre Web3, Blockchain y el futuro descentralizado",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    site: "@BandaWeb3",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className={inter.className}>
        {/* Navbar */}
        <nav className="bg-black bg-opacity-50 backdrop-blur-md sticky top-0 z-50 border-b border-gray-800">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <Link href="/" className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent">
                BandaWeb3
              </Link>
              <div className="flex gap-6">
                <Link href="/" className="text-gray-300 hover:text-white transition-colors">
                  Episodios
                </Link>
                <a
                  href="https://twitter.com/BandaWeb3"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Twitter
                </a>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        {children}

        {/* Footer */}
        <footer className="bg-black border-t border-gray-800 py-8">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center justify-between">
              <p className="text-gray-400 mb-4 md:mb-0">
                © 2024 BandaWeb3. Todos los derechos reservados.
              </p>
              <div className="flex gap-6">
                <a
                  href="https://twitter.com/BandaWeb3"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Twitter
                </a>
                <Link href="/rss.xml" className="text-gray-400 hover:text-white transition-colors">
                  RSS
                </Link>
              </div>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
