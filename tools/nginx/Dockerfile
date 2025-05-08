FROM nginx:1.19.10

RUN apt-get update -y && apt-get install -y apache2-utils
RUN mkdir /secrets \
 && cd /secrets \
 && htpasswd -cb htpasswd TheUser ThePassword

ADD entrypoint.sh /usr/local/sbin/entrypoint
ADD default.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
ENTRYPOINT ["/usr/local/sbin/entrypoint"]
