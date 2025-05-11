FROM press-service-framework
RUN apt install -y --no-install-recommends imagemagick
RUN apt install -y --no-install-recommends jpegoptim
RUN rm -rf /var/lib/apt/lists/*
COPY ./bin/service /app/bin/service
