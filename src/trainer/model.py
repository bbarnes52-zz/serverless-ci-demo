# Copyright 2016 Google Inc. All Rights Reserved.
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

import tensorflow as tf

tf.logging.set_verbosity(tf.logging.INFO)

FEATURE_COLUMN='current_retail_amount'

def model_fn(features, labels, mode, params):
    """Model function for Estimator."""
    
    fully_connected_layer = tf.layers.dense(
            tf.expand_dims(tf.cast(features[FEATURE_COLUMN], tf.float64), -1),
            units=1,
            activation=None)
    predictions = tf.reshape(fully_connected_layer, [-1])
    predictions_dict = {"shelf_outs": predictions}
    if mode == tf.contrib.learn.ModeKeys.INFER:
        return tf.contrib.learn.ModelFnOps(
                mode=mode,
                predictions=predictions_dict)
    loss = tf.losses.mean_squared_error(labels, predictions)
    eval_metric_ops = {
            "rmse": tf.metrics.root_mean_squared_error(
                tf.cast(labels, tf.float64), predictions)
            }
    optimizer = tf.train.GradientDescentOptimizer(
                  learning_rate=params.learning_rate)
    train_op = optimizer.minimize(
            loss=loss, global_step=tf.train.get_global_step())
    return tf.contrib.learn.ModelFnOps(
        mode = mode,
        predictions = predictions_dict,
        loss = loss,
        train_op = train_op,
        eval_metric_ops = eval_metric_ops)
   
