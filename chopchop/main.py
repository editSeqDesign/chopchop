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
from loguru import logger
logger.add('out.log')
logger.add(sys.stdout, level='INFO', format='{message}')   
from pandarallel import pandarallel  
pandarallel.initialize(nb_workers=80)

# def execute_input_2_chopchop_input(input_file_path, primer_config, genome_path, convert_input_file_chopchopInput_workdir, chopchop_input_dir):
#     crispr_info = pd.read_csv(input_file_path)
#     config = pf.conf_read(primer_config)
#     dict_input_seq = pf.input_to_primer_template(input_file_path,genome_path,config, convert_input_file_chopchopInput_workdir)
#     info_input_df = pf.dict_to_df(dict_input_seq)
#     info_input_df.to_csv(chopchop_input_dir+'info_input.csv')
    
def excecute_one_chopchop(env,base_path,chopchop_params):
    
    env = env
    base_path = base_path
    genome_name = chopchop_params['genome_name']
    output = chopchop_params['output']
    info_list_one = chopchop_params['info_list_one']
    PAM = chopchop_params['PAM']
    scoringMethod = chopchop_params['scoringMethod']
    maxMismatches = chopchop_params['maxMismatches']
    guideSize = chopchop_params['guideSize']

    

    cmd = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" % \
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
                                        guideSize
                                    )
    logger.info(f"cmd = {cmd}")


    runbashcmd(cmd)  
    try:
        temp_df = pd.read_csv(output+'result.csv')
    except Exception as e:
        logger.error(f'Get files list failed. | Exception: {e}')
        print(e)
        temp_df = pd.DataFrame()
    
    temp_df['Region'] = info_list_one
    return temp_df


def call_chopchop(output,base_path,chopchop_params,info_list_one):   
  
    #env
    env = os.environ['CONDA_PREFIX']
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

    temp_df = excecute_one_chopchop(env,base_path,chopchop_params)

    end_time = time.time()
    arr = info_list_one.split(":")[1].split("-")
    temp_df['edit_region_length'] = int(arr[1]) - int(arr[0])
    temp_df['time(s)'] =  end_time - start_time
     


    return temp_df

def write_config(base_path,config):

    print('base_path:',base_path)

    #-----------------------------------------
    if base_path in config['PATH']['BOWTIE']: 
        pass
    else:
        config['PATH']['BOWTIE'] = base_path +'/'+ config['PATH']['BOWTIE']
        config['PATH']['TWOBIT_INDEX_DIR'] = base_path +'/'+ config['PATH']['TWOBIT_INDEX_DIR']
        config['PATH']['PRIMER3'] = base_path +'/'+ config['PATH']['PRIMER3']
        config['PATH']['TWOBITTOFA'] = base_path +'/'+ config['PATH']['TWOBITTOFA']
        config['PATH']['BOWTIE_INDEX_DIR'] = base_path +'/'+ config['PATH']['BOWTIE_INDEX_DIR'] +'/'+ config['chopchop_params']['genome_name']
    #------------------------------------------


    #write new_config.json
    json_str = json.dumps(config)
    with open(base_path +'/data/input/'+ 'config.json', 'w') as json_file:
        json_file.write(json_str)

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

def read_config(base_path):

    with open(base_path+'/data/input/'+'config.json', "r") as f:
        config = json.load(f)

    #chopchop_params
    chopchop_params = config['chopchop_params']

    #genome path
    genome_path = base_path +'/'+ config['genome_path']
    #input_path   
    input_path = base_path +'/'+ config['info_path']
    #output
    output = base_path +'/'+ config['output_path']
 
    #2bit
    genome_name = chopchop_params['genome_name'] 
    bit_datat = base_path +'/'+ config['bit_datat']
    genome_2bit ='{}{}{}'.format(bit_datat,genome_name,'.2bit')
    #ebwt
    ebwt_datat = base_path +'/'+  config['ebwt_datat']
    genome_ebwt_datat = '{}{}'.format(ebwt_datat,genome_name)
    print( '-------------------------------------------------------------------',genome_ebwt_datat,'---------------',genome_ebwt_datat )



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
        cmd = '{}\t{}\t{}'.format('bowtie/bowtie-build',genome_path,genome_ebwt_datat)
        print('build:-----------------------------------------------',cmd)
        runbashcmd(cmd)

  
    
    return input_path,output,genome_path,chopchop_params


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



def main(data):

    #
    base_path = os.path.abspath(os.path.dirname(__file__))
    parent_base_path = os.path.abspath(os.path.join(base_path, os.path.pardir))

    #
    write_config(base_path,data)

    #
    input_path,output,genome_path,chopchop_params = read_config(base_path)
    df = pd.read_csv(input_path+'Corynebacterium_glutamicum_info_input.csv')
    

    # info_list_one = 'CM001534.1:231516-232905'      
    # sgRNA = call_chopchop(output,base_path,chopchop_params,info_list_one)

    # ------------------------------------------------------
    import time
    start_time = time.time()
    #parallel processing
    temp = df.region.parallel_apply(lambda x: call_chopchop(output,base_path,chopchop_params,x))
    sgRNA_df = pd.concat([row for i,row in temp.iteritems()])
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




