
from continuumio/miniconda3
# Install the function's dependencies using file requirements.txt
# from your project folder.


RUN apt-get update && \
  apt-get install -y \
  g++ \
  make \
  cmake \   
  unzip \
  libcurl4-openssl-dev 


#install wget
# RUN yum install -y wget vim tar gzip unzip zip

# ENV PATH /opt/conda/bin:$PATH  
# ENV PATH /opt/blast/bin:$PATH

WORKDIR /app

# RUN wget --quiet https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.9.0/ncbi-blast-2.9.0+-x64-linux.tar.gz -O /opt/blast.tar.gz && \
#     tar -zvxf /opt/blast.tar.gz -C /opt/ && \
#     mv /opt/ncbi-blast-2.9.0+ /opt/blast 
    
# RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda && \
#     rm ~/miniconda.sh && \
#     ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
#     echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
#     echo "conda activate base" >> ~/.bashrc

RUN conda create -n chopchop -y python=2.7.18
RUN conda create -n crispr_hr_editor -y python=3.8
COPY *  /app/ 
RUN chmod -R a+rwx app.py
# COPY chopchop_requirements.txt .
# COPY crispr_hr_editor_requirements.txt .
# COPY chopchop .
# COPY edit_sequence_design .
# COPY main.py .
    
# RUN wget --quiet http://hgdownload.soe.ucsc.edu/admin/exe/linux.x86_64/twoBitToFa -O /app/chopchop/twoBitToFa && \
# RUN chmod +x twoBitToFa

# ENV PATH /app/chopchop/:$PATH

# RUN wget --quiet https://sourceforge.net/projects/bowtie-bio/files/bowtie/1.3.1/bowtie-1.3.1-linux-x86_64.zip -O /app/chopchop/bowtie.zip && \
#     unzip /app/chopchop/bowtie.zip -d /app/chopchop/ && \
#     mv /app/chopchop/bowtie-1.3.1-linux-x86_64  /app/chopchop/bowtie && \
#     rm /app/chopchop/bowtie.zip



# set shell to use bash in interactive mode
SHELL ["/bin/bash", "--login", "-c"]

# RUN . /opt/conda/etc/profile.d/conda.sh && \
RUN conda activate chopchop && \
    pip install -r chopchop_requirements.txt


# RUN . /opt/conda/etc/profile.d/conda.sh && \
RUN  conda activate crispr_hr_editor && \
    pip install -r requirements.txt && \ 
    pip install loguru && \
    pip install pandarallel && \
    conda config --add channels 'https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/' && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge'   && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/menpo/'     && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda/' && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/msys2/'   && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/conda-forge/' && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/pkgs/free/' && \
    conda config --add channels 'https://mirrors.ustc.edu.cn/anaconda/cloud/bioconda' && \
    conda config --add channels 'http://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/' && \
    conda install primer3-py && \   
    conda install awscli && \
    conda install boto3

# activate the conda environment
SHELL ["/bin/bash", "-c"]
RUN source /opt/conda/bin/activate crispr_hr_editor

# set the default environment to myenv
RUN echo "source activate crispr_hr_editor" > ~/.bashrc



# Install the runtime interface client
RUN pip install \
        --target ./  \
        awslambdaric

ENTRYPOINT [ "/opt/conda/envs/crispr_hr_editor/bin/python", "-m", "awslambdaric" ]
CMD [ "app.lambda_handler" ]
