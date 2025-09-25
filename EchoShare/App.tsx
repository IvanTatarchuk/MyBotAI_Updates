/**
 * EchoShare - AI-Powered Personal Finance & Social Investing Platform
 * A revolutionary fintech app that combines AI-driven financial insights with social trading
 */

import React from 'react';
import { StatusBar, StyleSheet } from 'react-native';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { Provider } from 'react-redux';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

import { store } from './src/store/store';
import DashboardScreen from './src/screens/DashboardScreen';
import PortfolioScreen from './src/screens/PortfolioScreen';
import SocialScreen from './src/screens/SocialScreen';
import MarketScreen from './src/screens/MarketScreen';
import ProfileScreen from './src/screens/ProfileScreen';

const Tab = createBottomTabNavigator();

function App() {
  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <StatusBar barStyle="light-content" backgroundColor="#1a1a2e" />
        <NavigationContainer>
          <Tab.Navigator
            screenOptions={{
              tabBarActiveTintColor: '#00d4ff',
              tabBarInactiveTintColor: '#8892b0',
              tabBarStyle: {
                backgroundColor: '#16213e',
                borderTopColor: '#00d4ff',
              },
              headerStyle: {
                backgroundColor: '#1a1a2e',
              },
              headerTintColor: '#ffffff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          >
            <Tab.Screen
              name="Dashboard"
              component={DashboardScreen}
              options={{
                tabBarLabel: 'Home',
                title: 'EchoShare',
              }}
            />
            <Tab.Screen
              name="Portfolio"
              component={PortfolioScreen}
              options={{
                tabBarLabel: 'Portfolio',
              }}
            />
            <Tab.Screen
              name="Social"
              component={SocialScreen}
              options={{
                tabBarLabel: 'Social',
              }}
            />
            <Tab.Screen
              name="Market"
              component={MarketScreen}
              options={{
                tabBarLabel: 'Market',
              }}
            />
            <Tab.Screen
              name="Profile"
              component={ProfileScreen}
              options={{
                tabBarLabel: 'Profile',
              }}
            />
          </Tab.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </Provider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f23',
  },
});

export default App;
