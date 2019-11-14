# fpga-server-grpc

To set up server (from `prp-gpu-1.t2.ucsd.edu`):
```
source /xilinx/Vivado/2019.2/settings64.sh
source /opt/xilinx/xrt/setup.sh
python3 server.py &
```

To run client (from anywhere):
```
python3 client-wait.py
```