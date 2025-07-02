FROM node:20-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the React Native application
RUN npm run build

# Expose port for development server
EXPOSE 8081

# Start the Metro bundler
CMD ["npm", "start"]
