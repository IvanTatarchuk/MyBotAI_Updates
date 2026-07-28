import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
} from 'react-native';
import { useSelector } from 'react-redux';
import { RootState } from '../store/store';
import { User } from '../store/slices/userSlice';

const ProfileScreen: React.FC = () => {
  const { user } = useSelector((state: RootState) => state.user);
  const [activeSection, setActiveSection] = useState<'profile' | 'achievements' | 'settings'>('profile');

  if (!user) return null;

  const menuItems = [
    { label: 'Profile', value: 'profile', icon: '👤' },
    { label: 'Achievements', value: 'achievements', icon: '🏆' },
    { label: 'Settings', value: 'settings', icon: '⚙️' },
  ];

  const achievements = [
    { title: 'First Investment', description: 'Made your first investment', icon: '🎯', earned: true },
    { title: 'Portfolio Master', description: 'Diversified portfolio across 5+ asset types', icon: '📊', earned: true },
    { title: 'Social Trader', description: 'Followed 10+ traders', icon: '👥', earned: true },
    { title: 'Risk Manager', description: 'Maintained portfolio risk under 15%', icon: '🛡️', earned: false },
    { title: 'Crypto Expert', description: 'Achieved 50% crypto portfolio growth', icon: '₿', earned: false },
    { title: 'Market Timer', description: 'Successfully timed 5 market moves', icon: '⏰', earned: false },
  ];

  const settingsItems = [
    { label: 'Notifications', icon: '🔔', action: 'notifications' },
    { label: 'Privacy & Security', icon: '🔒', action: 'privacy' },
    { label: 'Subscription', icon: '💎', action: 'subscription' },
    { label: 'Help & Support', icon: '❓', action: 'support' },
    { label: 'About', icon: 'ℹ️', action: 'about' },
  ];

  const handleMenuPress = (section: string) => {
    setActiveSection(section as any);
  };

  const handleSettingPress = (action: string) => {
    Alert.alert('Setting', `${action} settings would open here`, [{ text: 'OK' }]);
  };

  const renderProfile = () => (
    <View style={styles.contentSection}>
      {/* User Info */}
      <View style={styles.userCard}>
        <Image source={{ uri: user.avatar }} style={styles.userAvatar} />
        <View style={styles.userInfo}>
          <Text style={styles.userName}>{user.name}</Text>
          <Text style={styles.userEmail}>{user.email}</Text>
          <View style={styles.subscriptionBadge}>
            <Text style={styles.subscriptionText}>{user.subscription.toUpperCase()}</Text>
          </View>
        </View>
      </View>

      {/* Stats */}
      <View style={styles.statsSection}>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{user.level}</Text>
          <Text style={styles.statLabel}>Level</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{user.experience}</Text>
          <Text style={styles.statLabel}>Experience</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statNumber}>{user.badges.length}</Text>
          <Text style={styles.statLabel}>Badges</Text>
        </View>
      </View>

      {/* Risk Profile */}
      <View style={styles.profileSection}>
        <Text style={styles.sectionTitle}>Risk Profile</Text>
        <View style={styles.riskCard}>
          <Text style={styles.riskTitle}>Risk Tolerance</Text>
          <Text style={[styles.riskValue, styles[user.riskTolerance]]}>
            {user.riskTolerance.charAt(0).toUpperCase() + user.riskTolerance.slice(1)}
          </Text>
        </View>
      </View>

      {/* Goals */}
      <View style={styles.profileSection}>
        <Text style={styles.sectionTitle}>Investment Goals</Text>
        <View style={styles.goalsContainer}>
          {user.investmentGoals.map((goal, index) => (
            <View key={index} style={styles.goalChip}>
              <Text style={styles.goalText}>{goal}</Text>
            </View>
          ))}
        </View>
      </View>
    </View>
  );

  const renderAchievements = () => (
    <View style={styles.contentSection}>
      <Text style={styles.sectionTitle}>🏆 Achievements</Text>
      <View style={styles.achievementsGrid}>
        {achievements.map((achievement, index) => (
          <View
            key={index}
            style={[
              styles.achievementCard,
              achievement.earned && styles.achievementEarned,
            ]}
          >
            <Text style={styles.achievementIcon}>{achievement.icon}</Text>
            <Text style={styles.achievementTitle}>{achievement.title}</Text>
            <Text style={styles.achievementDescription}>{achievement.description}</Text>
          </View>
        ))}
      </View>
    </View>
  );

  const renderSettings = () => (
    <View style={styles.contentSection}>
      <Text style={styles.sectionTitle}>⚙️ Settings</Text>
      {settingsItems.map((item, index) => (
        <TouchableOpacity
          key={index}
          style={styles.settingItem}
          onPress={() => handleSettingPress(item.action)}
        >
          <Text style={styles.settingIcon}>{item.icon}</Text>
          <Text style={styles.settingLabel}>{item.label}</Text>
          <Text style={styles.settingArrow}>›</Text>
        </TouchableOpacity>
      ))}
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Menu Tabs */}
      <View style={styles.menuSection}>
        {menuItems.map((item) => (
          <TouchableOpacity
            key={item.value}
            style={[
              styles.menuButton,
              activeSection === item.value && styles.menuButtonActive,
            ]}
            onPress={() => handleMenuPress(item.value)}
          >
            <Text style={styles.menuIcon}>{item.icon}</Text>
            <Text
              style={[
                styles.menuLabel,
                activeSection === item.value && styles.menuLabelActive,
              ]}
            >
              {item.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Content */}
      {activeSection === 'profile' && renderProfile()}
      {activeSection === 'achievements' && renderAchievements()}
      {activeSection === 'settings' && renderSettings()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
  menuSection: {
    flexDirection: 'row',
    padding: 20,
    backgroundColor: '#16213e',
    margin: 20,
    marginBottom: 0,
    borderRadius: 12,
  },
  menuButton: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 12,
    borderRadius: 8,
  },
  menuButtonActive: {
    backgroundColor: '#00d4ff',
  },
  menuIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  menuLabel: {
    fontSize: 12,
    color: '#8892b0',
    fontWeight: '600',
  },
  menuLabelActive: {
    color: '#ffffff',
  },
  contentSection: {
    padding: 20,
  },
  userCard: {
    backgroundColor: '#16213e',
    padding: 20,
    borderRadius: 12,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  userAvatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    marginRight: 16,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 16,
    color: '#8892b0',
    marginBottom: 8,
  },
  subscriptionBadge: {
    backgroundColor: '#00d4ff',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  subscriptionText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '600',
  },
  statsSection: {
    flexDirection: 'row',
    marginBottom: 20,
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
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#8892b0',
  },
  profileSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 16,
  },
  riskCard: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
  },
  riskTitle: {
    fontSize: 14,
    color: '#8892b0',
    marginBottom: 8,
  },
  riskValue: {
    fontSize: 18,
    fontWeight: '600',
  },
  conservative: {
    color: '#00ff88',
  },
  moderate: {
    color: '#ffaa00',
  },
  aggressive: {
    color: '#ff6b6b',
  },
  goalsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  goalChip: {
    backgroundColor: '#00d4ff20',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  goalText: {
    color: '#00d4ff',
    fontSize: 14,
    fontWeight: '600',
  },
  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  achievementCard: {
    backgroundColor: '#16213e',
    width: '48%',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
    opacity: 0.6,
  },
  achievementEarned: {
    opacity: 1,
    borderColor: '#00d4ff',
    borderWidth: 2,
  },
  achievementIcon: {
    fontSize: 24,
    marginBottom: 8,
  },
  achievementTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 4,
  },
  achievementDescription: {
    fontSize: 12,
    color: '#8892b0',
    textAlign: 'center',
  },
  settingItem: {
    backgroundColor: '#16213e',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
  },
  settingIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  settingLabel: {
    flex: 1,
    fontSize: 16,
    color: '#ffffff',
  },
  settingArrow: {
    fontSize: 20,
    color: '#8892b0',
  },
});

export default ProfileScreen;