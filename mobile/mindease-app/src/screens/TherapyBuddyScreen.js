import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image } from 'react-native';
import { useTranslation } from 'react-i18next';
import { AuthContext } from '../contexts/AuthContext';

// Import components
import SafeAreaWrapper from '../components/SafeAreaWrapper';
import Header from '../components/Header';
import BuddyCard from '../components/BuddyCard';
import MoodSummary from '../components/MoodSummary';
import ChatBubble from '../components/ChatBubble';

const TherapyBuddyScreen = () => {
  const { t } = useTranslation();
  const { userToken } = useContext(AuthContext);
  const [buddy, setBuddy] = useState(null);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [buddyRequests, setBuddyRequests] = useState([]);
  const [showRequests, setShowRequests] = useState(false);

  // Fetch buddy information
  useEffect(() => {
    fetchBuddyInfo();
  }, []);

  const fetchBuddyInfo = async () => {
    if (!userToken) return;
    
    setLoading(true);
    try {
      const response = await fetch('https://api.mindease.app/buddies/current', {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setBuddy(data.buddy);
        
        // If we have a buddy, fetch messages
        if (data.buddy) {
          fetchMessages();
        } else {
          // If no buddy, check for pending requests
          fetchBuddyRequests();
        }
      } else {
        console.error('Failed to fetch buddy information');
      }
    } catch (error) {
      console.error('Error fetching buddy information:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch messages with buddy
  const fetchMessages = async () => {
    if (!userToken || !buddy) return;
    
    try {
      const response = await fetch(`https://api.mindease.app/buddies/messages?buddy_id=${buddy.id}`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      } else {
        console.error('Failed to fetch messages');
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  // Fetch buddy requests
  const fetchBuddyRequests = async () => {
    if (!userToken) return;
    
    try {
      const response = await fetch('https://api.mindease.app/buddies/requests', {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setBuddyRequests(data.requests);
      } else {
        console.error('Failed to fetch buddy requests');
      }
    } catch (error) {
      console.error('Error fetching buddy requests:', error);
    }
  };

  // Send message to buddy
  const sendMessage = async () => {
    if (!userToken || !buddy || !newMessage.trim()) return;
    
    try {
      const response = await fetch('https://api.mindease.app/buddies/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`,
        },
        body: JSON.stringify({
          buddy_id: buddy.id,
          message: newMessage.trim(),
        }),
      });
      
      if (response.ok) {
        // Add message to local state
        const timestamp = new Date().toISOString();
        setMessages([
          ...messages,
          {
            id: `temp-${timestamp}`,
            sender_id: 'me', // This would be the actual user ID in a real app
            content: newMessage.trim(),
            created_at: timestamp,
          },
        ]);
        setNewMessage('');
        
        // Refresh messages to get server-generated ID
        setTimeout(fetchMessages, 1000);
      } else {
        alert(t('message_send_error'));
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert(t('message_send_error'));
    }
  };

  // Accept buddy request
  const acceptBuddyRequest = async (requestId) => {
    if (!userToken) return;
    
    try {
      const response = await fetch(`https://api.mindease.app/buddies/requests/${requestId}/accept`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        alert(t('buddy_request_accepted'));
        // Refresh buddy info
        fetchBuddyInfo();
      } else {
        alert(t('buddy_request_error'));
      }
    } catch (error) {
      console.error('Error accepting buddy request:', error);
      alert(t('buddy_request_error'));
    }
  };

  // Decline buddy request
  const declineBuddyRequest = async (requestId) => {
    if (!userToken) return;
    
    try {
      const response = await fetch(`https://api.mindease.app/buddies/requests/${requestId}/decline`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        // Remove request from local state
        setBuddyRequests(buddyRequests.filter(req => req.id !== requestId));
      } else {
        alert(t('buddy_request_error'));
      }
    } catch (error) {
      console.error('Error declining buddy request:', error);
      alert(t('buddy_request_error'));
    }
  };

  // Find a new buddy
  const findNewBuddy = async () => {
    if (!userToken) return;
    
    try {
      const response = await fetch('https://api.mindease.app/buddies/find', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        alert(t('buddy_request_sent'));
      } else {
        alert(t('buddy_request_error'));
      }
    } catch (error) {
      console.error('Error finding new buddy:', error);
      alert(t('buddy_request_error'));
    }
  };

  return (
    <SafeAreaWrapper>
      <Header title={t('therapy_buddy')} />
      
      <View style={styles.container}>
        {loading ? (
          <View style={styles.centerContent}>
            <Text>{t('loading')}</Text>
          </View>
        ) : buddy ? (
          // We have a buddy
          <>
            <BuddyCard
              name={buddy.name}
              avatar={buddy.avatar}
              lastActive={new Date(buddy.last_active)}
              streak={buddy.streak}
              onViewProfile={() => {/* Navigate to buddy profile */}}
            />
            
            <View style={styles.moodSummaryContainer}>
              <Text style={styles.sectionTitle}>{t('buddy_mood_today')}</Text>
              <MoodSummary
                mood={buddy.current_mood}
                timestamp={new Date(buddy.mood_updated_at)}
                note={buddy.mood_note}
              />
            </View>
            
            <View style={styles.chatContainer}>
              <Text style={styles.sectionTitle}>{t('chat_with_buddy')}</Text>
              
              <ScrollView style={styles.messagesContainer}>
                {messages.length === 0 ? (
                  <View style={styles.emptyChat}>
                    <Image 
                      source={require('../assets/images/chat-empty.png')} 
                      style={styles.emptyChatImage}
                    />
                    <Text style={styles.emptyChatText}>
                      {t('start_conversation')}
                    </Text>
                  </View>
                ) : (
                  messages.map((message) => (
                    <ChatBubble
                      key={message.id}
                      message={message.content}
                      isMe={message.sender_id === 'me'} // This would check against actual user ID
                      timestamp={new Date(message.created_at)}
                    />
                  ))
                )}
              </ScrollView>
              
              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  value={newMessage}
                  onChangeText={setNewMessage}
                  placeholder={t('type_message')}
                  multiline
                />
                <TouchableOpacity 
                  style={styles.sendButton}
                  onPress={sendMessage}
                  disabled={!newMessage.trim()}
                >
                  <Text style={styles.sendButtonText}>{t('send')}</Text>
                </TouchableOpacity>
              </View>
            </View>
          </>
        ) : (
          // No buddy yet
          <View style={styles.noBuddyContainer}>
            <Image 
              source={require('../assets/images/buddy-placeholder.png')} 
              style={styles.noBuddyImage}
            />
            
            <Text style={styles.noBuddyTitle}>{t('no_buddy_yet')}</Text>
            <Text style={styles.noBuddyDescription}>
              {t('buddy_description')}
            </Text>
            
            {buddyRequests.length > 0 ? (
              <>
                <TouchableOpacity 
                  style={styles.viewRequestsButton}
                  onPress={() => setShowRequests(!showRequests)}
                >
                  <Text style={styles.viewRequestsText}>
                    {showRequests ? t('hide_requests') : t('view_buddy_requests')} 
                    ({buddyRequests.length})
                  </Text>
                </TouchableOpacity>
                
                {showRequests && (
                  <View style={styles.requestsContainer}>
                    {buddyRequests.map((request) => (
                      <View key={request.id} style={styles.requestCard}>
                        <View style={styles.requestInfo}>
                          <Image 
                            source={{ uri: request.sender_avatar || 'https://via.placeholder.com/50' }} 
                            style={styles.requestAvatar}
                          />
                          <View>
                            <Text style={styles.requestName}>{request.sender_name}</Text>
                            <Text style={styles.requestDate}>
                              {new Date(request.created_at).toLocaleDateString()}
                            </Text>
                          </View>
                        </View>
                        <View style={styles.requestActions}>
                          <TouchableOpacity 
                            style={[styles.requestButton, styles.acceptButton]}
                            onPress={() => acceptBuddyRequest(request.id)}
                          >
                            <Text style={styles.requestButtonText}>{t('accept')}</Text>
                          </TouchableOpacity>
                          <TouchableOpacity 
                            style={[styles.requestButton, styles.declineButton]}
                            onPress={() => declineBuddyRequest(request.id)}
                          >
                            <Text style={styles.requestButtonText}>{t('decline')}</Text>
                          </TouchableOpacity>
                        </View>
                      </View>
                    ))}
                  </View>
                )}
              </>
            ) : (
              <TouchableOpacity 
                style={styles.findBuddyButton}
                onPress={findNewBuddy}
              >
                <Text style={styles.findBuddyText}>{t('find_buddy')}</Text>
              </TouchableOpacity>
            )}
          </View>
        )}
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
  centerContent: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  moodSummaryContainer: {
    marginTop: 16,
    marginBottom: 16,
  },
  chatContainer: {
    flex: 1,
    marginBottom: 16,
  },
  messagesContainer: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  emptyChat: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  emptyChatImage: {
    width: 80,
    height: 80,
    marginBottom: 16,
    opacity: 0.7,
  },
  emptyChatText: {
    textAlign: 'center',
    color: '#6c757d',
    fontSize: 16,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
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
  sendButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
  noBuddyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  noBuddyImage: {
    width: 120,
    height: 120,
    marginBottom: 24,
  },
  noBuddyTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 12,
    textAlign: 'center',
  },
  noBuddyDescription: {
    fontSize: 16,
    textAlign: 'center',
    color: '#6c757d',
    marginBottom: 24,
  },
  findBuddyButton: {
    backgroundColor: '#4361ee',
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 8,
    minWidth: 200,
    alignItems: 'center',
  },
  findBuddyText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  viewRequestsButton: {
    marginBottom: 16,
  },
  viewRequestsText: {
    color: '#4361ee',
    fontSize: 16,
    fontWeight: '500',
  },
  requestsContainer: {
    width: '100%',
    marginBottom: 16,
  },
  requestCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  requestInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  requestAvatar: {
    width: 50,
    height: 50,
    borderRadius: 25,
    marginRight: 12,
  },
  requestName: {
    fontSize: 16,
    fontWeight: '600',
  },
  requestDate: {
    fontSize: 14,
    color: '#6c757d',
  },
  requestActions: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  requestButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    marginLeft: 8,
  },
  acceptButton: {
    backgroundColor: '#38b2ac',
  },
  declineButton: {
    backgroundColor: '#e53e3e',
  },
  requestButtonText: {
    color: '#ffffff',
    fontWeight: '600',
  },
});

export default TherapyBuddyScreen;
