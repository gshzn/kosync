FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy build artifacts from local dist directory
ADD ./app/dist/ /usr/share/nginx/app
ADD ./landing-page/dist/ /usr/share/nginx/landing-page

# Expose port
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
