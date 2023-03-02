import os,sys
from os import makedirs
import pandas as pd
from os.path import exists,splitext,dirname,splitext,basename,realpath,abspath
os.getcwd()
import json  
import argparse
import math   
import subprocess
from Bio import SeqIO
import multiprocessing as mp
   
# from loguru import logger
# logger.add('out.log')
# logger.add(sys.stdout, level='INFO', format='{message}')   
# from pandarallel import pandarallel  
# pandarallel.initialize(nb_workers=80)
    
def excecute_one_chopchop(env,chopchop_params,parent_output):
    
    env = env
    base_path = base_path = os.path.abspath(os.path.dirname(__file__)) + '/'
    genome_name = chopchop_params['genome_name']
    output = chopchop_params['output']
    info_list_one = chopchop_params['info_list_one']
    PAM = chopchop_params['PAM']
    scoringMethod = chopchop_params['scoringMethod']
    maxMismatches = chopchop_params['maxMismatches']
    guideSize = chopchop_params['guideSize']


    cmd = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
                                    (env + '/bin/python',
                                        base_path+'/'+'chopchop.py',
                                        '-G',
                                        genome_name,
                                        '-o', 
                                        output,
                                        '-Target',
                                        info_list_one,   
                                        '-scoringMethod',     # ["XU_2015", "DOENCH_2014", "DOENCH_2016", "MORENO_MATEOS_2015", "CHARI_2015", "G_20", "KIM_2018", "ALKAN_2018", "ZHANG_2019", "ALL"]
                                        scoringMethod,
                                        '-v',    #[0, 1, 2, 3]
                                        maxMismatches,
                                        '-M',    #The PAM motif
                                        PAM,
                                        '-g',
                                        guideSize,
                                        '-config',
                                        parent_output+'/'+'config.json'
                                    )   
    # logger.info(f"cmd = {cmd}")
    
    print('执行的命令:',cmd)   


    runbashcmd(cmd)  
    try:
        temp_df = pd.read_csv(output+'result.csv')
    except Exception as e:
        # logger.error(f'Get files list failed. | Exception: {e}')
        print(e)
        temp_df = pd.DataFrame()
    
    temp_df['Region'] = info_list_one
    return temp_df


def call_chopchop(output,chopchop_params,info_list_one):   
  
    #env
    env = os.environ['CONDA_PREFIX']

    print(env)  
    if 'chopchop' not in env:
        env_path = env.split('/')
        print(env_path)  
        env_path[-1] = 'chopchop'
        env = '/'.join(env_path)
        print('env:',env)

    

    temp_output = output +'/temp/'+info_list_one + '/'
    if not exists(temp_output):
        makedirs(temp_output)

    chopchop_params.update({'output':temp_output,"info_list_one":info_list_one})

    #统计计算时间
    import time
    start_time = time.time()   
   
    temp_df = excecute_one_chopchop(env,chopchop_params,output)

    end_time = time.time()
    arr = info_list_one.split(":")[1].split("-")
    temp_df['edit_region_length'] = int(arr[1]) - int(arr[0])
    temp_df['time(s)'] =  end_time - start_time

    return temp_df



def check_create_path(config):

    genome_name = config['chopchop_params']['genome_name']
    genome_path = config['genome_path']


    #2bit
    bit_datat = config['bit_datat']
    genome_2bit ='{}{}{}'.format(bit_datat,genome_name,'.2bit')
    #ebwt
    ebwt_datat = config['ebwt_datat']
    genome_ebwt_datat = '{}{}'.format(ebwt_datat,genome_name)

      #judge
    if not exists(bit_datat):  
        makedirs(bit_datat)
    if not exists(genome_2bit):
        cmd = '{}\t{}\t{}'.format('faToTwoBit',genome_path,genome_2bit)
        runbashcmd(cmd)
    if not exists(genome_ebwt_datat):
        makedirs(genome_ebwt_datat)

        print(genome_ebwt_datat)
        genome_ebwt_datat = genome_ebwt_datat + '/'+ genome_name
        cmd = '{}\t{}\t{}'.format('bowtie-build',genome_path,genome_ebwt_datat)
        print('build:-----------------------------------------------',cmd)
        runbashcmd(cmd)


def write_config(config,input_path,ref_genome,chopchop_params,output):

    chopchop_workdir = output

    #-------------------------------------------
    config['genome_path'] = ref_genome
    config['chopchop_params'] = chopchop_params
    config['info_path'] = input_path
    config['output_path'] = output
    #-------------------------------------------

    #-----------------------------------------
    if chopchop_workdir in config['PATH']['BOWTIE_INDEX_DIR']: 
        pass
    else:
        config['PATH']['BOWTIE'] = 'bowtie'
        config['PATH']['TWOBITTOFA'] = 'twoBitToFa'

        config['PATH']['TWOBIT_INDEX_DIR'] = chopchop_workdir +'/'+ config['PATH']['TWOBIT_INDEX_DIR']
        config['PATH']['PRIMER3'] = chopchop_workdir +'/'+ config['PATH']['PRIMER3']
        config['PATH']['BOWTIE_INDEX_DIR'] = chopchop_workdir +'/'+ config['PATH']['BOWTIE_INDEX_DIR'] +'/'+ config['chopchop_params']['genome_name']
    #------------------------------------------

    #--------------------------------------------
    config['ebwt_datat'] = chopchop_workdir + '/' + config['ebwt_datat']  
    config['bit_datat'] = chopchop_workdir + '/' + config['bit_datat']
    #--------------------------------------------


    check_create_path(config)
    


    #write new_config.json
    json_str = json.dumps(config)
   
    with open(chopchop_workdir+"/"+'config.json', 'w') as json_file:
        json_file.write(json_str)
    

    return chopchop_workdir+"/"+'config.json'


