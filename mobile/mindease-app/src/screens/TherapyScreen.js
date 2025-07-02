import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, TextInput } from 'react-native';
import { useTranslation } from 'react-i18next';
import { AuthContext } from '../contexts/AuthContext';

// Import components
import SafeAreaWrapper from '../components/SafeAreaWrapper';
import Header from '../components/Header';
import MessageBubble from '../components/MessageBubble';
import TherapyTools from '../components/TherapyTools';

const TherapyScreen = () => {
  const { t } = useTranslation();
  const { userToken } = useContext(AuthContext);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [sessionInfo, setSessionInfo] = useState({
    duration: 0,
    mode: 'rule-based',
    startTime: new Date(),
  });

  // Initialize or resume therapy session
  useEffect(() => {
    initializeSession();
  }, []);

  // Start timer for session duration
  useEffect(() => {
    if (!sessionId) return;
    
    const timer = setInterval(() => {
      setSessionInfo(prev => ({
        ...prev,
        duration: Math.floor((new Date() - new Date(prev.startTime)) / 1000),
      }));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [sessionId]);

  const initializeSession = async () => {
    if (!userToken) return;
    
    setIsLoading(true);
    try {
      // Check for existing active session
      const checkResponse = await fetch('https://api.mindease.app/therapy/active-session', {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (checkResponse.ok) {
        const checkData = await checkResponse.json();
        
        if (checkData.active_session) {
          // Resume existing session
          setSessionId(checkData.session_id);
          setSessionInfo({
            duration: Math.floor((new Date() - new Date(checkData.start_time)) / 1000),
            mode: checkData.mode,
            startTime: checkData.start_time,
          });
          
          // Fetch existing messages
          fetchMessages(checkData.session_id);
        } else {
          // Start new session
          startNewSession();
        }
      } else {
        console.error('Failed to check active session');
        startNewSession();
      }
    } catch (error) {
      console.error('Error initializing session:', error);
      startNewSession();
    } finally {
      setIsLoading(false);
    }
  };

  const startNewSession = async () => {
    if (!userToken) return;
    
    try {
      const response = await fetch('https://api.mindease.app/therapy/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`,
        },
        body: JSON.stringify({
          language: t('current_language_code'),
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setSessionInfo({
          duration: 0,
          mode: 'rule-based',
          startTime: new Date(),
        });
        
        // Add welcome message
        setMessages([
          {
            id: 'welcome',
            content: t('therapy_welcome_message'),
            sender: 'therapist',
            timestamp: new Date(),
          },
        ]);
      } else {
        console.error('Failed to start new session');
      }
    } catch (error) {
      console.error('Error starting new session:', error);
    }
  };

  const fetchMessages = async (sid) => {
    if (!userToken || !sid) return;
    
    try {
      const response = await fetch(`https://api.mindease.app/therapy/sessions/${sid}/messages`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages.map(msg => ({
          id: msg.id,
          content: msg.content,
          sender: msg.sender_type,
          timestamp: new Date(msg.created_at),
        })));
      } else {
        console.error('Failed to fetch messages');
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const sendMessage = async () => {
    if (!userToken || !sessionId || !inputMessage.trim()) return;
    
    // Add user message to UI immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      content: inputMessage.trim(),
      sender: 'user',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      const response = await fetch(`https://api.mindease.app/therapy/sessions/${sessionId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`,
        },
        body: JSON.stringify({
          content: userMessage.content,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Update session mode if it changed
        if (data.session_mode !== sessionInfo.mode) {
          setSessionInfo(prev => ({
            ...prev,
            mode: data.session_mode,
          }));
        }
        
        // Add therapist response
        setMessages(prev => [...prev, {
          id: data.message_id,
          content: data.response,
          sender: 'therapist',
          timestamp: new Date(),
        }]);
      } else {
        console.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const endSession = async () => {
    if (!userToken || !sessionId) return;
    
    try {
      const response = await fetch(`https://api.mindease.app/therapy/sessions/${sessionId}/end`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        // Add session end message
        setMessages(prev => [...prev, {
          id: 'session-end',
          content: t('therapy_session_ended'),
          sender: 'system',
          timestamp: new Date(),
        }]);
        
        // Reset session
        setSessionId(null);
        setSessionInfo({
          duration: 0,
          mode: 'rule-based',
          startTime: new Date(),
        });
      } else {
        console.error('Failed to end session');
      }
    } catch (error) {
      console.error('Error ending session:', error);
    }
  };

  // Format seconds to MM:SS
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <SafeAreaWrapper>
      <Header title={t('therapy_session')} />
      
      <View style={styles.container}>
        <View style={styles.sessionInfoBar}>
          <View style={styles.sessionInfoItem}>
            <Text style={styles.sessionInfoLabel}>{t('session_id')}</Text>
            <Text style={styles.sessionInfoValue}>
              {sessionId ? sessionId.substring(0, 8) : '-'}
            </Text>
          </View>
          
          <View style={styles.sessionInfoItem}>
            <Text style={styles.sessionInfoLabel}>{t('duration')}</Text>
            <Text style={styles.sessionInfoValue}>
              {formatDuration(sessionInfo.duration)}
            </Text>
          </View>
          
          <View style={styles.sessionInfoItem}>
            <Text style={styles.sessionInfoLabel}>{t('mode')}</Text>
            <Text style={styles.sessionInfoValue}>
              {sessionInfo.mode === 'rule-based' ? t('rule_based') : t('mistral_ai')}
            </Text>
          </View>
        </View>
        
        <ScrollView 
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
        >
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message.content}
              sender={message.sender}
              timestamp={message.timestamp}
            />
          ))}
          
          {isLoading && (
            <View style={styles.loadingIndicator}>
              <Text style={styles.loadingText}>{t('therapist_typing')}</Text>
            </View>
          )}
        </ScrollView>
        
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputMessage}
            onChangeText={setInputMessage}
            placeholder={t('type_message')}
            multiline
            editable={!isLoading && !!sessionId}
          />
          <TouchableOpacity 
            style={[
              styles.sendButton,
              (!inputMessage.trim() || isLoading || !sessionId) && styles.sendButtonDisabled
            ]}
            onPress={sendMessage}
            disabled={!inputMessage.trim() || isLoading || !sessionId}
          >
            <Text style={styles.sendButtonText}>{t('send')}</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.toolsContainer}>
          <TherapyTools sessionId={sessionId} />
          
          {sessionId && (
            <TouchableOpacity 
              style={styles.endSessionButton}
              onPress={endSession}
            >
              <Text style={styles.endSessionText}>{t('end_session')}</Text>
            </TouchableOpacity>
          )}
        </View>
      </View>
    </SafeAreaWrapper>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8f9fa',
  },
  sessionInfoBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  sessionInfoItem: {
    alignItems: 'center',
  },
  sessionInfoLabel: {
    fontSize: 12,
    color: '#6c757d',
    marginBottom: 4,
  },
  sessionInfoValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  messagesContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  messagesContent: {
    padding: 16,
  },
  loadingIndicator: {
    padding: 8,
    alignSelf: 'flex-start',
    backgroundColor: '#e9ecef',
    borderRadius: 16,
    marginVertical: 8,
  },
  loadingText: {
    color: '#6c757d',
    fontStyle: 'italic',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  input: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginRight: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
    maxHeight: 100,
  },
  sendButton: {
    backgroundColor: '#4361ee',
    borderRadius: 20,
    paddingVertical: 10,
    paddingHorizontal: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#a0aec0',
  },
  sendButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  toolsContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  endSessionButton: {
    backgroundColor: '#e53e3e',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  endSessionText: {
    color: '#ffffff',
    fontWeight: '600',
  },
});

export default TherapyScreen;
