# PyCh

PyCh is a Python package based on SimPy for discrete-event simulation.
It is a tool developed for the course "Analysis of production systems" (4DC10).
PyCh is a port of [Chi3](https://cstweb.wtb.tue.nl/chi/trunk-r9682/).

# Important
**The project is currently set to public, to make testing with mybinder easier. However, in its current state, this project cannot be shared with students, as it contains the notebook files with the answers for the assignment. It is important that before the course starts a separate github project is created without any answers.**

## How to install
1.	Download and install the latest version of anaconda
    -	https://www.anaconda.com/products/individual 
2.	Open an anaconda prompt (found in windows menu), and enter the following commands:
    - conda create --name pychEnv
        - Enter Y (for yes)
    -	conda activate pychEnv
    -	conda install git pip ipykernel
        - Enter Y (for yes)
    -	python -m ipykernel install --user --name pychEnv --display-name "Python (pychEnv)"
    -	pip install git+git://github.com/Nickp1993/Pych/
    -	You can now close this window
3.	Now every time you want to start jupyter notebook: open jupyter notebook (found in windows menu)
    -	Wait till a local server has started, your browser should open it automatically
    -   Navigate to the notebook you want to open and open it  
    -	In the menubar, click kernel > change kernel >  Python (pychEnv)
    -	You can now use this notebook


## Python dependencies
Pych requires the following packages: 'simpy', 'numpy', 'matplotlib.pyplot' and 'dataclasses'.

For faster simulation, PyCh can be used with [PyPy](https://www.pypy.org/).

## Contents
- 'src/PyCh' contains the source code of the package
- 'notebooks' contains the jupyter notebooks used in the course
- 'examples' contains some simulation examples in python 

## Jupyter notebooks
The jupyter notebooks used in this project can be tested in [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Nickp1993/PyCh/HEAD)

Note, to test the notebooks in Mybinder.org: rename "_PyCh.py" to "PyCh.py" in the notebooks folder
