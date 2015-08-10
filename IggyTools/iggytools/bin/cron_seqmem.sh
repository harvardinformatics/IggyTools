#!/bin/bash

TYP=$(type -t module) || true
if [[ $TYP != "function" ]]; then
  source /etc/profile
fi

umask 002

. /n/informatics/mclamp/iggy/setup.sh
/n/informatics/mclamp/iggy/IggyTools/iggytools/bin/cron_seqmem ${@-}

