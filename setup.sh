
module --Silent load centos6/python-2.7.3
source /n/informatics/iggy/iggy_ve2.7.3/bin/activate

export DJANGO_SETTINGS_MODULE=iggytools.iggyapp.settings
export PYTHONPATH=$PYTHONPATH:/n/informatics/mclamp/test/IggyTools/IggyTools
export PATH=$PATH:/n/informatics/mclamp/test/IggyTools/IggyTools/iggytools/bin

iggytools_setup
