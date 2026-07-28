'use client'

import { Button } from '@/components/ui/button'
import { ArrowRight, BarChart3, Bot, Lock, TrendingUp, Zap, Globe, Shield } from 'lucide-react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

export default function HomePage() {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-secondary/20">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 glass-effect">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bot className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold gradient-text">CryptoVault AI</span>
          </div>
          <div className="flex items-center space-x-6">
            <Link href="/features" className="text-muted-foreground hover:text-foreground transition">
              Features
            </Link>
            <Link href="/pricing" className="text-muted-foreground hover:text-foreground transition">
              Pricing
            </Link>
            <Link href="/docs" className="text-muted-foreground hover:text-foreground transition">
              Docs
            </Link>
            <Button variant="ghost" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6">
              Cryptocurrency Portfolio
              <br />
              <span className="gradient-text">Management Reimagined</span>
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto">
              Harness the power of AI to manage, analyze, and grow your cryptocurrency portfolio.
              Built for serious investors and institutions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" className="text-lg px-8" asChild>
                <Link href="/register">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8" asChild>
                <Link href="/demo">Watch Demo</Link>
              </Button>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-20"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <div className="text-center">
              <h3 className="text-4xl font-bold text-primary">$2.5B+</h3>
              <p className="text-muted-foreground">Assets Under Management</p>
            </div>
            <div className="text-center">
              <h3 className="text-4xl font-bold text-primary">50K+</h3>
              <p className="text-muted-foreground">Active Users</p>
            </div>
            <div className="text-center">
              <h3 className="text-4xl font-bold text-primary">99.9%</h3>
              <p className="text-muted-foreground">Uptime SLA</p>
            </div>
            <div className="text-center">
              <h3 className="text-4xl font-bold text-primary">50+</h3>
              <p className="text-muted-foreground">Exchange Integrations</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-secondary/10">
        <div className="container mx-auto">
          <motion.div 
            className="text-center mb-16"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl font-bold mb-4">Enterprise-Grade Features</h2>
            <p className="text-xl text-muted-foreground">Everything you need to manage crypto at scale</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              viewport={{ once: true }}
            >
              <Bot className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">AI Price Predictions</h3>
              <p className="text-muted-foreground">
                Advanced machine learning models analyze market trends to predict price movements with high accuracy.
              </p>
            </motion.div>

            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              viewport={{ once: true }}
            >
              <BarChart3 className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">Portfolio Analytics</h3>
              <p className="text-muted-foreground">
                Real-time portfolio performance tracking with advanced risk metrics and optimization suggestions.
              </p>
            </motion.div>

            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              viewport={{ once: true }}
            >
              <Zap className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">Automated Trading</h3>
              <p className="text-muted-foreground">
                Set up sophisticated trading strategies with our AI-powered automation and backtesting tools.
              </p>
            </motion.div>

            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              viewport={{ once: true }}
            >
              <Globe className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">Multi-Exchange Support</h3>
              <p className="text-muted-foreground">
                Connect and manage accounts across 50+ major cryptocurrency exchanges from one dashboard.
              </p>
            </motion.div>

            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              viewport={{ once: true }}
            >
              <Shield className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">Bank-Grade Security</h3>
              <p className="text-muted-foreground">
                Military-grade encryption, multi-sig wallets, and comprehensive security audits protect your assets.
              </p>
            </motion.div>

            <motion.div
              className="card-hover p-6 rounded-lg border bg-card"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
              viewport={{ once: true }}
            >
              <TrendingUp className="h-12 w-12 text-primary mb-4" />
              <h3 className="text-2xl font-semibold mb-2">Tax Optimization</h3>
              <p className="text-muted-foreground">
                Automated tax reporting and optimization strategies to minimize your cryptocurrency tax burden.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center">
          <motion.div
            className="gradient-border inline-block"
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
          >
            <div className="bg-background p-12 rounded-lg">
              <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Crypto Portfolio?</h2>
              <p className="text-xl text-muted-foreground mb-8">
                Join thousands of investors using AI to maximize their returns
              </p>
              <Button size="lg" className="text-lg px-8" asChild>
                <Link href="/register">
                  Start Your Free Trial
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <p className="mt-4 text-sm text-muted-foreground">
                No credit card required · 14-day free trial · Cancel anytime
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Bot className="h-6 w-6 text-primary" />
                <span className="text-xl font-bold">CryptoVault AI</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Enterprise cryptocurrency portfolio management platform.
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/features" className="hover:text-foreground">Features</Link></li>
                <li><Link href="/pricing" className="hover:text-foreground">Pricing</Link></li>
                <li><Link href="/security" className="hover:text-foreground">Security</Link></li>
                <li><Link href="/roadmap" className="hover:text-foreground">Roadmap</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/about" className="hover:text-foreground">About</Link></li>
                <li><Link href="/blog" className="hover:text-foreground">Blog</Link></li>
                <li><Link href="/careers" className="hover:text-foreground">Careers</Link></li>
                <li><Link href="/contact" className="hover:text-foreground">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link href="/privacy" className="hover:text-foreground">Privacy Policy</Link></li>
                <li><Link href="/terms" className="hover:text-foreground">Terms of Service</Link></li>
                <li><Link href="/compliance" className="hover:text-foreground">Compliance</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
            <p>&copy; 2024 CryptoVault AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}