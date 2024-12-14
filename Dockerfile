FROM python:2.7

ARG UID=1000

RUN apt-get update
RUN apt-get --assume-yes install gcc make curl netcat ssh g++ python-dev python-tk

RUN adduser -q --disabled-login --gecos "First Last,RoomNumber,WorkPhone,HomePhone" --uid $UID myuser
USER myuser
WORKDIR /home/myuser
RUN mkdir /home/myuser/vv_calan
RUN mkdir /home/myuser/measure_ex
RUN mkdir /home/myuser/gui
RUN mkdir /home/myuser/data

ADD data/ /home/myuser/data

COPY --chown=myuser:myuser requirements requirements
COPY --chown=myuser:myuser vv_calan/ vv_calan/
COPY --chown=myuser:myuser measure_ex/ measure_ex/
COPY --chown=myuser:myuser gui/ gui/


RUN pip install --user -r requirements
#for some reason its not being installed correctly in the requirements..
RUN pip install --user git+https://github.com/ska-sa/PySPEAD.git
RUN pip install --user git+https://github.com/sebajor/vv_calan.git
RUN pip install ipython
#RUN pip install /home/myuser/vv_calan/

ENV PATH="/home/myuser/.local/bin:${PATH}"
ENV LD_LIBRARY_PATH="/home/myuser/libs:$(LD_LIBRARY_PATH)"

CMD ["bash"]


