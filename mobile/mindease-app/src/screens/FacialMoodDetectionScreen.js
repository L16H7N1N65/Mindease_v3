import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';
import { Camera } from 'react-native-camera';
import * as tf from '@tensorflow/tfjs';
import { bundleResourceIO } from '@tensorflow/tfjs-react-native';
import { useTranslation } from 'react-i18next';

// Import components
import SafeAreaWrapper from '../components/SafeAreaWrapper';
import Header from '../components/Header';
import MoodResult from '../components/MoodResult';
import PrivacyInfo from '../components/PrivacyInfo';

const modelJson = require('../assets/models/facial_expression_model.json');
const modelWeights = require('../assets/models/facial_expression_model.bin');

const FacialMoodDetectionScreen = () => {
  const { t } = useTranslation();
  const [hasPermission, setHasPermission] = React.useState(null);
  const [cameraActive, setCameraActive] = React.useState(false);
  const [model, setModel] = React.useState(null);
  const [detectedMood, setDetectedMood] = React.useState(null);
  const [confidence, setConfidence] = React.useState(null);
  const [secondaryMood, setSecondaryMood] = React.useState(null);
  const [secondaryConfidence, setSecondaryConfidence] = React.useState(null);
  const [processing, setProcessing] = React.useState(false);
  const cameraRef = React.useRef(null);

  // Load TensorFlow model on component mount
  React.useEffect(() => {
    async function loadModel() {
      try {
        await tf.ready();
        const loadedModel = await tf.loadLayersModel(bundleResourceIO(modelJson, modelWeights));
        setModel(loadedModel);
        console.log('Facial expression model loaded successfully');
      } catch (error) {
        console.error('Failed to load model:', error);
      }
    }

    loadModel();
  }, []);

  // Request camera permissions
  React.useEffect(() => {
    (async () => {
      const { status } = await Camera.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
  }, []);

  // Process image and detect mood
  const detectMood = async () => {
    if (cameraRef.current && model) {
      setProcessing(true);
      try {
        // Capture image
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.5,
          base64: true,
          exif: false,
        });

        // Process image with TensorFlow
        const imageTensor = await tf.image.decodeJpeg(tf.util.encodeString(photo.base64, 'base64'), 3);
        const resized = tf.image.resizeBilinear(imageTensor, [48, 48]);
        const grayscale = tf.image.rgbToGrayscale(resized);
        const normalized = grayscale.div(255.0);
        const batched = normalized.expandDims(0);
        
        // Run inference
        const predictions = await model.predict(batched).data();
        
        // Get top two predictions
        const emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral'];
        const topPredictions = Array.from(predictions)
          .map((confidence, index) => ({ emotion: emotions[index], confidence }))
          .sort((a, b) => b.confidence - a.confidence);
        
        // Set results
        setDetectedMood(topPredictions[0].emotion);
        setConfidence(topPredictions[0].confidence);
        setSecondaryMood(topPredictions[1].emotion);
        setSecondaryConfidence(topPredictions[1].confidence);
        
        // Clean up tensors
        tf.dispose([imageTensor, resized, grayscale, normalized, batched]);
      } catch (error) {
        console.error('Error detecting mood:', error);
      } finally {
        setProcessing(false);
      }
    }
  };

  // Toggle camera
  const toggleCamera = () => {
    setCameraActive(!cameraActive);
    if (detectedMood) {
      setDetectedMood(null);
      setConfidence(null);
      setSecondaryMood(null);
      setSecondaryConfidence(null);
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
          mood_type: 'facial',
          mood_value: detectedMood,
          confidence: confidence,
          secondary_mood: secondaryMood,
          secondary_confidence: secondaryConfidence,
          notes: '',
        }),
      });
      
      if (response.ok) {
        alert(t('mood_saved_success'));
        // Reset state
        setDetectedMood(null);
        setConfidence(null);
        setSecondaryMood(null);
        setSecondaryConfidence(null);
        setCameraActive(false);
      } else {
        alert(t('mood_saved_error'));
      }
    } catch (error) {
      console.error('Error saving mood:', error);
      alert(t('mood_saved_error'));
    }
  };

  if (hasPermission === null) {
    return <View style={styles.container}><Text>{t('requesting_camera_permission')}</Text></View>;
  }
  
  if (hasPermission === false) {
    return <View style={styles.container}><Text>{t('camera_permission_denied')}</Text></View>;
  }

  return (
    <SafeAreaWrapper>
      <Header title={t('facial_mood_detection')} />
      
      <View style={styles.container}>
        <Text style={styles.description}>{t('facial_mood_description')}</Text>
        
        {cameraActive ? (
          <View style={styles.cameraContainer}>
            <Camera
              ref={cameraRef}
              style={styles.camera}
              type={Camera.Constants.Type.front}
              ratio="16:9"
            />
            <View style={styles.cameraOverlay}>
              <Text style={styles.privacyNote}>{t('privacy_protected')}</Text>
            </View>
          </View>
        ) : (
          <TouchableOpacity style={styles.cameraPlaceholder} onPress={toggleCamera}>
            <Image 
              source={require('../assets/images/camera-placeholder.png')} 
              style={styles.placeholderImage}
            />
            <Text style={styles.placeholderText}>{t('tap_to_start_camera')}</Text>
          </TouchableOpacity>
        )}
        
        {detectedMood && (
          <MoodResult
            primaryMood={detectedMood}
            primaryConfidence={confidence}
            secondaryMood={secondaryMood}
            secondaryConfidence={secondaryConfidence}
          />
        )}
        
        <View style={styles.buttonContainer}>
          {cameraActive && !processing && (
            <TouchableOpacity style={styles.button} onPress={detectMood} disabled={processing}>
              <Text style={styles.buttonText}>{t('detect_mood')}</Text>
            </TouchableOpacity>
          )}
          
          {cameraActive && processing && (
            <TouchableOpacity style={[styles.button, styles.buttonDisabled]} disabled>
              <Text style={styles.buttonText}>{t('processing')}</Text>
            </TouchableOpacity>
          )}
          
          {!cameraActive && (
            <TouchableOpacity style={styles.button} onPress={toggleCamera}>
              <Text style={styles.buttonText}>{t('start_camera')}</Text>
            </TouchableOpacity>
          )}
          
          {detectedMood && (
            <TouchableOpacity style={[styles.button, styles.saveButton]} onPress={saveMoodDetection}>
              <Text style={styles.buttonText}>{t('save_mood')}</Text>
            </TouchableOpacity>
          )}
        </View>
        
        <PrivacyInfo />
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
  description: {
    fontSize: 16,
    marginBottom: 16,
    color: '#333',
  },
  cameraContainer: {
    width: '100%',
    aspectRatio: 16/9,
    borderRadius: 12,
    overflow: 'hidden',
    marginBottom: 16,
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    padding: 8,
  },
  privacyNote: {
    color: 'white',
    fontSize: 12,
    textAlign: 'center',
  },
  cameraPlaceholder: {
    width: '100%',
    aspectRatio: 16/9,
    backgroundColor: '#e9ecef',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  placeholderImage: {
    width: 64,
    height: 64,
    marginBottom: 8,
  },
  placeholderText: {
    fontSize: 16,
    color: '#6c757d',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginTop: 16,
  },
  button: {
    backgroundColor: '#4361ee',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#a0aec0',
  },
  saveButton: {
    backgroundColor: '#38b2ac',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default FacialMoodDetectionScreen;
