# Tank Ai Game

Tank Ai Game is a 2d python capture the flag game with player and ai controlled tanks.

## Installation

Clone this repo.
```
git clone https://gitlab.liu.se/tdde25/ctf https://github.com/chrnas/tank-ai-game.git
cd ctf
```

Code does not work with newer versions of python.
Check that python version 3.9 or lower using python3 --version
```
python3 --version
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.
Install dependencies, game does not work on newer versions:
```
pip install pymunk==5.7.0
pip install pygame==2.0.1
```

## Usage

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

## License

[MIT](https://choosealicense.com/licenses/mit/)
