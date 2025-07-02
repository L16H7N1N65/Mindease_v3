import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Image } from 'react-native';

// Auth Screens
import LoginScreen from './screens/LoginScreen';
import RegisterScreen from './screens/RegisterScreen';

// Main Screens
import DashboardScreen from './screens/DashboardScreen';
import TherapyScreen from './screens/TherapyScreen';
import MoodTrackerScreen from './screens/MoodTrackerScreen';
import TherapyBuddyScreen from './screens/TherapyBuddyScreen';
import FacialMoodDetectionScreen from './screens/FacialMoodDetectionScreen';
import VoiceMoodAnalysisScreen from './screens/VoiceMoodAnalysisScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

const MainTabs = () => {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconSource;

          if (route.name === 'Dashboard') {
            iconSource = require('./assets/dashboard-icon.png');
          } else if (route.name === 'Therapy') {
            iconSource = require('./assets/therapy-icon.png');
          } else if (route.name === 'Mood') {
            iconSource = require('./assets/mood-icon.png');
          } else if (route.name === 'Buddies') {
            iconSource = require('./assets/buddy-icon.png');
          }

          return (
            <Image
              source={iconSource}
              style={{
                width: size,
                height: size,
                tintColor: color,
              }}
            />
          );
        },
        tabBarActiveTintColor: '#4A6FFF',
        tabBarInactiveTintColor: '#666666',
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: '500',
        },
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#E1E5EA',
          paddingTop: 5,
          paddingBottom: 5,
          height: 60,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Therapy" component={TherapyScreen} />
      <Tab.Screen name="Mood" component={MoodTrackerScreen} />
      <Tab.Screen name="Buddies" component={TherapyBuddyScreen} />
    </Tab.Navigator>
  );
};

const MoodStack = createStackNavigator();

const MoodNavigator = () => {
  return (
    <MoodStack.Navigator screenOptions={{ headerShown: false }}>
      <MoodStack.Screen name="MoodTracker" component={MoodTrackerScreen} />
      <MoodStack.Screen name="FacialMoodDetection" component={FacialMoodDetectionScreen} />
      <MoodStack.Screen name="VoiceMoodAnalysis" component={VoiceMoodAnalysisScreen} />
    </MoodStack.Navigator>
  );
};

const AppNavigator = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Login" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="Register" component={RegisterScreen} />
        <Stack.Screen name="Main" component={MainTabs} />
        <Stack.Screen name="MoodNavigator" component={MoodNavigator} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigator;
