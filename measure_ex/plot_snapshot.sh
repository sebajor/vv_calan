#!/bin/bash
plot_snapshots.py \
    --ip         192.168.1.14 \
    `#--bof      $(echo $BOF_FILE)` \
    --upload      \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">b" \
    --nsamples   200
