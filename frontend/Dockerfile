FROM node:18 as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-slim
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/server.mjs .
COPY --from=build /app/package*.json ./
RUN npm install --production
EXPOSE 8080
ENV PORT=8080
CMD ["node", "server.mjs"]
