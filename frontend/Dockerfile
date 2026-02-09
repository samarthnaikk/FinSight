# Use Node.js 18 alpine image as base
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose port
EXPOSE 5173

# Note: This uses Vite dev server for DEVELOPMENT only.
# For production, build static assets and serve via nginx or similar.
# Run Vite development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
