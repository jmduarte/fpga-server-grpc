# fpga-server-grpc

To set up server (from `prp-gpu-1.t2.ucsd.edu`):
```
source /xilinx/Vivado/2019.2/settings64.sh
source /opt/xilinx/xrt/setup.sh
python3 server.py &
```

To build server from Docker:
```
docker build -t fpga-server-grpc .
```

To run server from Docker:
```
export PORT=50051
./docker_run_xilinx.sh -p ${PORT}:${PORT} -e FPGA_SERVER_PORT=${PORT} -v ${PWD}:/app fpga-server-grpc
```

To run client (from anywhere):
```
python3 client-wait.py
```