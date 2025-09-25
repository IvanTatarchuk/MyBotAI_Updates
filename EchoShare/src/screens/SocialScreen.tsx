import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  FlatList,
  Image,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { Trader, Trade } from '../store/slices/socialSlice';

const SocialScreen: React.FC = () => {
  const { traders, trades, followedTraders, feed } = useSelector((state: RootState) => state.social);
  const [selectedTab, setSelectedTab] = useState<'feed' | 'traders' | 'trades'>('feed');

  const renderTraderCard = ({ item }: { item: Trader }) => {
    const isFollowing = followedTraders.includes(item.id);

    return (
      <TouchableOpacity style={styles.traderCard} onPress={() => handleTraderPress(item)}>
        <View style={styles.traderHeader}>
          <Image source={{ uri: item.avatar }} style={styles.traderAvatar} />
          <View style={styles.traderInfo}>
            <View style={styles.traderMain}>
              <Text style={styles.traderName}>{item.name}</Text>
              {item.verified && <Text style={styles.verifiedBadge}>✓</Text>}
            </View>
            <Text style={styles.traderBio}>{item.bio}</Text>
          </View>
        </View>

        <View style={styles.traderStats}>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{item.followers.toLocaleString()}</Text>
            <Text style={styles.statLabel}>Followers</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>{item.winRate}%</Text>
            <Text style={styles.statLabel}>Win Rate</Text>
          </View>
          <View style={styles.stat}>
            <Text style={styles.statValue}>+{item.totalReturn}%</Text>
            <Text style={styles.statLabel}>Total Return</Text>
          </View>
        </View>

        <View style={styles.specializations}>
          {item.specializations.map((spec, index) => (
            <View key={index} style={styles.specChip}>
              <Text style={styles.specText}>{spec}</Text>
            </View>
          ))}
        </View>

        <TouchableOpacity
          style={[styles.followButton, isFollowing && styles.followingButton]}
          onPress={() => handleFollowPress(item.id)}
        >
          <Text style={[styles.followButtonText, isFollowing && styles.followingButtonText]}>
            {isFollowing ? 'Following' : 'Follow'}
          </Text>
        </TouchableOpacity>
      </TouchableOpacity>
    );
  };

  const renderTradeItem = ({ item }: { item: Trade }) => (
    <View style={styles.tradeItem}>
      <View style={styles.tradeHeader}>
        <Text style={styles.tradeSymbol}>{item.symbol}</Text>
        <Text style={[styles.tradeType, item.type === 'buy' ? styles.buyType : styles.sellType]}>
          {item.type.toUpperCase()}
        </Text>
      </View>
      <Text style={styles.tradeDetails}>
        {item.quantity} shares @ ${item.price}
      </Text>
      <Text style={styles.tradeTime}>
        {new Date(item.timestamp).toLocaleTimeString()}
      </Text>
    </View>
  );

  const renderFeedItem = ({ item }: { item: any }) => {
    if (item.type === 'achievement') {
      return (
        <View style={styles.feedItem}>
          <Text style={styles.achievementText}>🏆 {item.achievement}</Text>
        </View>
      );
    }

    return renderTradeItem({ item });
  };

  const handleTraderPress = (trader: Trader) => {
    Alert.alert(
      trader.name,
      `${trader.bio}\n\nWin Rate: ${trader.winRate}%\nTotal Return: +${trader.totalReturn}%\nFollowers: ${trader.followers.toLocaleString()}`,
      [{ text: 'OK' }]
    );
  };

  const handleFollowPress = (traderId: string) => {
    Alert.alert('Follow', 'Follow functionality would be implemented here', [{ text: 'OK' }]);
  };

  const tabs = [
    { label: 'Feed', value: 'feed' },
    { label: 'Top Traders', value: 'traders' },
    { label: 'Live Trades', value: 'trades' },
  ];

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Social Trading</Text>
        <Text style={styles.headerSubtitle}>Follow and copy successful traders</Text>
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

      {/* Content */}
      {selectedTab === 'feed' && (
        <View style={styles.contentSection}>
          <FlatList
            data={feed}
            renderItem={renderFeedItem}
            keyExtractor={(item, index) => item.id || `feed-${index}`}
            showsVerticalScrollIndicator={false}
          />
        </View>
      )}

      {selectedTab === 'traders' && (
        <View style={styles.contentSection}>
          <FlatList
            data={traders}
            renderItem={renderTraderCard}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        </View>
      )}

      {selectedTab === 'trades' && (
        <View style={styles.contentSection}>
          <FlatList
            data={trades}
            renderItem={renderTradeItem}
            keyExtractor={(item) => item.id}
            showsVerticalScrollIndicator={false}
          />
        </View>
      )}
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
  },
  tabSection: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  tabButton: {
    backgroundColor: '#16213e',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 25,
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
  contentSection: {
    paddingHorizontal: 20,
  },
  traderCard: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  traderHeader: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  traderAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  traderInfo: {
    flex: 1,
  },
  traderMain: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  traderName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginRight: 8,
  },
  verifiedBadge: {
    color: '#00d4ff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  traderBio: {
    fontSize: 14,
    color: '#8892b0',
    lineHeight: 20,
  },
  traderStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 16,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#8892b0',
  },
  specializations: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 16,
  },
  specChip: {
    backgroundColor: '#00d4ff20',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
    marginBottom: 8,
  },
  specText: {
    color: '#00d4ff',
    fontSize: 12,
    fontWeight: '600',
  },
  followButton: {
    backgroundColor: '#00d4ff',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 25,
    alignSelf: 'center',
  },
  followingButton: {
    backgroundColor: '#16213e',
    borderWidth: 1,
    borderColor: '#00d4ff',
  },
  followButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  followingButtonText: {
    color: '#00d4ff',
  },
  tradeItem: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  tradeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  tradeSymbol: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
  },
  tradeType: {
    fontSize: 14,
    fontWeight: '600',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  buyType: {
    backgroundColor: '#00ff8820',
    color: '#00ff88',
  },
  sellType: {
    backgroundColor: '#ff6b6b20',
    color: '#ff6b6b',
  },
  tradeDetails: {
    fontSize: 14,
    color: '#8892b0',
    marginBottom: 4,
  },
  tradeTime: {
    fontSize: 12,
    color: '#8892b0',
  },
  feedItem: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
  },
  achievementText: {
    fontSize: 16,
    color: '#00d4ff',
    fontWeight: '600',
  },
});

export default SocialScreen;