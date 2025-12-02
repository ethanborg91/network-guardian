# ---- Build Step (React) ----
FROM node:18-alpine AS build

WORKDIR /app

COPY dashboard/package.json dashboard/package-lock.json ./
RUN npm install --legacy-peer-deps

COPY dashboard/ ./
RUN npm run build


# ---- Serve with NGINX ----
FROM nginx:stable-alpine

# Copy built React files
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
