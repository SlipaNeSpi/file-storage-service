# Стадия сборки
FROM node:22-alpine AS build
WORKDIR /app

# Копируем файлы зависимостей
COPY package*.json ./
RUN npm ci

# Копируем исходники
COPY . .

# Собираем проект (результат в папке dist)
RUN npm run build

# Стадия production
FROM nginx:alpine

# Копируем собранную статику
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]