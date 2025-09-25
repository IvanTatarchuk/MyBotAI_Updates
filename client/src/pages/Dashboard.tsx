import React from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Activity,
  Eye,
  Users,
  BarChart3,
  Zap
} from 'lucide-react';

import { useAuth } from '../hooks/useAuth';
import { useTrading } from '../hooks/useTrading';
import { Card } from '../components/ui/Card';
import { StatCard } from '../components/dashboard/StatCard';
import { PortfolioChart } from '../components/dashboard/PortfolioChart';
import { MarketOverview } from '../components/dashboard/MarketOverview';
import { RecentTrades } from '../components/dashboard/RecentTrades';
import { AIInsights } from '../components/dashboard/AIInsights';
import { QuickActions } from '../components/dashboard/QuickActions';
import { NewsFeed } from '../components/dashboard/NewsFeed';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const { portfolio, marketData, isLoading } = useTrading();

  const stats = [
    {
      title: 'Total Portfolio Value',
      value: portfolio?.totalValue || 0,
      change: portfolio?.change24h || 0,
      changeType: portfolio?.change24h >= 0 ? 'positive' : 'negative',
      icon: DollarSign,
      color: 'blue',
    },
    {
      title: '24h P&L',
      value: portfolio?.pnl24h || 0,
      change: portfolio?.pnlPercentage || 0,
      changeType: portfolio?.pnl24h >= 0 ? 'positive' : 'negative',
      icon: TrendingUp,
      color: portfolio?.pnl24h >= 0 ? 'green' : 'red',
    },
    {
      title: 'Active Positions',
      value: portfolio?.activePositions || 0,
      change: portfolio?.newPositions || 0,
      changeType: 'neutral',
      icon: Activity,
      color: 'purple',
    },
    {
      title: 'Win Rate',
      value: portfolio?.winRate || 0,
      change: 0,
      changeType: 'neutral',
      icon: BarChart3,
      color: 'orange',
      suffix: '%',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
      },
    },
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 h-96 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />
          <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <motion.div
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* Welcome Header */}
      <motion.div variants={itemVariants}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Welcome back, {user?.firstName}! 👋
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Here's what's happening with your portfolio today.
            </p>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <Eye className="w-4 h-4" />
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <StatCard
              key={index}
              title={stat.title}
              value={stat.value}
              change={stat.change}
              changeType={stat.changeType}
              icon={stat.icon}
              color={stat.color as any}
              suffix={stat.suffix}
            />
          ))}
        </div>
      </motion.div>

      {/* Main Content Grid */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Portfolio Chart */}
          <div className="lg:col-span-2">
            <Card className="h-96">
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Portfolio Performance
                  </h2>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-primary-500 rounded-full"></div>
                    <span className="text-sm text-gray-600 dark:text-gray-400">Portfolio Value</span>
                  </div>
                </div>
                <PortfolioChart />
              </div>
            </Card>
          </div>

          {/* Market Overview */}
          <div>
            <Card className="h-96">
              <div className="p-6">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
                  Market Overview
                </h2>
                <MarketOverview />
              </div>
            </Card>
          </div>
        </div>
      </motion.div>

      {/* Secondary Content Grid */}
      <motion.div variants={itemVariants}>
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {/* Recent Trades */}
          <div className="xl:col-span-1">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Recent Trades
                  </h2>
                  <Activity className="w-5 h-5 text-gray-400" />
                </div>
                <RecentTrades />
              </div>
            </Card>
          </div>

          {/* AI Insights */}
          <div className="xl:col-span-1">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    AI Insights
                  </h2>
                  <Zap className="w-5 h-5 text-primary-500" />
                </div>
                <AIInsights />
              </div>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="xl:col-span-1">
            <Card>
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                    Quick Actions
                  </h2>
                </div>
                <QuickActions />
              </div>
            </Card>
          </div>
        </div>
      </motion.div>

      {/* News Feed */}
      <motion.div variants={itemVariants}>
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">
              Market News
            </h2>
            <NewsFeed />
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;