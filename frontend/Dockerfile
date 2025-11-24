FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy project files
COPY . .

# Expose port
EXPOSE 3000

# Set environment to development for hot-reload
ENV NODE_ENV=development

# Start development server
CMD ["npm", "run", "dev"]
