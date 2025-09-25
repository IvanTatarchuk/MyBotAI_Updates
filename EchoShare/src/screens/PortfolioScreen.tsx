import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { PortfolioItem } from '../store/slices/portfolioSlice';

const PortfolioScreen: React.FC = () => {
  const { items, totalValue } = useSelector((state: RootState) => state.portfolio);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'stock' | 'crypto' | 'etf'>('all');

  const filteredItems = items.filter(item =>
    selectedFilter === 'all' || item.type === selectedFilter
  );

  const getTotalByType = (type: string) => {
    return items
      .filter(item => item.type === type)
      .reduce((sum, item) => sum + item.value, 0);
  };

  const renderPortfolioItem = ({ item }: { item: PortfolioItem }) => (
    <TouchableOpacity style={styles.portfolioItem} onPress={() => handleItemPress(item)}>
      <View style={styles.itemHeader}>
        <View>
          <Text style={styles.symbol}>{item.symbol}</Text>
          <Text style={styles.name}>{item.name}</Text>
        </View>
        <View style={styles.itemRight}>
          <Text style={styles.quantity}>{item.quantity} shares</Text>
          <Text style={styles.typeLabel}>{item.type.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.itemDetails}>
        <View style={styles.priceInfo}>
          <Text style={styles.currentPrice}>${item.currentPrice.toFixed(2)}</Text>
          <Text style={[styles.change, item.change >= 0 ? styles.positive : styles.negative]}>
            {item.change >= 0 ? '+' : ''}${item.change.toFixed(2)} ({item.changePercent.toFixed(2)}%)
          </Text>
        </View>
        <Text style={styles.value}>${item.value.toLocaleString()}</Text>
      </View>
    </TouchableOpacity>
  );

  const handleItemPress = (item: PortfolioItem) => {
    Alert.alert(
      item.symbol,
      `${item.name}\n\nCurrent Price: $${item.currentPrice}\nQuantity: ${item.quantity}\nTotal Value: $${item.value.toLocaleString()}\nAvg Cost: $${item.averagePrice}`,
      [{ text: 'OK' }]
    );
  };

  const filterButtons = [
    { label: 'All', value: 'all' },
    { label: 'Stocks', value: 'stock' },
    { label: 'Crypto', value: 'crypto' },
    { label: 'ETFs', value: 'etf' },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Portfolio Summary */}
      <View style={styles.summarySection}>
        <Text style={styles.summaryTitle}>Portfolio Summary</Text>
        <View style={styles.summaryCards}>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Total Value</Text>
            <Text style={styles.summaryValue}>${totalValue.toLocaleString()}</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Stocks</Text>
            <Text style={styles.summaryValue}>${getTotalByType('stock').toLocaleString()}</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>Crypto</Text>
            <Text style={styles.summaryValue}>${getTotalByType('crypto').toLocaleString()}</Text>
          </View>
          <View style={styles.summaryCard}>
            <Text style={styles.summaryLabel}>ETFs</Text>
            <Text style={styles.summaryValue}>${getTotalByType('etf').toLocaleString()}</Text>
          </View>
        </View>
      </View>

      {/* Filter Buttons */}
      <View style={styles.filterSection}>
        {filterButtons.map((filter) => (
          <TouchableOpacity
            key={filter.value}
            style={[
              styles.filterButton,
              selectedFilter === filter.value && styles.filterButtonActive,
            ]}
            onPress={() => setSelectedFilter(filter.value as any)}
          >
            <Text
              style={[
                styles.filterButtonText,
                selectedFilter === filter.value && styles.filterButtonTextActive,
              ]}
            >
              {filter.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Portfolio Items */}
      <View style={styles.portfolioSection}>
        <Text style={styles.sectionTitle}>Holdings</Text>
        <FlatList
          data={filteredItems}
          renderItem={renderPortfolioItem}
          keyExtractor={(item) => item.id}
          showsVerticalScrollIndicator={false}
          ItemSeparatorComponent={() => <View style={styles.separator} />}
        />
      </View>

      {/* Performance Chart Placeholder */}
      <View style={styles.chartSection}>
        <Text style={styles.sectionTitle}>Performance</Text>
        <View style={styles.chartPlaceholder}>
          <Text style={styles.chartText}>📈 Portfolio Chart</Text>
          <Text style={styles.chartSubtext}>Interactive charts coming soon</Text>
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
  summarySection: {
    padding: 20,
  },
  summaryTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  summaryCards: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  summaryCard: {
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
  filterSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  filterButton: {
    backgroundColor: '#16213e',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    marginRight: 12,
  },
  filterButtonActive: {
    backgroundColor: '#00d4ff',
  },
  filterButtonText: {
    color: '#8892b0',
    fontSize: 14,
    fontWeight: '600',
  },
  filterButtonTextActive: {
    color: '#ffffff',
  },
  portfolioSection: {
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  portfolioItem: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  symbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  name: {
    fontSize: 14,
    color: '#8892b0',
    marginTop: 4,
  },
  itemRight: {
    alignItems: 'flex-end',
  },
  quantity: {
    fontSize: 14,
    color: '#8892b0',
  },
  typeLabel: {
    fontSize: 12,
    color: '#00d4ff',
    fontWeight: '600',
    marginTop: 4,
  },
  itemDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  priceInfo: {
    flex: 1,
  },
  currentPrice: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    marginBottom: 4,
  },
  change: {
    fontSize: 14,
    fontWeight: '500',
  },
  positive: {
    color: '#00ff88',
  },
  negative: {
    color: '#ff6b6b',
  },
  value: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  separator: {
    height: 8,
  },
  chartSection: {
    padding: 20,
    paddingBottom: 40,
  },
  chartPlaceholder: {
    backgroundColor: '#16213e',
    height: 200,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  chartText: {
    fontSize: 24,
    color: '#8892b0',
    marginBottom: 8,
  },
  chartSubtext: {
    fontSize: 14,
    color: '#8892b0',
  },
});

export default PortfolioScreen;