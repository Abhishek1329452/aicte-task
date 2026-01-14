### Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
COPY src ./src
COPY index.html ./
RUN npm ci --silent
RUN npm run build

### Serve stage
FROM nginx:stable-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
