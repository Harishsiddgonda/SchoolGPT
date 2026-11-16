import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { setAuthToken } from '../api/mobileClient';

interface ProfileScreenProps {
  user: any;
  onLogout: () => void;
}

export const ProfileScreen: React.FC<ProfileScreenProps> = ({ user, onLogout }) => {
  const handleLogout = () => {
    setAuthToken(null);
    onLogout();
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {user?.full_name ? user.full_name[0] : 'U'}
          </Text>
        </View>

        <Text style={styles.name}>{user?.full_name || 'School User'}</Text>
        <Text style={styles.username}>@{user?.username || 'user'}</Text>
        
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{user?.role || 'Student'}</Text>
        </View>

        <View style={styles.divider} />

        <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
          <Text style={styles.logoutText}>Log Out</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footer}>
        RSR Technologies • SchoolGPT Mobile v2.5.0
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    padding: 20,
    justifyContent: 'center',
  },
  card: {
    backgroundColor: '#1e293b',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#2563eb',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  avatarText: {
    color: '#ffffff',
    fontSize: 24,
    fontWeight: '800',
  },
  name: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '800',
  },
  username: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: 2,
  },
  badge: {
    backgroundColor: '#7c3aed',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 10,
  },
  badgeText: {
    color: '#ffffff',
    fontSize: 11,
    fontWeight: '700',
  },
  divider: {
    width: '100%',
    height: 1,
    backgroundColor: '#334155',
    marginVertical: 20,
  },
  logoutBtn: {
    backgroundColor: '#450a0a',
    borderColor: '#991b1b',
    borderWidth: 1,
    paddingVertical: 10,
    paddingHorizontal: 24,
    borderRadius: 10,
  },
  logoutText: {
    color: '#f87171',
    fontWeight: '700',
    fontSize: 13,
  },
  footer: {
    color: '#64748b',
    fontSize: 11,
    textAlign: 'center',
    marginTop: 24,
  },
});
