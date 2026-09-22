FROM node:22-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ARG CONTENT_AS_OF
ARG CI_COMMIT_SHA=local

ENV CONTENT_AS_OF=${CONTENT_AS_OF}
ENV CI_COMMIT_SHA=${CI_COMMIT_SHA}

RUN npm run build


FROM nginx:1.27-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build /app/build /usr/share/nginx/html

RUN chown -R nginx:nginx \
    /usr/share/nginx/html \
    /var/cache/nginx \
    /var/run

USER nginx

EXPOSE 8080

HEALTHCHECK \
  --interval=30s \
  --timeout=3s \
  --start-period=5s \
  --retries=3 \
  CMD wget -qO- http://localhost:8080/health || exit 1
