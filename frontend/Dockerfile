FROM node:20-alpine AS build

WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
RUN apk add --no-cache gettext
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/conf.d/default.conf
COPY env.js.template /usr/share/nginx/html/env.js.template
EXPOSE 80
CMD ["/bin/sh", "-c", "envsubst '$VITE_API_URL' < /usr/share/nginx/html/env.js.template > /usr/share/nginx/html/env.js && nginx -g 'daemon off;'"]
