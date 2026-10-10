FROM node:22.23.3-alpine3.24 AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
ARG VITE_API_URL=/api
ARG VITE_USE_MOCK=false
ENV VITE_API_URL=${VITE_API_URL} \
    VITE_USE_MOCK=${VITE_USE_MOCK}
RUN npm run build

FROM nginx:1.30.5-alpine3.24

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist/ /usr/share/nginx/html/
RUN mkdir -p /tmp/nginx-client-body /tmp/nginx-proxy-temp \
    /tmp/nginx-fastcgi-temp /tmp/nginx-uwsgi-temp /tmp/nginx-scgi-temp \
    && chown nginx:nginx /tmp/nginx-client-body /tmp/nginx-proxy-temp \
    /tmp/nginx-fastcgi-temp /tmp/nginx-uwsgi-temp /tmp/nginx-scgi-temp

USER nginx
EXPOSE 8080
ENTRYPOINT ["nginx", "-g", "daemon off;"]
