FROM node:lts
WORKDIR /react-app
COPY public/ /react-app/public
COPY src/ /react-app/src
COPY package.json /react-app/
COPY tailwind.config.js /react-app/
RUN npm install
RUN npx tailwindcss -i /react-app/public/index.css -o /react-app/public/main.css
CMD ["npm", "start"]