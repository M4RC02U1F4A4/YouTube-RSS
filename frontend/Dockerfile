FROM node:lts
WORKDIR /react-app-tmp
COPY public/ /react-app-tmp/public
COPY src/ /react-app-tmp/src
COPY package.json /react-app-tmp/
COPY tailwind.config.js /react-app-tmp/
RUN npm install
RUN npx tailwindcss -i /react-app-tmp/public/index.css -o /react-app-tmp/public/main.css
RUN export BUILD_PATH="/react-app" && npm run build
RUN rm -rf /react-app-tmp
WORKDIR /react-app
RUN npm install -g serve
LABEL org.opencontainers.image.source=https://github.com/M4RC02U1F4A4/YouTube-RSS
ENTRYPOINT ["serve"]
CMD ["-l" , "3000"]