def runbashcmd(cmd,test=False,logf=None):

    # from super_beditor.lib.global_vars import dirs2ps 
    print('before:',cmd)
    # cmd = cmd.replace("$BIN", dirs2ps['binDir'])
    # cmd = cmd.replace("$PYTHON", dirs2ps['pyp'])
    # cmd = cmd.replace("$SCRIPT", dirs2ps['scriptDir'])
    print('after:',cmd)
    if test:
        print(cmd)
    
    err=subprocess.call(cmd,shell=True,stdout=logf,stderr=subprocess.STDOUT)
    print(err)
    if err!=0:
        print('bash command error: {}\n{}\n'.format(err,cmd))
        sys.exit(1)


def extract_seq_from_genome(genome,gene_id,start=0,end=0):
    # 读取基因组文件
    records = SeqIO.parse(genome,'fasta')
    
    # 遍历基因组文件中的所有记录
    for record in records:
        # 如果当前记录的ID与所需的ID匹配
        if record.id == gene_id:
            # 提取坐标范围内的序列
            if start ==0 and end ==0:
                return str(record.seq)
            else:
                sequence = str(record.seq[start:end])
                if sequence != '':
                    return  sequence.upper()
                else:
                    return sequence



def filter(df,genome):
    df = df[df['region'] != '']
    df['chromosome_seq_len'] = df.region.parallel_apply(lambda x: len(extract_seq_from_genome(genome=genome, gene_id=x.split(":")[0])))
    def work(region, chromosome_seq_len):
            target_coords=region.split(":")[1]
            target_coords = int(target_coords.split('-')[0]),int(target_coords.split('-')[1])
            start = target_coords[0]
            end = target_coords[1]
            if start < 80 or chromosome_seq_len - end < 80 or start >= end:
                return 'no'
            else:
                return 'yes'
    df['tag'] = df.parallel_apply(lambda x: work(x['region'], x['chromosome_seq_len']), axis=1)

    df = df[df['tag'] == 'yes']
    return df




# 定义一个函数，用于在多进程中调用
def process_region(params):
    output,chopchop_params, region = params
    # 调用call_chopchop函数
    print(output,chopchop_params, region)   
    result = call_chopchop(output, chopchop_params, region)
    return result



def main(event):

    #
    base_path = os.path.abspath(os.path.dirname(__file__)) + '/'

    print('hjdsgfjdgsjghdjshjk')
    print(base_path)
    print(os.listdir(base_path))    


    #parse event
    input_path = event["input_file_path"]
    ref_genome = event["ref_genome"] 
    chopchop_params = event["chopchop_config"]
    output = event["chopchop_workdir"] 


    #read config
    chopchop_local_config = base_path + '/data/input/' + 'config.json'
    with open(chopchop_local_config, "r") as f:
        data = json.load(f)

    #write config to temp
    tem_config = write_config(data,input_path,ref_genome,chopchop_params,output)
    print('temp中的config位置',tem_config)

    print("output内容",os.listdir(output))


    #
    
    df = pd.read_csv(input_path)

    print(df.columns)
  
    # info_list_one = 'CM001534.1:231516-232905'      
    # sgRNA = call_chopchop(output,base_path,chopchop_params,info_list_one)
    # ------------------------------------------------------
    import time
    start_time = time.time()
    #parallel processing
    
    temp = df.region.apply(lambda x: call_chopchop(output,chopchop_params,x))
    # pool = mp.Pool()
    #   # 使用map函数在多个进程中调用process_region函数
    # results = pool.map(process_region, [(output,chopchop_params, region) for region in df.region])

    # # 关闭进程池
    # pool.close()



    sgRNA_df = pd.concat([row for i,row in temp.items()])
    sgRNA_df.to_csv(output+'/'+'sgRNA.csv',index=False)
     
    end_time = time.time()
    print("Execution time:", end_time - start_time, "seconds")     
    # --------------------------------------------------------

    import shutil
    # remove .sam files as they take up wayyy to much space
    print(output)
    if exists(output +'/'+ 'temp'):
        shutil.rmtree(output +'/'+ 'temp')
   
    return output + '/' + 'sgRNA.csv'



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input params file', required=True) 
    args = parser.parse_args()
    input_path =  args.input
    with open(input_path, "r") as f:
        data = json.load(f)
    
    main(data)




