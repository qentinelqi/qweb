# How to install QWeb to a Mac with Apple silicon (ARM/M1)

QWeb requires some packages that are hardware dependent and don't install on M1 based Mac using pip. 
Here are instructions on how to do a custom installation for those packages.

Prerequisites: Command Line Tools and [Homebrew](https://docs.brew.sh/Installation) installed.

## 1. Install Miniforge

Go to [Miniforge](https://github.com/conda-forge/miniforge) page and download installer for OS X *arm64 (Apple Silicon)*.
You should now have the installer in *Downloads* folder.

Next open terminal and navigate to *Downloads* folder. Make the installer executable and run it:
```bash
    chmod +x Miniforge3-MacOSX-arm64.sh
    ./Miniforge3-MacOSX-arm64.sh
```
You can accept the defaults and answer Yes to all questions. Now make sure that Miniforge3 is the path environments
use from here on.
```bash
    ~/miniforge3/condabin/conda
```
And
```bash
    ~/miniforge3/condabin/conda init
```
Last step is to make sure we use the preferred channel with conda.
```bash
    conda config --add channels conda-forge
    conda config --set channel_priority strict
```
Now you should have Miniforge3 installed.

## 2. Create Python 3.9 environment

Using the conda command from Miniforge3 create a new environment and activate it.
```bash
    conda create -n qweb_env python=3.9
    conda activate qweb_env
```

## 3. Install ffmpeg
QWeb uses ffmpeg for handling screenshots. It is not available by default and needs to be installed separately using
Homebrew. Open new terminal window and type:
```bash
    brew install ffmpeg
```

## 4. Install scipy
Go back to terminal where you have Python 3.9 environment activated. Use conda to install correct version of scipy
package:
```bash
    conda install scipy=1.5.*
```

## 5. Clone QWeb (but don't install yet!)
Go to your project folder and clone QWeb from GitHub:
```bash
    git clone https://github.com/qentinelqi/qweb.git
```
If git is not found you can install it with Homebrew.

## 6. Install scikit-image and change version requirement
Install scikit-image with conda:
```bash
    conda install scikit-image
```
Use pip to check the version of scikit-image package:
```bash
    pip list
```
Open *qweb/requirements.txt* and *qweb/setup.py* files to editor and find lines where scikit-image is mentioned for
Python versions greater than 3.6. Change the version to the one you have in your environment.

## 7. Install QWeb
Now QWeb can be installed to the environment. Installation needs to happen from the local clone where requirements
were modified in previous steps:
 ```bash
    cd qweb
    pip install -e .
```

## 8. Install browser driver
The last step is to use webdriver manager to install chromedriver. Install webdriver manager using pip:
 ```bash
    pip install webdrivermanager
```
Install chromedriver using webdriver manager:
 ```bash
    webdrivermanager --linkpath AUTO chrome
```
Now your environment should be ready!
