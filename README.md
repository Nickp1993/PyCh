# PyCh

PyCh is a Python package based on SimPy for discrete-event simulation.
It is a tool developed for the course "Analysis of production systems" (4DC10).
PyCh is a port of [Chi3](https://cstweb.wtb.tue.nl/chi/trunk-r9682/).

## Important
**The project is currently set to public, to make testing with mybinder easier. However, in its current state, this project cannot be shared with students, as it contains the notebook files with the answers for the assignment. It is important that before the course starts a separate github project is created without any answers.**

## How to install
1.	Download and install the latest version of anaconda
    -	https://www.anaconda.com/products/individual 
2.	Open an anaconda prompt (found in windows menu), and enter the following commands:
    - `conda create --name pychEnv`
        - Enter `y` (for yes)
    -	`conda activate pychEnv`
    -	`conda install git pip ipykernel`
        - Enter `y` (for yes)
    -	`python -m ipykernel install --user --name pychEnv --display-name "Python (pychEnv)"`
    -	`pip install git+git://github.com/Nickp1993/Pych/`
    -	Close this window (do not continue with the "how to use" without closing!)
3.	You have finished installation, continue with the "How to use" below to start a notebook

## How to use
1. Download the notebook files
    -   Click the green button above, and click download ZIP (or [click here](https://github.com/Nickp1993/PyCh/archive/refs/heads/main.zip))
    -   Extract the `notebooks` folder from the ZIP-file.
        - E.g. to `C:\4DC10\notebooks`
2. Every time you want to start jupyter notebook: 
    -   Open the anaconda prompt (found in windows menu)
    -   In anaconda, set the path to that of your notebooks folder by entering `cd X` with X the path of your notebooks folder
        - E.g. `cd C:\4DC10\notebooks`
    -   Enter `jupyter notebook`
    -	Wait till a local server has started, your browser should open it automatically, if not, [try clicking this links](http://127.0.0.1:8888/)
    -   Open one of the notebooks (files with an `.ipynb` extension)
    -	In the menubar, click kernel > change kernel >  Python (pychEnv)
3. You can now use this notebook!
    -   You can now click run to execute the cells of the notebook one-by-one (jupyter notebooks work top-down)
    -   [Click this link for information on how jupyter notebook works](https://realpython.com/jupyter-notebook-introduction/)

## Other information

### Python dependencies
Pych requires the following packages: 'simpy', 'numpy', 'matplotlib.pyplot' and 'dataclasses'.

For faster simulation, PyCh can be used with [PyPy](https://www.pypy.org/).

### Contents
- 'src/PyCh' contains the source code of the package
- 'notebooks' contains the jupyter notebooks used in the course
- 'examples' contains some simulation examples in python 

### Binder
The jupyter notebooks used in this project can be tested in [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Nickp1993/PyCh/HEAD)

Note, to test the notebooks in Mybinder.org: rename "_PyCh.py" to "PyCh.py" in the notebooks folder
