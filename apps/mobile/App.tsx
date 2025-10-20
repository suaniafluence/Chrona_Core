import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { authStorage } from './src/services/secureStorage';
import { StatusBar } from 'expo-status-bar';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import HomeScreen from './src/screens/HomeScreen';
import QRCodeScreen from './src/screens/QRCodeScreen';
import HistoryScreen from './src/screens/HistoryScreen';

// Onboarding Screens
import HRCodeScreen from './src/screens/onboarding/HRCodeScreen';
import OTPVerificationScreen from './src/screens/onboarding/OTPVerificationScreen';
import CompleteOnboardingScreen from './src/screens/onboarding/CompleteOnboardingScreen';

export type RootStackParamList = {
  Login: undefined;
  Home: undefined;
  QRCode: undefined;
  History: undefined;
  HRCode: undefined;
  OTPVerification: { sessionToken: string; email: string };
  CompleteOnboarding: { sessionToken: string; email: string };
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = await authStorage.getToken();
      setIsAuthenticated(!!token);
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return null; // ou un splash screen
  }

  return (
    <NavigationContainer>
      <StatusBar style="auto" />
      <Stack.Navigator
        initialRouteName={isAuthenticated ? 'Home' : 'Login'}
        screenOptions={{
          headerStyle: {
            backgroundColor: '#667eea',
          },
          headerTintColor: '#fff',
          headerTitleStyle: {
            fontWeight: 'bold',
          },
        }}
      >
        {!isAuthenticated ? (
          <>
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="HRCode"
              component={HRCodeScreen}
              options={{ headerShown: false }}
            />
            <Stack.Screen
              name="OTPVerification"
              component={OTPVerificationScreen}
              options={{
                title: 'Vérification OTP',
                headerBackTitle: 'Retour',
              }}
            />
            <Stack.Screen
              name="CompleteOnboarding"
              component={CompleteOnboardingScreen}
              options={{
                title: 'Finalisation',
                headerBackTitle: 'Retour',
              }}
            />
          </>
        ) : (
          <>
            <Stack.Screen
              name="Home"
              component={HomeScreen}
              options={{ title: 'Chrona' }}
            />
            <Stack.Screen
              name="QRCode"
              component={QRCodeScreen}
              options={{ title: 'QR Code' }}
            />
            <Stack.Screen
              name="History"
              component={HistoryScreen}
              options={{ title: 'Historique' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
