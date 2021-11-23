#!/bin/bash
plot_snapshots.py \
    --ip         10.10.1.90 \
    `#--bof      $(echo $BOF_FILE)` \
    --upload      \
    --snapnames  adcsnap0 adcsnap1 \
    --dtype      ">b" \
    --nsamples   200
