## Getting started

Clone this repo and then remove the `.git` folder:
```
git clone https://gitlab.liu.se/tdde25/ctf
cd ctf
rm -rf .git
```
Then add your own git folder per the instructions on the TDDE25 git tutorial.


We also need to add the required libraries pymunk and pygame.
```
pip3 install --upgrade --user setuptools pip
cd ~/.local/bin
./pip3 install --user pymunk==5.7.0
./pip3 install --user pygame==2.0.1
```
Now, all these local installations will end up in `~/.local/lib/python3.4/site-packages`, so we'll need to add it to our `PYTHONPATH`.
We'll do this by modyfying the bash file that gets run every time we open up a new terminal (`~/.bashrc`). Add this line to your `~/.bashrc` file:
```
export PYTHONPATH = "~/.local/lib/python3.4/site-packages:${PYTHONPATH}"
```

If you are want to install them on your own computer simply use:
```
pip install pymunk==5.7.0
pip install pygame==2.0.1
```

Use the following command to check that the versions are correct:
```
pip freeze
```


Next go to our [wiki](https://gitlab.liu.se/tdde25/ctf/wikis/home) and get started on the tutorials.
