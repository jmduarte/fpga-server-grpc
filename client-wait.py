import logging, grpc, time

import numpy as np

import server_tools_pb2
import server_tools_pb2_grpc

PORT = '50051'
f = open("IP.txt")
IP = f.read()
if IP[-1] == '\n':
    IP = IP[:-1]
f.close()

def run(max_events=32):
    # Get a handle to the server
    channel = grpc.insecure_channel(IP+':'+PORT)
    stub = server_tools_pb2_grpc.MnistServerStub(channel)

    # Get a client ID which you need to talk to the server
    try:
        response = stub.RequestClientID(server_tools_pb2.NullParam())
    except:
        print("Connection to the server could not be established. Press enter to try again.")
        return
    client_id = response.new_id

    # Load the image from image.bmp
    data = np.loadtxt('tb_input_features.dat')
    data = data[:max_events,:]
    data = data.tostring()

    # Pass the data to the server and receive a prediction
    print("Submitting image and waiting")
    start_time=time.time()
    response = stub.StartJobWait(server_tools_pb2.DataMessage(images=data, client_id = client_id, batch_size=32))

    # Find the most likely prediction and print it
    original_array = np.frombuffer(response.prediction).reshape(max_events, 1)
    whole_time = time.time() - start_time
    result = list(original_array[0])
    print("Prediction is:", result.index(max(result)))
    print("Total time:", whole_time)
    print("Predict time:", response.infer_time)
    print("Fraction of time spent not predicting:", (1 - response.infer_time / whole_time) * 100, '%')
    channel.close()


if __name__ == '__main__':
    logging.basicConfig()
    # Repeat so that you can change the image
    while input('Run? ') == '':
        run(max_events = 32)
