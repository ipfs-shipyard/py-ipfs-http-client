FROM ipfs/go-ipfs:v0.7.0

RUN sed -i 's/exec ipfs "$@"//' /usr/local/bin/start_ipfs
ADD entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
CMD ["ipfs", "daemon", "--migrate=true", "--enable-namesys-pubsub"] 
