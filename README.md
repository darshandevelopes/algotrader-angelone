## Syntax for SCP

```sh
scp -i abc.pem my-image.tar username@example.com:/home/username/
```

## Build Docker Image

```sh
docker build -t algotrader .
```

## Export Docker image to zip file

```sh
docker save algotrader | zip > algotrader.zip
```

## Create Docker Container

#### Note

Make sure to set set restart policy to "always" and map host port 80 to docker post 800 when creating the container

```sh
docker run -d -p 80:8000 --name algotrader --restart always algotrader
```
