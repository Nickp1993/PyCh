from setuptools import setup

setup(
    name='PyCh',
    version='0.1',
    url='https://github.com/Nickp1993/4DC10',
    license='MIT',
    author='N. Paape',
    author_email='n.paape@tue.nl',
    description='Simulation tool for 4DC10',
    packages=['PyCh'],
    install_requires=['simpy', 'dataclasses', 'numpy', 'matplotlib.pyplot' ]
)
