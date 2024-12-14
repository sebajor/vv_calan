#!/bin/bash

docker run -it --mount src="$(pwd)"/data,target=/home/myuser/data,type=bind vv_test bash
