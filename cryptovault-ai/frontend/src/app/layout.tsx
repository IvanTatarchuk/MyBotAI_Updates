import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/toaster'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CryptoVault AI - Advanced Cryptocurrency Portfolio Management',
  description: 'Enterprise-grade cryptocurrency portfolio management with AI-powered analytics and predictions',
  keywords: 'cryptocurrency, portfolio, management, AI, trading, analytics',
  authors: [{ name: 'CryptoVault AI Team' }],
  openGraph: {
    title: 'CryptoVault AI',
    description: 'Advanced Cryptocurrency Portfolio Management Platform',
    type: 'website',
    locale: 'en_US',
    url: 'https://cryptovault.ai',
    siteName: 'CryptoVault AI',
    images: [
      {
        url: 'https://cryptovault.ai/og-image.png',
        width: 1200,
        height: 630,
        alt: 'CryptoVault AI',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CryptoVault AI',
    description: 'Advanced Cryptocurrency Portfolio Management Platform',
    images: ['https://cryptovault.ai/twitter-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}