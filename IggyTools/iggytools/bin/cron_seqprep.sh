#!/bin/bash

TYP=$(type -t module) || true
if [[ $TYP != "function" ]]; then
  source /etc/profile
fi

. /n/informatics/iggy/setup.sh
/n/informatics/iggy/IggyTools/iggytools/bin/cron_seqprep ${@-}

