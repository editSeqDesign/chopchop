#-*- coding:utf-8 -*-
'''
Author: yangchunhe
Date: 2023-02-16 05:38:18
LastEditors: wangruoyu
LastEditTime: 2023-03-09 02:10:45
Description: file content
FilePath: /chopchop_crispr_cdk/lambda/chopchop/app.py
'''
import os
import sys
import uuid

import boto3   
import pandas as pd
import xlsxwriter
from Bio import SeqIO

# print(sys.path)
print(os.environ) 
print(os.listdir('.'))  

import main as mn    


result_bucket = os.environ["s3Result"]
s3 = boto3.resource('s3')

def download_s3_file(s3_file, workdir):
    """
    从s3下载文件
    :param s3_file: _description_
    :type s3_file: _type_
    :param workdir: _description_
    :type workdir: _type_
    """
    bucket = s3_file.split('/')[2]
    filename = s3_file.split('/')[-1]
    obj_key = '/'.join(s3_file.split('/')[3:])
    
    local_file = os.path.join(
        workdir,
        filename
    )
    s3.Object(bucket, obj_key).download_file(local_file)
    return local_file

def lambda_handler(event,context):
    """
    :param event: _description_
    :type event: _type_
    :param context: _description_
    :type context: _type_
    :return: _description_
    :rtype: _type_
   
    event = {
        "input_file_path":"s3://chopchop-prod/test/chopchop/Corynebacterium_glutamicum_info_input.csv",
        "ref_genome":"s3://chopchop-prod/test/chopchop/GCA_000011325.1_ASM1132v1_genomic.fna",
        "data_preprocessing_workdir":"/home/yanghe/tmp/chopchop/output/",
        "chopchop_config":{
            "PAM": "NGG",
            "THREADS": 8,
            "genome_name": "Corynebacterium_glutamicum",
            "guideSize": 20,
            "maxMismatches": 3,
            "scoringMethod": "DOENCH_2014"
        }
    }
    """
    print(event)
    try:
        # 读写路径
        jobid = event["jobid"]
        workdir = f'/tmp/{jobid}'
        print(f'working dir: {workdir}')
        if not os.path.exists(workdir):
            os.mkdir(workdir)
        os.chdir(workdir)
        event["chopchop_workdir"] = workdir
        
        #下载数据 并重置参数
        event["input_file_path"] = download_s3_file(event["input_file_path"],workdir)
        event["ref_genome"] = download_s3_file(event["ref_genome"],workdir)
        event["chopchop_config"] = event["chopchop_config"]
          
        print("event事件:",event["input_file_path"],  event["ref_genome"] ,event['chopchop_config'])
    
        
        output_file = mn.main(event)
        
        # 上传结果文件
        output_file_key = f"result/{jobid}/chopchop/{output_file.split('/')[-1]}"
        s3.meta.client.upload_file(output_file, result_bucket, output_file_key,ExtraArgs={'ACL': "public-read"})
        print(f'upload result file: {output_file_key} ')
        return {
            "statusCode":200,
            "output_file":f"s3://{result_bucket}/{output_file_key}"
        }
    except Exception as e:
        print(e)
        return {
            "statusCode":500,
            "msg":str(e)
        }
    finally:
        # os.system(f'rm -rf {workdir}')  
        print(f"delete working dir: {workdir}")
    
    
if __name__ == "__main__":
    
    # s3文件测试
    event = {
        "input_file_path":"s3://chopchop-prod/test/chopchop/Corynebacterium_glutamicum_info_input.csv",
        "ref_genome":"s3://chopchop-prod/test/chopchop/GCA_000011325.1_ASM1132v1_genomic.fna",
        "chopchop_workdir":"/home/wang_ry/tmp/chopchop/output/",
        "chopchop_config":{
            "PAM": "NGG",
            "THREADS": 8,
            "genome_name": "Corynebacterium_glutamicum",  
            "guideSize": 20,
            "maxMismatches": 3,
            "scoringMethod": "DOENCH_2014"
        }
    }
    lambda_handler(event,{})



