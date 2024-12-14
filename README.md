# vv_calan
Python Package to interface the vector voltmeter developed in ROACH2 board

Important note, the codes are in python2 and like the dependencies are a hell pit, I recommend using pyenv to manage the installation. 
There is also a Docker file if you want to have all the packages right away, the only thing to look at is that to share the GUI you need to give access to the X server by runinng something like: `xhost +`(this gaves access to the X display to everyone)

# Installation:

You need to install the packages in the requirement file using

`pip install -r requirements`

Also for the transfer of data between the roach and your computer you would need netcat.

When you have the require packet you could install the package using:

`pip install vv_calan/`


