import React from 'react';
import { AppRegistry } from 'react-native';
import AppNavigator from './src/AppNavigator';
import { name as appName } from './app.json';
import axios from 'axios';

// Configure axios defaults
axios.defaults.baseURL = 'https://api.mindease.com';
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add request interceptor for authentication
axios.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem('userToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (error) {
      console.error('Error setting auth token:', error);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for handling token expiration
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = await AsyncStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken
          });
          
          if (response.data.token) {
            await AsyncStorage.setItem('userToken', response.data.token);
            axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.token}`;
            return axios(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('Error refreshing token:', refreshError);
        // Navigate to login screen
        // TO DO LATER ...
      }
    }
    
    return Promise.reject(error);
  }
);

const App = () => {
  return <AppNavigator />;
};

AppRegistry.registerComponent(appName, () => App);

export default App;
