
#module --Silent load centos6/python-2.7.3
#source /n/informatics/mclamp/iggy/iggy_ve2.7.3/bin/activate
module load python
source activate seqprep

umask 002

export DJANGO_SETTINGS_MODULE=iggytools.iggyapp.settings
#export PYTHONPATH=$PYTHONPATH:/n/informatics/afreedman/iggy/IggyTools
export PYTHONPATH=$PYTHONPATH:/n/home_rc/afreedman/workspace/IggyTools/IggyTools
#export PATH=$PATH:/n/informatics/afreedman/iggy/IggyTools/iggytools/bin
export PATH=$PATH:/n/home_rc/afreedman/workspace/IggyTools/IggyTools/iggytools/bin
iggytools_setup


