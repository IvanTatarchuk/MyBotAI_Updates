FROM node:20-alpine
WORKDIR /app

COPY package.json ./
# If you later add lockfile, add it too for reproducible installs
# COPY package-lock.json ./

RUN npm install --silent

COPY . .
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

