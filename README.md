## Build Docker Image

```sh
docker build -t algotrader .
```

## Save and compress image to gzip file

```sh
docker save algotrader | gzip > algotrader.tar.gz
```

## Transfer file to server using SCP

```sh
scp -i algotrader.pem algotrader.tar.gz ubuntu@example.com:/home/ubuntu/
```

## Decompress and load image

```sh
gunzip -c algotrader.tar.gz | docker load
```

## Create Docker Container

#### Note

Make sure to set set restart policy to "always" and map host port 80 to docker post 800 when creating the container

```sh
docker run -d -p 80:8000 --name algotrader --restart always algotrader
```
