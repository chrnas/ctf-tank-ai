## Getting started

Clone this repo.
```
git clone https://gitlab.liu.se/tdde25/ctf https://github.com/chrnas/tank-ai-game.git
cd ctf
```

Code does not work on python 3.12
Check python version using python3 --version
```
python3 --version
```

Install dependencies, game does not work on newer versions:
```
pip install pymunk==5.7.0
pip install pygame==2.0.1
```

Use the following command to check that the versions are correct:
```
pip freeze
```

To run the game with only ai
```
python ctf.py
```

To run the game in singleplayer mode
```
python ctf.py -s
```

To run the game in multiplayer mode
```
python ctf.py -m
```


Next go to our [wiki](https://gitlab.liu.se/tdde25/ctf/wikis/home) and get started on the tutorials.
