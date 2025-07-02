import React, { useState, useEffect, useContext } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Image } from 'react-native';
import { LineChart } from 'react-native-chart-kit';
import { useTranslation } from 'react-i18next';
import { AuthContext } from '../contexts/AuthContext';

// Import components
import SafeAreaWrapper from '../components/SafeAreaWrapper';
import Header from '../components/Header';
import MoodCard from '../components/MoodCard';
import EmotionPicker from '../components/EmotionPicker';

const MoodTrackerScreen = () => {
  const { t } = useTranslation();
  const { userToken } = useContext(AuthContext);
  const [moodEntries, setMoodEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('week');
  const [currentMood, setCurrentMood] = useState(null);
  const [moodNote, setMoodNote] = useState('');

  // Fetch mood entries from API
  useEffect(() => {
    fetchMoodEntries();
  }, [selectedPeriod]);

  const fetchMoodEntries = async () => {
    if (!userToken) return;
    
    setLoading(true);
    try {
      const response = await fetch(`https://api.mindease.app/mood/entries?period=${selectedPeriod}`, {
        headers: {
          'Authorization': `Bearer ${userToken}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setMoodEntries(data.entries);
      } else {
        console.error('Failed to fetch mood entries');
      }
    } catch (error) {
      console.error('Error fetching mood entries:', error);
    } finally {
      setLoading(false);
    }
  };

  // Save manual mood entry
  const saveMoodEntry = async () => {
    if (!currentMood) return;
    
    try {
      const response = await fetch('https://api.mindease.app/mood/entries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`,
        },
        body: JSON.stringify({
          mood_type: 'manual',
          mood_value: currentMood,
          confidence: 1.0, // Manual entries have 100% confidence
          notes: moodNote,
        }),
      });
      
      if (response.ok) {
        alert(t('mood_saved_success'));
        setCurrentMood(null);
        setMoodNote('');
        fetchMoodEntries(); // Refresh the list
      } else {
        alert(t('mood_saved_error'));
      }
    } catch (error) {
      console.error('Error saving mood:', error);
      alert(t('mood_saved_error'));
    }
  };

  // Prepare chart data
  const getChartData = () => {
    // Default empty data
    const defaultData = {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [
        {
          data: [0, 0, 0, 0, 0, 0, 0],
          color: (opacity = 1) => `rgba(67, 97, 238, ${opacity})`,
          strokeWidth: 2,
        },
      ],
    };
    
    if (moodEntries.length === 0) return defaultData;
    
    // Map mood values to numbers (0-6)
    const moodValues = {
      'angry': 0,
      'sad': 1,
      'fearful': 2,
      'neutral': 3,
      'calm': 4,
      'happy': 5,
      'excited': 6,
    };
    
    // Process entries based on selected period
    let labels = [];
    let data = [];
    
    if (selectedPeriod === 'week') {
      labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
      // Group entries by day and calculate average mood
      // This is simplified - in a real app we'd do proper date processing
      const days = [0, 1, 2, 3, 4, 5, 6];
      data = days.map(day => {
        const dayEntries = moodEntries.filter(entry => new Date(entry.created_at).getDay() === day);
        if (dayEntries.length === 0) return 3; // Default to neutral
        
        const sum = dayEntries.reduce((acc, entry) => acc + (moodValues[entry.mood_value] || 3), 0);
        return sum / dayEntries.length;
      });
    } else if (selectedPeriod === 'month') {
      // For month view, we'd group by week
      labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
      // Simplified implementation
      data = [3, 4, 3.5, 4.2]; // Example data
    } else if (selectedPeriod === 'year') {
      // For year view, we'd group by month
      labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      // Simplified implementation
      data = [3, 3.2, 3.5, 4, 4.2, 4.5, 4.2, 4, 3.8, 3.5, 3.8, 4]; // Example data
    }
    
    return {
      labels,
      datasets: [
        {
          data,
          color: (opacity = 1) => `rgba(67, 97, 238, ${opacity})`,
          strokeWidth: 2,
        },
      ],
    };
  };

  return (
    <SafeAreaWrapper>
      <Header title={t('mood_tracker')} />
      
      <ScrollView style={styles.container}>
        <Text style={styles.description}>{t('mood_tracker_description')}</Text>
        
        {/* Period selector */}
        <View style={styles.periodSelector}>
          <TouchableOpacity
            style={[styles.periodButton, selectedPeriod === 'week' && styles.periodButtonActive]}
            onPress={() => setSelectedPeriod('week')}
          >
            <Text style={[styles.periodButtonText, selectedPeriod === 'week' && styles.periodButtonTextActive]}>
              {t('week')}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.periodButton, selectedPeriod === 'month' && styles.periodButtonActive]}
            onPress={() => setSelectedPeriod('month')}
          >
            <Text style={[styles.periodButtonText, selectedPeriod === 'month' && styles.periodButtonTextActive]}>
              {t('month')}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.periodButton, selectedPeriod === 'year' && styles.periodButtonActive]}
            onPress={() => setSelectedPeriod('year')}
          >
            <Text style={[styles.periodButtonText, selectedPeriod === 'year' && styles.periodButtonTextActive]}>
              {t('year')}
            </Text>
          </TouchableOpacity>
        </View>
        
        {/* Mood chart */}
        <View style={styles.chartContainer}>
          <Text style={styles.chartTitle}>{t('mood_trends')}</Text>
          <LineChart
            data={getChartData()}
            width={styles.chartContainer.width || 350}
            height={220}
            chartConfig={{
              backgroundColor: '#ffffff',
              backgroundGradientFrom: '#ffffff',
              backgroundGradientTo: '#ffffff',
              decimalPlaces: 1,
              color: (opacity = 1) => `rgba(67, 97, 238, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
              style: {
                borderRadius: 16,
              },
              propsForDots: {
                r: '6',
                strokeWidth: '2',
                stroke: '#4361ee',
              },
            }}
            bezier
            style={styles.chart}
          />
          <View style={styles.moodLegend}>
            <Text style={styles.legendItem}>0 = {t('mood_angry')}</Text>
            <Text style={styles.legendItem}>3 = {t('mood_neutral')}</Text>
            <Text style={styles.legendItem}>6 = {t('mood_excited')}</Text>
          </View>
        </View>
        
        {/* Record current mood */}
        <View style={styles.recordMoodSection}>
          <Text style={styles.sectionTitle}>{t('record_current_mood')}</Text>
          <EmotionPicker
            selectedEmotion={currentMood}
            onSelectEmotion={setCurrentMood}
          />
          
          {currentMood && (
            <TouchableOpacity 
              style={styles.saveButton}
              onPress={saveMoodEntry}
            >
              <Text style={styles.buttonText}>{t('save_mood')}</Text>
            </TouchableOpacity>
          )}
        </View>
        
        {/* Recent entries */}
        <View style={styles.recentEntriesSection}>
          <Text style={styles.sectionTitle}>{t('recent_entries')}</Text>
          
          {loading ? (
            <Text style={styles.loadingText}>{t('loading')}</Text>
          ) : moodEntries.length === 0 ? (
            <Text style={styles.emptyText}>{t('no_mood_entries')}</Text>
          ) : (
            moodEntries.slice(0, 5).map((entry, index) => (
              <MoodCard
                key={index}
                mood={entry.mood_value}
                date={new Date(entry.created_at)}
                source={entry.mood_type}
                notes={entry.notes}
              />
            ))
          )}
          
          {moodEntries.length > 0 && (
            <TouchableOpacity style={styles.viewAllButton}>
              <Text style={styles.viewAllText}>{t('view_all_entries')}</Text>
            </TouchableOpacity>
          )}
        </View>
        
        {/* Insights */}
        <View style={styles.insightsSection}>
          <Text style={styles.sectionTitle}>{t('mood_insights')}</Text>
          <View style={styles.insightCard}>
            <Image 
              source={require('../assets/images/insights-icon.png')} 
              style={styles.insightIcon}
            />
            <Text style={styles.insightText}>
              {t('mood_insight_example')}
            </Text>
          </View>
        </View>
      </ScrollView>
    </SafeAreaWrapper>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
    backgroundColor: '#f8f9fa',
  },
  description: {
    fontSize: 16,
    marginBottom: 16,
    color: '#333',
  },
  periodSelector: {
    flexDirection: 'row',
    marginBottom: 16,
    backgroundColor: '#e9ecef',
    borderRadius: 8,
    padding: 4,
  },
  periodButton: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 6,
  },
  periodButtonActive: {
    backgroundColor: '#4361ee',
  },
  periodButtonText: {
    fontSize: 14,
    color: '#495057',
  },
  periodButtonTextActive: {
    color: '#ffffff',
    fontWeight: '600',
  },
  chartContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    width: '100%',
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  chart: {
    borderRadius: 12,
    marginVertical: 8,
  },
  moodLegend: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  legendItem: {
    fontSize: 12,
    color: '#6c757d',
  },
  recordMoodSection: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  saveButton: {
    backgroundColor: '#38b2ac',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  recentEntriesSection: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  loadingText: {
    textAlign: 'center',
    padding: 16,
    color: '#6c757d',
  },
  emptyText: {
    textAlign: 'center',
    padding: 16,
    color: '#6c757d',
  },
  viewAllButton: {
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  viewAllText: {
    color: '#4361ee',
    fontSize: 16,
    fontWeight: '500',
  },
  insightsSection: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  insightCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    padding: 12,
  },
  insightIcon: {
    width: 40,
    height: 40,
    marginRight: 12,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: '#495057',
  },
});

export default MoodTrackerScreen;
