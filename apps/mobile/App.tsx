import React, { useState } from 'react';
import { SafeAreaView, View, Text, TouchableOpacity, StyleSheet, StatusBar } from 'react-native';
import { LoginScreen } from './src/screens/LoginScreen';
import { ChatScreen } from './src/screens/ChatScreen';
import { KnowledgeScreen } from './src/screens/KnowledgeScreen';
import { ProfileScreen } from './src/screens/ProfileScreen';

export default function App() {
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'knowledge' | 'profile'>('chat');

  if (!currentUser) {
    return (
      <>
        <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
        <LoginScreen onLoginSuccess={setCurrentUser} />
      </>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
      
      {/* Top Mobile Bar */}
      <View style={styles.topBar}>
        <View style={styles.topTitleRow}>
          <Text style={styles.topLogo}>RSR</Text>
          <Text style={styles.topTitle}>SchoolGPT</Text>
        </View>
        <Text style={styles.topRole}>{currentUser.role}</Text>
      </View>

      {/* Screen View */}
      <View style={styles.main}>
        {activeTab === 'chat' && <ChatScreen />}
        {activeTab === 'knowledge' && <KnowledgeScreen />}
        {activeTab === 'profile' && (
          <ProfileScreen user={currentUser} onLogout={() => setCurrentUser(null)} />
        )}
      </View>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          onPress={() => setActiveTab('chat')}
          style={[styles.navItem, activeTab === 'chat' && styles.navItemActive]}
        >
          <Text style={[styles.navText, activeTab === 'chat' && styles.navTextActive]}>
            💬 Assistant
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setActiveTab('knowledge')}
          style={[styles.navItem, activeTab === 'knowledge' && styles.navItemActive]}
        >
          <Text style={[styles.navText, activeTab === 'knowledge' && styles.navTextActive]}>
            📚 Knowledge
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          onPress={() => setActiveTab('profile')}
          style={[styles.navItem, activeTab === 'profile' && styles.navItemActive]}
        >
          <Text style={[styles.navText, activeTab === 'profile' && styles.navTextActive]}>
            👤 Profile
          </Text>
        </TouchableOpacity>
      </View>

    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  topBar: {
    height: 54,
    backgroundColor: '#1e293b',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#334155',
  },
  topTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  topLogo: {
    color: '#ffffff',
    backgroundColor: '#2563eb',
    fontWeight: '900',
    fontSize: 12,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  topTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '800',
  },
  topRole: {
    color: '#38bdf8',
    fontSize: 11,
    fontWeight: '700',
    backgroundColor: '#0f172a',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  main: {
    flex: 1,
  },
  bottomNav: {
    height: 60,
    backgroundColor: '#1e293b',
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#334155',
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navItemActive: {
    borderTopWidth: 2,
    borderTopColor: '#38bdf8',
  },
  navText: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '600',
  },
  navTextActive: {
    color: '#38bdf8',
    fontWeight: '800',
  },
});
