import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  SafeAreaView,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { LineChart } from 'react-native-chart-kit';
import { Dimensions } from 'react-native';

const screenWidth = Dimensions.get('window').width;

const DashboardScreen = ({ navigation }) => {
  const [userData, setUserData] = useState(null);
  const [moodData, setMoodData] = useState(null);
  const [therapySessions, setTherapySessions] = useState([]);
  const [buddies, setBuddies] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [currentMood, setCurrentMood] = useState('Calm');
  const [moodChange, setMoodChange] = useState('+15%');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setRefreshing(true);
    try {
      const token = await AsyncStorage.getItem('userToken');
      const userId = await AsyncStorage.getItem('userId');
      
      if (!token || !userId) {
        navigation.navigate('Login');
        return;
      }

      const headers = {
        Authorization: `Bearer ${token}`,
      };

      // Fetch user data
      const userResponse = await axios.get(`/api/v1/users/${userId}`, { headers });
      setUserData(userResponse.data);

      // Fetch mood data
      const moodResponse = await axios.get(`/api/v1/mood/user/${userId}`, { headers });
      setMoodData(moodResponse.data);

      // Fetch therapy sessions
      const therapyResponse = await axios.get(`/api/v1/therapy/sessions/user/${userId}`, { headers });
      setTherapySessions(therapyResponse.data.slice(0, 3)); // Get latest 3 sessions

      // Fetch buddies
      const buddiesResponse = await axios.get(`/api/v1/buddies/user/${userId}`, { headers });
      setBuddies(buddiesResponse.data);

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  // Mock data for chart
  const moodChartData = {
    labels: ['Mar 10', 'Mar 15', 'Mar 20', 'Mar 25', 'Mar 30', 'Apr 5'],
    datasets: [
      {
        data: [65, 45, 70, 75, 60, 80],
        color: (opacity = 1) => `rgba(74, 111, 255, ${opacity})`,
        strokeWidth: 2,
      },
    ],
  };

  const chartConfig = {
    backgroundGradientFrom: '#ffffff',
    backgroundGradientTo: '#ffffff',
    decimalPlaces: 0,
    color: (opacity = 1) => `rgba(74, 111, 255, ${opacity})`,
    labelColor: (opacity = 1) => `rgba(102, 102, 102, ${opacity})`,
    style: {
      borderRadius: 16,
    },
    propsForDots: {
      r: '6',
      strokeWidth: '2',
      stroke: '#4A6FFF',
    },
  };

  const renderCard = (title, value, subtitle, icon, onPress) => (
    <TouchableOpacity style={styles.card} onPress={onPress}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{title}</Text>
        <Image source={icon} style={styles.cardIcon} />
      </View>
      <View style={styles.cardContent}>
        <Text style={styles.cardValue}>{value}</Text>
        {subtitle && <Text style={styles.cardSubtitle}>{subtitle}</Text>}
      </View>
    </TouchableOpacity>
  );

  const renderSessionItem = (session) => (
    <TouchableOpacity 
      key={session.id} 
      style={styles.sessionItem}
      onPress={() => navigation.navigate('TherapyScreen', { sessionId: session.id })}
    >
      <View>
        <Text style={styles.sessionTitle}>{session.title}</Text>
        <Text style={styles.sessionDate}>
          {new Date(session.created_at).toLocaleDateString()} • {session.duration} minutes
        </Text>
        <View style={styles.sessionTagContainer}>
          <Text style={styles.sessionTag}>{session.session_type}</Text>
        </View>
      </View>
      <Text style={styles.viewText}>View</Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hello, {userData?.first_name || 'there'}!</Text>
          <Text style={styles.subGreeting}>Welcome to your wellness dashboard</Text>
        </View>
        <TouchableOpacity 
          style={styles.profileButton}
          onPress={() => navigation.navigate('Profile')}
        >
          <Image 
            source={require('../assets/profile-placeholder.png')} 
            style={styles.profileImage} 
          />
        </TouchableOpacity>
      </View>

      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={fetchDashboardData} />
        }
      >
        <View style={styles.cardsContainer}>
          {renderCard(
            'Current Mood',
            currentMood,
            moodChange,
            require('../assets/mood-icon.png'),
            () => navigation.navigate('MoodTrackerScreen')
          )}
          
          {renderCard(
            'Therapy Sessions',
            therapySessions.length || '0',
            'Last session: 2 days ago',
            require('../assets/therapy-icon.png'),
            () => navigation.navigate('TherapyScreen')
          )}
          
          {renderCard(
            'Buddy System',
            buddies.length || '0',
            buddies.length > 0 ? '1 new message' : 'Find a buddy',
            require('../assets/buddy-icon.png'),
            () => navigation.navigate('TherapyBuddyScreen')
          )}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Mood Over Time</Text>
          <View style={styles.chartContainer}>
            <LineChart
              data={moodChartData}
              width={screenWidth - 40}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </View>
        </View>

        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Therapy Sessions</Text>
            <TouchableOpacity onPress={() => navigation.navigate('TherapyScreen')}>
              <Text style={styles.seeAllText}>See All</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.sessionsList}>
            {therapySessions.length > 0 ? (
              therapySessions.map(session => renderSessionItem(session))
            ) : (
              <View style={styles.emptyState}>
                <Text style={styles.emptyStateText}>No therapy sessions yet</Text>
                <TouchableOpacity 
                  style={styles.startButton}
                  onPress={() => navigation.navigate('TherapyScreen')}
                >
                  <Text style={styles.startButtonText}>Start Your First Session</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI-Generated Insights</Text>
          <View style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <Image 
                source={require('../assets/insight-icon.png')} 
                style={styles.insightIcon} 
              />
              <Text style={styles.insightTitle}>Sleep Pattern Impact</Text>
            </View>
            <Text style={styles.insightText}>
              Your mood tends to improve when you get 7+ hours of sleep. Consider maintaining a consistent sleep schedule to stabilize your emotional wellbeing.
            </Text>
          </View>
          
          <View style={styles.insightCard}>
            <View style={styles.insightHeader}>
              <Image 
                source={require('../assets/insight-icon.png')} 
                style={styles.insightIcon} 
              />
              <Text style={styles.insightTitle}>Social Connection</Text>
            </View>
            <Text style={styles.insightText}>
              Your mood scores are consistently higher on days when you engage with your therapy buddy. Consider scheduling regular check-ins.
            </Text>
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Your Wellness Plan</Text>
          <View style={styles.planItem}>
            <View style={styles.planIconContainer}>
              <Image 
                source={require('../assets/mindfulness-icon.png')} 
                style={styles.planIcon} 
              />
            </View>
            <View style={styles.planContent}>
              <Text style={styles.planTitle}>Daily Mindfulness Practice</Text>
              <Text style={styles.planDescription}>5-10 minutes of guided meditation each morning</Text>
              <TouchableOpacity style={styles.planButton}>
                <Text style={styles.planButtonText}>Start Practice</Text>
              </TouchableOpacity>
            </View>
          </View>
          
          <View style={styles.planItem}>
            <View style={styles.planIconContainer}>
              <Image 
                source={require('../assets/therapy-icon.png')} 
                style={styles.planIcon} 
              />
            </View>
            <View style={styles.planContent}>
              <Text style={styles.planTitle}>Weekly CBT Session</Text>
              <Text style={styles.planDescription}>Schedule your next therapy session for this week</Text>
              <TouchableOpacity 
                style={styles.planButton}
                onPress={() => navigation.navigate('TherapyScreen')}
              >
                <Text style={styles.planButtonText}>Schedule Session</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F7FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 15,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E1E5EA',
  },
  greeting: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#333333',
  },
  subGreeting: {
    fontSize: 14,
    color: '#666666',
    marginTop: 2,
  },
  profileButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: '#4A6FFF',
  },
  profileImage: {
    width: '100%',
    height: '100%',
  },
  scrollView: {
    flex: 1,
  },
  cardsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    padding: 20,
  },
  card: {
    width: '31%',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 15,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666666',
  },
  cardIcon: {
    width: 16,
    height: 16,
    tintColor: '#4A6FFF',
  },
  cardContent: {
    marginTop: 5,
  },
  cardValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#666666',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginHorizontal: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333333',
    marginBottom: 15,
  },
  seeAllText: {
    fontSize: 14,
    color: '#4A6FFF',
    fontWeight: '500',
  },
  chartContainer: {
    alignItems: 'center',
    marginTop: 10,
  },
  chart: {
    borderRadius: 12,
    paddingRight: 20,
  },
  sessionsList: {
    marginTop: 5,
  },
  sessionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E5EA',
  },
  sessionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 4,
  },
  sessionDate: {
    fontSize: 12,
    color: '#666666',
    marginBottom: 6,
  },
  sessionTagContainer: {
    flexDirection: 'row',
  },
  sessionTag: {
    fontSize: 10,
    color: '#4A6FFF',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    overflow: 'hidden',
  },
  viewText: {
    fontSize: 14,
    color: '#4A6FFF',
    fontWeight: '500',
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 20,
  },
  emptyStateText: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 15,
  },
  startButton: {
    backgroundColor: '#4A6FFF',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  startButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  insightCard: {
    backgroundColor: '#F5F7FA',
    borderRadius: 8,
    padding: 15,
    marginBottom: 12,
  },
  insightHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightIcon: {
    width: 20,
    height: 20,
    marginRight: 8,
    tintColor: '#4A6FFF',
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
  },
  insightText: {
    fontSize: 14,
    color: '#666666',
    lineHeight: 20,
  },
  planItem: {
    flexDirection: 'row',
    marginBottom: 15,
  },
  planIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  planIcon: {
    width: 20,
    height: 20,
    tintColor: '#4A6FFF',
  },
  planContent: {
    flex: 1,
  },
  planTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 4,
  },
  planDescription: {
    fontSize: 14,
    color: '#666666',
    marginBottom: 10,
  },
  planButton: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#4A6FFF',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    alignSelf: 'flex-start',
  },
  planButtonText: {
    color: '#4A6FFF',
    fontSize: 12,
    fontWeight: '600',
  },
});

export default DashboardScreen;
