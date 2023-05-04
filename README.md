# chopchop
## Project Introduction 
This project uses the output results of the upstream task module (data_processing) as input to the standardized editing area, and then encapsulates and modifies the sgRNA design tool chopshop. Finally, it can high-throughput design sgRNA for multiple editing areas simultaneously.

    data = {
        "input_file_path":"/home/XXX/tmp/data_preprocessing/output/info_input.csv",
        "ref_genome":"/home/XXX/tmp/data_preprocessing/output/xxx.fna",
        "chopchop_workdir":"/home/XXX/tmp/chopchop/output/", 
        "chopchop_config":{
            "PAM": "NNNNGMTT", 
            "guideSize": 20,
            "maxMismatches": 3,
            "scoringMethod": "XU_2015"
        }
    }

    output: "/home/yanghe/tmp/chopchop/output/sgRNA.json","/home/yanghe/tmp/chopchop/output/sgRNA.csv"


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
method1：在main_chopchop环境中调用chopchop环境中main.py

method2：在aws云开发中通过Dockerfile启动容器ECR将其代码托管到lambda中使用

```shell

git clone http://172.16.25.29/yangChunhe/chopchop.git

python main.py

```