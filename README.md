# mnist-server-grpc

Build image:
```
docker build -t jduarte1/mnist-server-grpc:1.0 .
```

Run server:
```
docker run -t --rm -p 50051:50051 -v "$PWD" jduarte1/mnist-server-grpc:1.0 &
```