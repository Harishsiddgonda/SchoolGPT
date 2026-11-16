import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  SafeAreaView
} from 'react-native';
import { mobileAPI, setAuthToken, setBaseUrl, getBaseUrl } from '../api/mobileClient';

interface LoginScreenProps {
  onLoginSuccess: (user: any) => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('student');
  const [password, setPassword] = useState('password123');
  const [serverUrl, setServerUrl] = useState(getBaseUrl());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const demoRoles = [
    { label: 'Admin', user: 'admin' },
    { label: 'Principal', user: 'principal' },
    { label: 'Teacher', user: 'teacher' },
    { label: 'Parent', user: 'parent' },
    { label: 'Student', user: 'student' }
  ];

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    setBaseUrl(serverUrl);
    try {
      const data = await mobileAPI.login(username, password);
      setAuthToken(data.access_token);
      onLoginSuccess(data.user);
    } catch (e: any) {
      setError(e.message || 'Login failed. Check server URL and credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        
        {/* Brand Header */}
        <View style={styles.header}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoText}>RSR</Text>
          </View>
          <Text style={styles.title}>SchoolGPT</Text>
          <Text style={styles.subtitle}>AI School Assistant • LLM + RAG</Text>
          <Text style={styles.tagline}>Smart • Reliable • Instant Answers</Text>
        </View>

        {/* Demo Fast Logins */}
        <View style={styles.demoSection}>
          <Text style={styles.demoTitle}>QUICK DEMO PROFILES:</Text>
          <View style={styles.demoRow}>
            {demoRoles.map((d) => (
              <TouchableOpacity
                key={d.user}
                onPress={() => {
                  setUsername(d.user);
                  setPassword('password123');
                }}
                style={[
                  styles.demoChip,
                  username === d.user && styles.demoChipActive
                ]}
              >
                <Text
                  style={[
                    styles.demoChipText,
                    username === d.user && styles.demoChipTextActive
                  ]}
                >
                  {d.label}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>

        {/* Login Card */}
        <View style={styles.card}>
          {error ? <Text style={styles.errorText}>{error}</Text> : null}

          <Text style={styles.inputLabel}>Username</Text>
          <TextInput
            style={styles.input}
            value={username}
            onChangeText={setUsername}
            autoCapitalize="none"
            placeholder="Username"
            placeholderTextColor="#94a3b8"
          />

          <Text style={styles.inputLabel}>Password</Text>
          <TextInput
            style={styles.input}
            value={password}
            onChangeText={setPassword}
            secureTextEntry
            placeholder="Password"
            placeholderTextColor="#94a3b8"
          />

          <Text style={styles.inputLabel}>Server URL</Text>
          <TextInput
            style={styles.input}
            value={serverUrl}
            onChangeText={setServerUrl}
            autoCapitalize="none"
            placeholder="e.g. http://10.0.2.2:8000"
            placeholderTextColor="#94a3b8"
          />

          <TouchableOpacity
            style={styles.button}
            onPress={handleLogin}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#ffffff" />
            ) : (
              <Text style={styles.buttonText}>Sign In to SchoolGPT</Text>
            )}
          </TouchableOpacity>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scroll: {
    padding: 24,
    justifyContent: 'center',
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
  },
  logoBadge: {
    backgroundColor: '#2563eb',
    width: 52,
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  logoText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '900',
  },
  title: {
    color: '#ffffff',
    fontSize: 28,
    fontWeight: '800',
  },
  subtitle: {
    color: '#38bdf8',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 4,
  },
  tagline: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 4,
  },
  demoSection: {
    marginBottom: 20,
  },
  demoTitle: {
    color: '#64748b',
    fontSize: 11,
    fontWeight: '700',
    marginBottom: 8,
  },
  demoRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  demoChip: {
    backgroundColor: '#1e293b',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  demoChipActive: {
    backgroundColor: '#2563eb',
    borderColor: '#38bdf8',
  },
  demoChipText: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '600',
  },
  demoChipTextActive: {
    color: '#ffffff',
  },
  card: {
    backgroundColor: '#1e293b',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#334155',
  },
  inputLabel: {
    color: '#cbd5e1',
    fontSize: 12,
    fontWeight: '600',
    marginBottom: 6,
    marginTop: 10,
  },
  input: {
    backgroundColor: '#0f172a',
    borderWidth: 1,
    borderColor: '#334155',
    color: '#ffffff',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
  },
  button: {
    backgroundColor: '#2563eb',
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 15,
    fontWeight: '700',
  },
  errorText: {
    color: '#f87171',
    fontSize: 12,
    backgroundColor: '#450a0a',
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
  },
});
