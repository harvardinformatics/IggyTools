#!/bin/bash

TYP=$(type -t module) || true
if [[ $TYP != "function" ]]; then
  source /etc/profile
fi

umask 002

. /n/informatics/iggy/setup.sh
/n/informatics/IggyTools/iggytools/bin/updateIggyref.py ${@-} 1> /n/regal/informatics_public/ref/.work/log/cron.log
