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
from tensorflow.contrib.learn.python.learn import learn_runner
import model
import input_fn_utils
import argparse
import shutil
import sys

def _parse_arguments(argv):
  """Parses command line arguments."""
  parser = argparse.ArgumentParser(
      description="Runs training on THD data.")
  parser.add_argument(
      "--model_dir", required=True,
      help="The directory where model outputs will be written")
  parser.add_argument(
      "--input_dir", required=True,
      help=("GCS or local directory containing tensorflow-transform outputs."))
  parser.add_argument(
      "--learning_rate", default=0.0005, required=False, type=float,
      help=("Learning rate to use during training."))
  parser.add_argument(
      "--batch_size", default=16, required=False, type=int,
      help=("Batch size to use during training."))
  parser.add_argument(
      "--num_epochs", default=5, required=False, type=int,
      help=("Number of epochs through the training set"))
  args, _ = parser.parse_known_args(args=argv[1:])
  return args

def get_experiment_fn(args):
    config = tf.contrib.learn.RunConfig(save_checkpoints_steps=1000)
    def experiment_fn(output_dir):
        return tf.contrib.learn.Experiment(
            estimator = tf.contrib.learn.Estimator(model_fn = model.model_fn,
                                          model_dir = output_dir,
                                          config = config,
                                          params=args),
            train_input_fn = input_fn_utils.read_dataset(args.input_dir,
                args.num_epochs, args.batch_size,
                mode=tf.contrib.learn.ModeKeys.TRAIN),
            eval_input_fn = input_fn_utils.read_dataset(args.input_dir,
                args.num_epochs, args.batch_size,
                mode=tf.contrib.learn.ModeKeys.EVAL),
            eval_steps = 500,
            export_strategies = tf.contrib.learn.utils.make_export_strategy(
                input_fn_utils.get_serving_input_fn(args.input_dir),
                default_output_alternative_key=None,
                exports_to_keep=5))
    return experiment_fn


def run(args):
    shutil.rmtree(args.model_dir, ignore_errors=True)
    learn_runner.run(get_experiment_fn(args), args.model_dir)


if __name__ == '__main__':
    args = _parse_arguments(sys.argv)
    run(args)
