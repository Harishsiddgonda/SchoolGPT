import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator
} from 'react-native';
import { mobileAPI } from '../api/mobileClient';

export const ChatScreen: React.FC = () => {
  const [question, setQuestion] = useState('What is the schools leave policy for students?');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<any[]>([]);
  const [language, setLanguage] = useState<'en' | 'kn' | 'hi'>('en');
  const [model, setModel] = useState<string>('');

  const handleAsk = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await mobileAPI.sendQuery(question, language);
      setAnswer(res.answer);
      setSources(res.sources || []);
      setModel(res.model || '');
    } catch (e: any) {
      setAnswer('Could not connect to SchoolGPT assistant. Ensure backend server is running.');
      setSources([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      
      {/* Language Switcher */}
      <View style={styles.langRow}>
        <Text style={styles.langLabel}>Language:</Text>
        {(['en', 'kn', 'hi'] as const).map((l) => (
          <TouchableOpacity
            key={l}
            onPress={() => setLanguage(l)}
            style={[styles.langBtn, language === l && styles.langBtnActive]}
          >
            <Text style={[styles.langBtnText, language === l && styles.langBtnTextActive]}>
              {l === 'en' ? 'English' : l === 'kn' ? 'ಕನ್ನಡ' : 'हिंदी'}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Query Input Box */}
      <View style={styles.inputCard}>
        <TextInput
          style={styles.input}
          value={question}
          onChangeText={setQuestion}
          placeholder="Ask anything about school policies, fees, leave..."
          placeholderTextColor="#94a3b8"
          multiline
        />
        <TouchableOpacity
          style={styles.askButton}
          onPress={handleAsk}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#ffffff" size="small" />
          ) : (
            <Text style={styles.askButtonText}>Ask Assistant</Text>
          )}
        </TouchableOpacity>
      </View>

      {/* Answer Panel */}
      {answer ? (
        <View style={styles.answerCard}>
          <View style={styles.answerHeader}>
            <View style={styles.checkBadge}>
              <Text style={styles.checkText}>✓</Text>
            </View>
            <Text style={styles.answerTitle}>Answer</Text>
            {model ? <Text style={styles.modelBadge}>{model}</Text> : null}
          </View>
          <Text style={styles.answerBody}>{answer}</Text>
        </View>
      ) : null}

      {/* Sources (Cited) */}
      {sources.length > 0 ? (
        <View style={styles.sourcesCard}>
          <Text style={styles.sourcesTitle}>Sources (Cited)</Text>
          {sources.map((s, idx) => (
            <View key={idx} style={styles.sourceItem}>
              <Text style={styles.sourceName}>{s.title}</Text>
              <Text style={styles.sourceDetails}>
                Page {s.page} {s.section ? `• ${s.section}` : ''}
              </Text>
              <Text style={styles.sourceSnippet}>"{s.snippet}"</Text>
            </View>
          ))}
        </View>
      ) : null}

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
    paddingBottom: 40,
  },
  langRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8,
  },
  langLabel: {
    color: '#94a3b8',
    fontSize: 12,
    fontWeight: '600',
  },
  langBtn: {
    backgroundColor: '#1e293b',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#334155',
  },
  langBtnActive: {
    backgroundColor: '#2563eb',
    borderColor: '#38bdf8',
  },
  langBtnText: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '600',
  },
  langBtnTextActive: {
    color: '#ffffff',
  },
  inputCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 14,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 16,
  },
  input: {
    color: '#ffffff',
    fontSize: 14,
    minHeight: 50,
  },
  askButton: {
    backgroundColor: '#7c3aed',
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    marginTop: 10,
  },
  askButtonText: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 13,
  },
  answerCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  answerHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
    paddingBottom: 8,
  },
  checkBadge: {
    backgroundColor: '#10b981',
    width: 22,
    height: 22,
    borderRadius: 11,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  checkText: {
    color: '#ffffff',
    fontWeight: '900',
    fontSize: 12,
  },
  answerTitle: {
    fontSize: 16,
    fontWeight: '800',
    color: '#0f172a',
    flex: 1,
  },
  modelBadge: {
    fontSize: 10,
    color: '#2563eb',
    backgroundColor: '#eff6ff',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  answerBody: {
    fontSize: 13,
    lineHeight: 20,
    color: '#1e293b',
  },
  sourcesCard: {
    backgroundColor: '#1e293b',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  sourcesTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#38bdf8',
    marginBottom: 10,
  },
  sourceItem: {
    backgroundColor: '#0f172a',
    padding: 10,
    borderRadius: 10,
    marginBottom: 8,
  },
  sourceName: {
    color: '#ffffff',
    fontWeight: '700',
    fontSize: 12,
  },
  sourceDetails: {
    color: '#a855f7',
    fontSize: 11,
    fontWeight: '600',
    marginVertical: 2,
  },
  sourceSnippet: {
    color: '#94a3b8',
    fontSize: 11,
    fontStyle: 'italic',
  },
});
