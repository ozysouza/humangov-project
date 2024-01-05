# Utilize o NGINX alpine como imagem base
FROM nginx:alpine

# Remova o arquivo de configuração padrão do NGINX
RUN rm /etc/nginx/conf.d/default.conf

# Copie o arquivo de configuração personalizado
COPY nginx.conf /etc/nginx/conf.d

# Copie os parâmetros de proxy
COPY proxy_params /etc/nginx/proxy_params

# Exponha a porta 80
EXPOSE 80

# Inicie o NGINX
CMD ["nginx", "-g", "daemon off;"]
