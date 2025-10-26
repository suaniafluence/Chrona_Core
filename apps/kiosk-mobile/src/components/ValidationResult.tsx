import React, { useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import { PunchValidateResponse } from '../services/api';

interface ValidationResultProps {
  result: PunchValidateResponse | null;
}

export default function ValidationResult({ result }: ValidationResultProps) {
  const fadeAnim = new Animated.Value(0);
  const scaleAnim = new Animated.Value(0.5);

  useEffect(() => {
    // Animate in
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 4,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  if (!result) {
    return null;
  }

  const isSuccess = result.success;
  const icon = isSuccess ? '✓' : '✗';
  const backgroundColor = isSuccess ? '#4caf50' : '#f44336';

  return (
    <Animated.View
      style={[
        styles.container,
        { backgroundColor, opacity: fadeAnim, transform: [{ scale: scaleAnim }] },
      ]}
    >
      <View style={styles.content}>
        <Text style={styles.icon}>{icon}</Text>
        <Text style={styles.message}>{result.message}</Text>
        {isSuccess && result.punched_at && (
          <Text style={styles.timestamp}>
            {new Date(result.punched_at).toLocaleTimeString('fr-FR', {
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            })}
          </Text>
        )}
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  content: {
    alignItems: 'center',
  },
  icon: {
    fontSize: 120,
    color: '#fff',
    marginBottom: 24,
    fontWeight: 'bold',
  },
  message: {
    fontSize: 24,
    color: '#fff',
    textAlign: 'center',
    fontWeight: '600',
    marginBottom: 12,
  },
  timestamp: {
    fontSize: 32,
    color: '#fff',
    fontWeight: 'bold',
    marginTop: 8,
  },
});
