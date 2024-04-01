# `lute3`

Learning Using Texts v3.

Lute is for learning foreign languages through reading.  `lute3` is a rewrite of the original Lute PHP application in Python and Flask.  See the [Lute manual](https://luteorg.github.io/lute-manual/) for more detail, and notes about installation.


## Requirements

Python 3.8+ (tested with python 3.8 through 3.11)

Japanese learners will also need to install MeCab.

## Install

`lute3` installs various dependencies, so you should install it in a virtual environment.  For example, using `venv`:

Create a new folder (e.g. `lute3`) anywhere on your system.

```
# Set up the virtual environment
python3.8 -m venv myenv

# Activate it (Mac or *nix)
source myenv/bin/activate

# (on Windows: myenv\Scripts\activate)

# Install everything.  Note the package name is lute3!
pip install lute3

# Start lute
python -m lute.main

# Open your web browser to http://localhost:5000
# When done, hit Ctl-C

# Stop the virtual environment.
deactivate
```

Once everything is installed, for future runs you'll just need to go into `lute3` folder created above and:

```
source myenv/bin/activate
python -m lute.main
```