import logging, grpc, time

import numpy as np

import server_tools_pb2
import server_tools_pb2_grpc

import keras
from keras.models import model_from_json

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

    with open('hcal_dense_1.json') as f:
        json_string = f.read()
    model = model_from_json(json_string)
    model.load_weights('hcal_dense_1_weights.h5')

    # Make up some input data:
    data = np.random.rand(max_events,11)*100.
    data = data[:max_events,:]
    expected = model.predict(data)
    data = data.tostring()

    # Pass the data to the server and receive a prediction
    print("Submitting image and waiting")
    start_time=time.time()
    response = stub.StartJobWait(server_tools_pb2.DataMessage(images=data, client_id = client_id, batch_size=32))

    # Find the prediction and print it
    original_array = np.frombuffer(response.prediction).reshape(max_events, 1)
    whole_time = time.time() - start_time
    print("Expected prediction is:", list(expected.reshape(-1)))
    print("Quantized prediction is:", list(original_array.reshape(-1)))
    print("Total time:", whole_time)
    print("Predict time:", response.infer_time)
    print("Fraction of time spent not predicting:", (1 - response.infer_time / whole_time) * 100, '%')
    channel.close()


if __name__ == '__main__':
    logging.basicConfig()
    # Repeat so that you can change the image
    while input('Run? ') == '':
        run(max_events = 16384)
