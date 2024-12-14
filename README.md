# vv_calan
Python Package to interface the vector voltmeter developed in ROACH2 board

Important note, the codes are in python2 and like the dependencies are a hell pit, I recommend using pyenv to manage the installation. 
There is also a Docker file if you want to have all the packages right away, the only thing to look at is that to share the GUI you need to give access to the X server by runinng something like: `xhost +`(this gaves access to the X display to everyone)

To install the docker image you just need to issue: `docker build -t <any_name> .` 
You can start the Docker container runing the `./start_docker.sh` (warning the only directory that is not being erased when shutting down the container is what is inside of the data folder)


# Installation:

You need to install the packages in the requirement file using

`pip install -r requirements`

Also for the transfer of data between the roach and your computer you would need netcat.

When you have the require packet you could install the package using:

`pip install vv_calan/`

For an unknown reason sometime when importing the package if throw an error realted with pyspead its because the installation from the requirements file did not worked (I dont know why). You can install manually the package to solve the issue by running: `pip install git+https://github.com/ska-sa/PySPEAD.git`


