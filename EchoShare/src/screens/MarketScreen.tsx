import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  TextInput,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { MarketData } from '../store/slices/marketSlice';

const MarketScreen: React.FC = () => {
  const { indices, crypto, trending, watchlist } = useSelector((state: RootState) => state.market);
  const [selectedTab, setSelectedTab] = useState<'indices' | 'crypto' | 'trending' | 'watchlist'>('indices');
  const [searchText, setSearchText] = useState('');

  const renderMarketItem = ({ item }: { item: MarketData }) => (
    <TouchableOpacity style={styles.marketItem} onPress={() => handleMarketItemPress(item)}>
      <View style={styles.marketItemHeader}>
        <Text style={styles.marketSymbol}>{item.symbol}</Text>
        <Text style={[styles.marketChange, item.change >= 0 ? styles.positive : styles.negative]}>
          {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)} ({item.changePercent.toFixed(2)}%)
        </Text>
      </View>
      <View style={styles.marketItemDetails}>
        <Text style={styles.marketPrice}>${item.price.toLocaleString()}</Text>
        <Text style={styles.marketVolume}>Vol: ${(item.volume / 1000000000).toFixed(1)}B</Text>
      </View>
      <Text style={styles.marketTime}>Last updated: {new Date(item.lastUpdated).toLocaleTimeString()}</Text>
    </TouchableOpacity>
  );

  const handleMarketItemPress = (item: MarketData) => {
    // This would open detailed market data view
    console.log('Market item pressed:', item.symbol);
  };

  const handleAddToWatchlist = (symbol: string) => {
    // This would add symbol to watchlist
    console.log('Add to watchlist:', symbol);
  };

  const tabs = [
    { label: 'Indices', value: 'indices' },
    { label: 'Crypto', value: 'crypto' },
    { label: 'Trending', value: 'trending' },
    { label: 'Watchlist', value: 'watchlist' },
  ];

  const getCurrentData = () => {
    switch (selectedTab) {
      case 'indices':
        return indices;
      case 'crypto':
        return crypto;
      case 'trending':
        return trending;
      case 'watchlist':
        // In a real app, this would filter from all market data
        return indices.slice(0, 3);
      default:
        return indices;
    }
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Market Data</Text>
        <Text style={styles.headerSubtitle}>Real-time market information</Text>

        {/* Search Bar */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search symbols..."
            placeholderTextColor="#8892b0"
            value={searchText}
            onChangeText={setSearchText}
          />
        </View>
      </View>

      {/* Tabs */}
      <View style={styles.tabSection}>
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.value}
            style={[
              styles.tabButton,
              selectedTab === tab.value && styles.tabButtonActive,
            ]}
            onPress={() => setSelectedTab(tab.value as any)}
          >
            <Text
              style={[
                styles.tabButtonText,
                selectedTab === tab.value && styles.tabButtonTextActive,
              ]}
            >
              {tab.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Market Data */}
      <View style={styles.marketSection}>
        <FlatList
          data={getCurrentData()}
          renderItem={renderMarketItem}
          keyExtractor={(item) => item.symbol}
          showsVerticalScrollIndicator={false}
        />
      </View>

      {/* Market Summary */}
      <View style={styles.summarySection}>
        <Text style={styles.sectionTitle}>Market Summary</Text>
        <View style={styles.summaryGrid}>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Market Cap</Text>
            <Text style={styles.summaryValue}>$45.2T</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>24h Volume</Text>
            <Text style={styles.summaryValue}>$2.1T</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>BTC Dominance</Text>
            <Text style={styles.summaryValue}>52.3%</Text>
          </View>
          <View style={styles.summaryItem}>
            <Text style={styles.summaryLabel}>Active Symbols</Text>
            <Text style={styles.summaryValue}>12,450</Text>
          </View>
        </View>
      </View>

      {/* Quick Stats */}
      <View style={styles.statsSection}>
        <Text style={styles.sectionTitle}>📊 Quick Stats</Text>
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>+127</Text>
            <Text style={styles.statLabel}>Gainers</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={[styles.statNumber, styles.negative]}>-89</Text>
            <Text style={styles.statLabel}>Losers</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statNumber}>$1.2T</Text>
            <Text style={styles.statLabel}>Crypto Market Cap</Text>
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
  headerTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#8892b0',
    marginBottom: 16,
  },
  searchContainer: {
    backgroundColor: '#16213e',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  searchInput: {
    color: '#ffffff',
    fontSize: 16,
    padding: 0,
  },
  tabSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  tabButton: {
    backgroundColor: '#16213e',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 12,
  },
  tabButtonActive: {
    backgroundColor: '#00d4ff',
  },
  tabButtonText: {
    color: '#8892b0',
    fontSize: 14,
    fontWeight: '600',
  },
  tabButtonTextActive: {
    color: '#ffffff',
  },
  marketSection: {
    paddingHorizontal: 20,
  },
  marketItem: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  marketItemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  marketSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  marketChange: {
    fontSize: 14,
    fontWeight: '600',
  },
  positive: {
    color: '#00ff88',
  },
  negative: {
    color: '#ff6b6b',
  },
  marketItemDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  marketPrice: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  marketVolume: {
    fontSize: 14,
    color: '#8892b0',
  },
  marketTime: {
    fontSize: 12,
    color: '#8892b0',
  },
  summarySection: {
    padding: 20,
    paddingTop: 0,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  summaryGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  summaryItem: {
    backgroundColor: '#16213e',
    width: '48%',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#8892b0',
    marginBottom: 8,
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  statsSection: {
    padding: 20,
    paddingTop: 0,
    paddingBottom: 40,
  },
  statsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statCard: {
    backgroundColor: '#16213e',
    flex: 1,
    marginHorizontal: 4,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#8892b0',
    textAlign: 'center',
  },
});

export default MarketScreen;