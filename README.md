# Home Depot - Cloud MVM

## Setup

- Install necessary dependencies

```
pip install tensorflow==1.2
pip install apache-beam==2.0.0
pip install tensorflow-transform==0.1.10
```

- Add constants to PATH

```
export PYTHONPATH = $PYTHONPATH:<path_to_project_directory>
```

## Commands

- Run preprocessing locally

```
NOW=$(date +"%Y%m%d_%H%M%S")
TFT_OUTPUT_DIR=tft_outputs/${NOW}
python preprocess.py \
  --output_dir=${TFT_OUTPUT_DIR} \
```

- Run training locally

```
NOW=$(date +"%Y%m%d_%H%M%S")
python ./trainer/task.py \
  --model_dir=models/${NOW} \
  --input_dir=$TFT_OUTPUT_DIR
```

- Run preprocessing on the cloud

```
BUCKET=gs://thdmodels
TFT_OUTPUT_DIR=${BUCKET}/tft/outputs/${USER}$(date +%Y%m%d%H%M%S)
python preprocess.py \
  --output_dir $TFT_OUTPUT_DIR \
  --cloud
```
