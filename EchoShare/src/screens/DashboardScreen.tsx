import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';

const DashboardScreen: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.user);
  const { totalValue, totalGainLoss, totalGainLossPercent } = useSelector(
    (state: RootState) => state.portfolio
  );

  const aiInsights = [
    'Your portfolio is 15% more diversified than last month',
    'Consider rebalancing: Tech sector overweight by 8%',
    'Based on your risk tolerance, you could increase crypto allocation by 3%',
    'Market sentiment is bullish - good time to review growth stocks',
  ];

  const quickActions = [
    { label: 'Buy Crypto', icon: '₿', color: '#f7931a' },
    { label: 'Invest in ETF', icon: '📈', color: '#00d4ff' },
    { label: 'Copy Trade', icon: '👥', color: '#00ff88' },
    { label: 'Set Alert', icon: '🔔', color: '#ff6b6b' },
  ];

  const handleQuickAction = (action: string) => {
    Alert.alert('Action', `Opening ${action}...`, [{ text: 'OK' }]);
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.welcome}>Welcome back, {user?.name?.split(' ')[0]}!</Text>
        <Text style={styles.subtitle}>Here's your financial overview</Text>
      </View>

      {/* Portfolio Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Portfolio Value</Text>
        <Text style={styles.value}>${totalValue.toLocaleString()}</Text>
        <View style={styles.gainLossContainer}>
          <Text style={[styles.gainLoss, totalGainLoss >= 0 ? styles.positive : styles.negative]}>
            {totalGainLoss >= 0 ? '+' : ''}${totalGainLoss.toFixed(2)} ({totalGainLossPercent.toFixed(2)}%)
          </Text>
          <Text style={styles.period}>Today</Text>
        </View>
      </View>

      {/* AI Insights */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🤖 AI Insights</Text>
        {aiInsights.map((insight, index) => (
          <View key={index} style={styles.insightCard}>
            <Text style={styles.insightText}>{insight}</Text>
          </View>
        ))}
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Quick Actions</Text>
        <View style={styles.quickActionsGrid}>
          {quickActions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.quickActionCard, { backgroundColor: action.color + '20' }]}
              onPress={() => handleQuickAction(action.label)}
            >
              <Text style={styles.quickActionIcon}>{action.icon}</Text>
              <Text style={styles.quickActionLabel}>{action.label}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Market Movers */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Market Movers</Text>
        <View style={styles.moversContainer}>
          <View style={styles.moverItem}>
            <Text style={styles.moverSymbol}>TSLA</Text>
            <Text style={[styles.moverChange, styles.positive]}>+6.5%</Text>
          </View>
          <View style={styles.moverItem}>
            <Text style={styles.moverSymbol}>NVDA</Text>
            <Text style={[styles.moverChange, styles.positive]}>+4.2%</Text>
          </View>
          <View style={styles.moverItem}>
            <Text style={styles.moverSymbol}>AAPL</Text>
            <Text style={[styles.moverChange, styles.negative]}>-1.3%</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  header: {
    padding: 20,
    paddingTop: 10,
  },
  welcome: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#8892b0',
  },
  summaryCard: {
    backgroundColor: '#16213e',
    margin: 20,
    marginTop: 0,
    padding: 24,
    borderRadius: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#00d4ff',
  },
  summaryTitle: {
    fontSize: 14,
    color: '#8892b0',
    marginBottom: 8,
  },
  value: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  gainLossContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  gainLoss: {
    fontSize: 18,
    fontWeight: '600',
    marginRight: 8,
  },
  positive: {
    color: '#00ff88',
  },
  negative: {
    color: '#ff6b6b',
  },
  period: {
    fontSize: 14,
    color: '#8892b0',
  },
  section: {
    margin: 20,
    marginTop: 0,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  insightCard: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  insightText: {
    color: '#ffffff',
    fontSize: 16,
    lineHeight: 22,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickActionCard: {
    width: '48%',
    padding: 20,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
  },
  quickActionIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  quickActionLabel: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  moversContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
  },
  moverItem: {
    alignItems: 'center',
  },
  moverSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  moverChange: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DashboardScreen;