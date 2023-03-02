# chopchop


## Installation

```shell

#创建python2.7环境
conda env create -f chopchop.yaml

#创建python3.8环境
conda env create -n main_chopchop python==3.8
conda install ucsc-fatotwobit
pip install pandas
pip install pandarallel
```

## Usage
#在main_chopchop环境中条用chopchop环境中chopchop.py

```shell

git clone http://172.16.25.29/yangChunhe/chopchop.git

python main.py -i ./data/input/config.json

```