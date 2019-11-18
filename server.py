# Copyright 2015 gRPC authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from concurrent import futures
from optparse import OptionParser

import logging, grpc, time
import numpy as np
import os
import ml_functions as ml
import threading

import server_tools_pb2
import server_tools_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

global processes, max_id, results, max_client_ids, max_client_id, new_client_permitted, times
processes = {}
max_client_ids = {}
max_client_id = 0
max_id = 0
new_client_permitted = True
results = {}
times = {}


def verify_request(request):
    return (request.client_id in max_client_ids) and request.batch_size > 0

class MnistServer(server_tools_pb2_grpc.MnistServerServicer):

    def StartJobWait(self, request, context):
        if not verify_request(request):
            return server_tools_pb2.PredictionMessage(complete=False, prediction=b'', error='Invalid data package', infer_time=0)
        data = np.frombuffer(request.images)
        data = data.reshape(-1, 11)
        prediction, predict_time = ml.predict(data, request.batch_size)
        return server_tools_pb2.PredictionMessage(complete=True, prediction=prediction.tostring(), error='', infer_time=predict_time)

    def RequestClientID(self, request, context):
        global max_client_id, new_client_permitted, max_client_ids
        while not new_client_permitted:
            pass

        new_client_permitted = False
        client_id = str(max_client_id)
        max_client_id += 1
        new_client_permitted = True

        max_client_ids[client_id] = 0
        return server_tools_pb2.IDMessage(new_id=client_id, error = '')

    def StartJobNoWait(self, request, context):
        if not verify_request(request):
            return server_tools_pb2.PredictionMessage(complete=False, prediction=b'', error='Invalid data package', infer_time=0)

        global processes, results, max_client_ids
        if request.client_id not in max_client_ids:
            return server_tools_pb2.IDMessage(new_id=None, error = "The ID "+str(request.client_id)+" is not a valid client ID")
        
        data = np.frombuffer(request.images)
        data = data.reshape(-1, 11)

        job_id = request.client_id + '-' + str(max_client_ids[request.client_id])
        max_client_ids[request.client_id] += 1

        results[job_id] = None
        processes[job_id] = threading.Thread(target=ml.predict, args=(data, request.batch_size, results, times, job_id))
        processes[job_id].start()
        return server_tools_pb2.IDMessage(new_id=job_id, error='')
    
    def ProbeJob(self, request, context):
        global processes, results
        if request.new_id not in processes:
            return server_tools_pb2.PredictionMessage(complete=False, prediction=None, 
                error = "The ID "+str(request.new_id)+" is not a valid job ID")
        if results[request.new_id] is None:
            a = results[request.new_id]
            return server_tools_pb2.PredictionMessage(complete=False, prediction=None)
        else:
            prediction = results[request.new_id].tostring()
            del processes[request.new_id]
            del results[request.new_id]
            return server_tools_pb2.PredictionMessage(complete=True, prediction=prediction, error='', infer_time=times[request.new_id])


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server_tools_pb2_grpc.add_MnistServerServicer_to_server(MnistServer(), server)
    server.add_insecure_port('[::]:'+PORT)
    server.start()
    print(f"Listening on port {PORT}")
    print("READY")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        ml.cleanup()
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="PORT", default='50051')
    (options, args) = parser.parse_args()
    PORT = os.getenv("FPGA_SERVER_PORT", options.PORT)
    serve()
