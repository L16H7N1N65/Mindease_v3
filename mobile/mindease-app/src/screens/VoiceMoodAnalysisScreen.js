import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { Audio } from 'expo-audio';
import * as tf from '@tensorflow/tfjs';
import { bundleResourceIO } from '@tensorflow/tfjs-react-native';
import { useTranslation } from 'react-i18next';

// Import components
import SafeAreaWrapper from '../components/SafeAreaWrapper';
import Header from '../components/Header';
import AudioWaveform from '../components/AudioWaveform';
import MoodResult from '../components/MoodResult';
import PrivacyInfo from '../components/PrivacyInfo';

const modelJson = require('../assets/models/voice_sentiment_model.json');
const modelWeights = require('../assets/models/voice_sentiment_model.bin');

const VoiceMoodAnalysisScreen = () => {
  const { t } = useTranslation();
  const [hasPermission, setHasPermission] = useState(null);
  const [recording, setRecording] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [audioUri, setAudioUri] = useState(null);
  const [model, setModel] = useState(null);
  const [detectedMood, setDetectedMood] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [processing, setProcessing] = useState(false);
  const durationTimer = useRef(null);

  // Load TensorFlow model on component mount
  useEffect(() => {
    async function loadModel() {
      try {
        await tf.ready();
        const loadedModel = await tf.loadLayersModel(bundleResourceIO(modelJson, modelWeights));
        setModel(loadedModel);
        console.log('Voice sentiment model loaded successfully');
      } catch (error) {
        console.error('Failed to load model:', error);
      }
    }

    loadModel();
  }, []);

  // Request audio permissions
  useEffect(() => {
    (async () => {
      const { status } = await Audio.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (durationTimer.current) {
        clearInterval(durationTimer.current);
      }
    };
  }, []);

  // Start recording audio
  const startRecording = async () => {
    try {
      if (hasPermission) {
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
        });
        
        const { recording } = await Audio.Recording.createAsync(
          Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
        );
        
        setRecording(recording);
        setIsRecording(true);
        setRecordingDuration(0);
        
        // Start timer to track recording duration
        durationTimer.current = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
      }
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  // Stop recording audio
  const stopRecording = async () => {
    try {
      if (!recording) return;
      
      // Stop timer
      if (durationTimer.current) {
        clearInterval(durationTimer.current);
        durationTimer.current = null;
      }
      
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setAudioUri(uri);
      setRecording(null);
      
      // Process the audio
      analyzeAudio(uri);
    } catch (error) {
      console.error('Failed to stop recording:', error);
    }
  };

  // Analyze audio with TensorFlow model
  const analyzeAudio = async (uri) => {
    if (!model || !uri) return;
    
    setProcessing(true);
    try {
      // In a real implementation, we would:
      // 1. Convert audio to the right format (e.g., extract MFCC features)
      // 2. Process with TensorFlow
      // 3. Get sentiment prediction
      
      // For this example, we'll simulate processing
      setTimeout(() => {
        // Simulate model prediction
        const emotions = ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised'];
        const randomIndex = Math.floor(Math.random() * emotions.length);
        const randomConfidence = 0.5 + (Math.random() * 0.5); // Between 0.5 and 1.0
        
        setDetectedMood(emotions[randomIndex]);
        setConfidence(randomConfidence);
        setProcessing(false);
      }, 2000);
    } catch (error) {
      console.error('Error analyzing audio:', error);
      setProcessing(false);
    }
  };

  // Save mood detection to backend
  const saveMoodDetection = async () => {
    if (!detectedMood) return;
    
    try {
      const response = await fetch('https://api.mindease.app/mood/entries', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${userToken}`, // This would come from auth context
        },
        body: JSON.stringify({
          mood_type: 'voice',
          mood_value: detectedMood,
          confidence: confidence,
          audio_duration: recordingDuration,
          notes: '',
        }),
      });
      
      if (response.ok) {
        alert(t('mood_saved_success'));
        // Reset state
        setDetectedMood(null);
        setConfidence(null);
        setAudioUri(null);
        setRecordingDuration(0);
      } else {
        alert(t('mood_saved_error'));
      }
    } catch (error) {
      console.error('Error saving mood:', error);
      alert(t('mood_saved_error'));
    }
  };

  // Format seconds to MM:SS
  const formatDuration = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>{t('requesting_audio_permission')}</Text></View>;
  }
  
  if (hasPermission === false) {
    return <View style={styles.container}><Text>{t('audio_permission_denied')}</Text></View>;
  }

  return (
    <SafeAreaWrapper>
      <Header title={t('voice_mood_analysis')} />
      
      <ScrollView style={styles.container}>
        <Text style={styles.description}>{t('voice_mood_description')}</Text>
        
        <View style={styles.audioContainer}>
          <AudioWaveform 
            isRecording={isRecording}
            audioUri={audioUri}
          />
          
          <Text style={styles.durationText}>
            {formatDuration(recordingDuration)}
          </Text>
        </View>
        
        <View style={styles.buttonContainer}>
          {!isRecording ? (
            <TouchableOpacity 
              style={styles.recordButton} 
              onPress={startRecording}
              disabled={processing}
            >
              <Text style={styles.buttonText}>{t('start_recording')}</Text>
            </TouchableOpacity>
          ) : (
            <TouchableOpacity 
              style={[styles.recordButton, styles.stopButton]} 
              onPress={stopRecording}
            >
              <Text style={styles.buttonText}>{t('stop_recording')}</Text>
            </TouchableOpacity>
          )}
        </View>
        
        {processing && (
          <View style={styles.processingContainer}>
            <ActivityIndicator size="large" color="#4361ee" />
            <Text style={styles.processingText}>{t('analyzing_voice')}</Text>
          </View>
        )}
        
        {detectedMood && (
          <View style={styles.resultContainer}>
            <Text style={styles.resultTitle}>{t('analysis_result')}</Text>
            <View style={styles.moodCard}>
              <Text style={styles.moodLabel}>{t('detected_mood')}</Text>
              <Text style={styles.moodValue}>{t(`mood_${detectedMood}`)}</Text>
              <View style={styles.confidenceBar}>
                <View 
                  style={[
                    styles.confidenceFill, 
                    { width: `${confidence * 100}%` }
                  ]} 
                />
              </View>
              <Text style={styles.confidenceText}>
                {t('confidence')}: {Math.round(confidence * 100)}%
              </Text>
            </View>
            
            <TouchableOpacity 
              style={styles.saveButton}
              onPress={saveMoodDetection}
            >
              <Text style={styles.buttonText}>{t('save_mood')}</Text>
            </TouchableOpacity>
          </View>
        )}
        
        <PrivacyInfo />
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
  audioContainer: {
    width: '100%',
    height: 200,
    backgroundColor: '#e9ecef',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
    padding: 16,
  },
  durationText: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 16,
  },
  buttonContainer: {
    alignItems: 'center',
    marginVertical: 16,
  },
  recordButton: {
    backgroundColor: '#4361ee',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 30,
    minWidth: 200,
    alignItems: 'center',
  },
  stopButton: {
    backgroundColor: '#e63946',
  },
  buttonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  processingContainer: {
    alignItems: 'center',
    marginVertical: 16,
  },
  processingText: {
    marginTop: 8,
    fontSize: 16,
    color: '#4361ee',
  },
  resultContainer: {
    marginVertical: 16,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  moodCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
    marginBottom: 16,
  },
  moodLabel: {
    fontSize: 16,
    color: '#6c757d',
    marginBottom: 4,
  },
  moodValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#212529',
    marginBottom: 12,
  },
  confidenceBar: {
    height: 8,
    backgroundColor: '#e9ecef',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 8,
  },
  confidenceFill: {
    height: '100%',
    backgroundColor: '#4361ee',
    borderRadius: 4,
  },
  confidenceText: {
    fontSize: 14,
    color: '#6c757d',
  },
  saveButton: {
    backgroundColor: '#38b2ac',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
});

export default VoiceMoodAnalysisScreen;
