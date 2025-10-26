import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaView, StyleSheet } from 'react-native';
import HomeScreen from './src/screens/HomeScreen';
import { KioskConfig } from './src/services/api';
import { HeartbeatService } from './src/services/heartbeat';

export default function App() {
  useEffect(() => {
    // Load kiosk configuration on app start
    const loadConfig = async () => {
      const config = KioskConfig.getInstance();
      await config.loadConfig();
      console.log('Kiosk configuration loaded');

      // Start heartbeat service after config is loaded
      const heartbeatService = HeartbeatService.getInstance();
      heartbeatService.start();
      console.log('Heartbeat service started');
    };

    loadConfig();

    // Cleanup: stop heartbeat when app unmounts
    return () => {
      const heartbeatService = HeartbeatService.getInstance();
      heartbeatService.stop();
      console.log('Heartbeat service stopped');
    };
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />
      <HomeScreen />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a73e8',
  },
});
