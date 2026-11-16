import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity
} from 'react-native';
import { mobileAPI } from '../api/mobileClient';

export const KnowledgeScreen: React.FC = () => {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const data = await mobileAPI.getDocuments();
        setDocuments(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchDocs();
  }, []);

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>School Documents</Text>
      <Text style={styles.subtitle}>Verified institutional knowledge base</Text>

      {loading ? (
        <ActivityIndicator color="#38bdf8" style={{ marginTop: 40 }} />
      ) : documents.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyText}>No documents found in knowledge base.</Text>
        </View>
      ) : (
        documents.map((d) => (
          <View key={d.id} style={styles.docCard}>
            <View style={styles.badgeRow}>
              <Text style={styles.catBadge}>{d.category}</Text>
              <Text style={styles.roleBadge}>{d.min_role}+</Text>
            </View>
            <Text style={styles.docTitle}>{d.title}</Text>
            <Text style={styles.docMeta}>
              {d.page_count} Pages • {d.chunk_count} Chunks • {d.file_size_kb} KB
            </Text>
          </View>
        ))
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  content: {
    padding: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '800',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginBottom: 16,
    marginTop: 2,
  },
  docCard: {
    backgroundColor: '#1e293b',
    padding: 14,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 10,
  },
  badgeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  catBadge: {
    color: '#38bdf8',
    backgroundColor: '#0369a1',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    fontSize: 10,
    fontWeight: '700',
  },
  roleBadge: {
    color: '#c084fc',
    fontSize: 11,
    fontWeight: '600',
  },
  docTitle: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '700',
    marginBottom: 4,
  },
  docMeta: {
    color: '#64748b',
    fontSize: 11,
  },
  empty: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    color: '#64748b',
    fontSize: 13,
  },
});
