'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ApolloProvider } from '@apollo/client'
import { ThemeProvider } from 'next-themes'
import { SessionProvider } from 'next-auth/react'
import { apolloClient } from '@/lib/apollo-client'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <SessionProvider>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <QueryClientProvider client={queryClient}>
          <ApolloProvider client={apolloClient}>
            {children}
          </ApolloProvider>
        </QueryClientProvider>
      </ThemeProvider>
    </SessionProvider>
  )
}