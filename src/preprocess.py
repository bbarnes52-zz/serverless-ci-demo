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
import argparse
from datetime import datetime
from posixpath import join as urljoin
import os
import sys

import apache_beam as beam
import tensorflow_transform as tft
from tensorflow_transform.beam import impl as tft_beam
from tensorflow_transform.tf_metadata import dataset_metadata
from tensorflow_transform.tf_metadata import dataset_schema
from tensorflow_transform.beam import tft_beam_io
from tensorflow_transform import coders
from tensorflow_transform import mappers

from constants import constants
import tempfile


GCP_PROJECT='pso-data-ml'
DATASET_NAME='mock'
TABLE_NAME='ice_cream_sales'


def _parse_arguments(argv):
  """Parses command line arguments."""
  parser = argparse.ArgumentParser(
      description="Runs Preprocessing on THD data.")
  parser.add_argument(
      "--project_id", default=GCP_PROJECT, required=False,
      help="The project to which the job will be submitted.")
  parser.add_argument(
      "--output_dir", required=False,
      help=("GCS or local directory in which to place outputs."))
  parser.add_argument(
      "--cloud", default=False, action="store_true",
      help="run preprocessing on the cloud.")
  args, _ = parser.parse_known_args(args=argv[1:])
  return args


def _make_input_schema(mode=tf.contrib.learn.ModeKeys.TRAIN):
  """Input schema definition.
  Args:
    mode: tf.contrib.learn.ModeKeys specifying if the schema is being used for
      train/eval or prediction.
  Returns:
    A `Schema` object.
  """
  feature_spec = ({} if mode == tf.contrib.learn.ModeKeys.INFER else {
      'temperature': tf.FixedLenFeature(shape=[], dtype=tf.float32)
  })
  feature_spec.update({
      'sales': tf.FixedLenFeature(shape=[], dtype=tf.float32)
  })
  return dataset_schema.from_feature_spec(feature_spec)


def _get_query():
    return """
    SELECT
        TEMPERATURE as temperature,
        SALES as sales
    FROM
        {}.{}
    """.format(DATASET_NAME, TABLE_NAME)


def get_preprocessing_fn():
    def preprocessing_fn(inputs):
        # TODO(bgb): Implement.
        return inputs
    return preprocessing_fn


def preprocess(p, output_dir):
  """Run preprocessing as pipeline."""
  from constants import constants

  train_eval_schema = _make_input_schema()

  train_eval_metadata = dataset_metadata.DatasetMetadata(
          schema=train_eval_schema)

  _ = (train_eval_metadata
       | 'WriteInputMetadata' >> tft_beam_io.WriteMetadata(
           os.path.join(output_dir, constants.RAW_METADATA_DIR),
           pipeline=p))
  
  train_data = (p | "ReadDataFromBQ" >> beam.io.Read(beam.io.BigQuerySource(
      query=_get_query(), use_standard_sql=True)))

                                                                                     
  (transformed_train_data, transformed_train_metadata), transform_fn = (           
          (train_data, train_eval_metadata)                                            
          | 'AnalyzeAndTransform' >> tft_beam.AnalyzeAndTransformDataset(              
              get_preprocessing_fn()))

  _ = (transform_fn 
          | 'WriteTransformFn' >> tft_beam_io.WriteTransformFn(output_dir))

  transformed_train_coder = coders.ExampleProtoCoder(
          transformed_train_metadata.schema)

  (transformed_train_data
   | 'SerializeTrainExamples' >> beam.Map(transformed_train_coder.encode)
   | 'WriteTraining' >> beam.io.WriteToTFRecord(
       os.path.join(output_dir, constants.TRANSFORMED_TRAIN_DATA_FILE_PREFIX),
       file_name_suffix=constants.DATA_FILE_SUFFIX))


def main():
  args = _parse_arguments(sys.argv)
  options = {"project": args.project_id}
  now = datetime.now().strftime("%Y%m%d%H%M%S")
  if not args.output_dir:
    if args.cloud:
      output_dir_prefix = "gs://ice-cream-sales/"
    else:
      output_dir_prefix = "./"
  output_dir = args.output_dir or urljoin(output_dir_prefix, "pipeline-outputs", now)
  temp_dir = urljoin(output_dir, 'tmp')
  if args.cloud:
    options.update({
        "job_name": ("ice-cream-sales-pipeline-{}".format(now)),
        'max_num_workers': 100,
        'setup_file': os.path.abspath(os.path.join(os.path.dirname(__file__),
            'setup.py')),
        "temp_location": temp_dir
    })
    runner = "DataflowRunner"
  else:
    runner = "DirectRunner"
  pipeline_options = beam.pipeline.PipelineOptions(flags=[], **options)
  with beam.Pipeline(runner, options=pipeline_options) as p:
    with tft_beam.Context(temp_dir=temp_dir):
      preprocess(p, output_dir)


if __name__ == "__main__":
  main()
