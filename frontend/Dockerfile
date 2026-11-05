# --- build the static site ---
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# frontend/.env.production sets an empty VITE_API_URL: the built site calls
# the API on its own origin ("/api/..."), which nginx below proxies
RUN npm run build

# --- serve it ---
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
