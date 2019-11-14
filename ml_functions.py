import tensorflow as tf
from keras.models import load_model
import keras.backend as K
import numpy as np
import os

from tensorflow.python.util import deprecation
deprecation._PRINT_DEPRECATION_WARNINGS = False

import time, threading

lock = threading.Lock()

def predict(data, batch_size, results=None, times=None, job_id=None):
    lock.acquire()
    np.savetxt('src/tb_data/tb_input_features.dat', data)
    start_time = time.time()
    os.system('./host %i'%int(data.shape[0]/batch_size))
    predictions = np.loadtxt('tb_output_data.dat')
    predict_time = time.time() - start_time
    lock.release()
    if results is not None and job_id is not None:
        results[job_id] = predictions
        times[job_id] = predict_time
    else:
        return predictions, predict_time

def cleanup():
    K.clear_session()
