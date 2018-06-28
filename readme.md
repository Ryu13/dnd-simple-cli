Prerequisites:
    1. Ensure Python is installed (2.7.13 is supported, 3.x may encounter issues)

Instructions:
    1. Navigate into this directory after pulling it down via Git or some other means.
    2.  `battle.py` or `*path*/python battle.py` is the base command.
        This needs to be run with the `-b *relative_path*` flag or `--battle=*relative_path*`
        This currently consists of a `.json` file that spells out the list of enemies.
        This file should be constructed in the form
        ```
        {
            "monsters": [{
                "NAME": "monster1",
                "AC": 10,
                "HP": 40
            }]
        }
        ```
    
        Battle files should be created under the `.battles` folder to ensure no changes are detected by Git.
        Sample battles are located under `./sample-battles` and can be easily run with `battle.py -s X` or `battle.py --sample=X` where X is the sample battle num 

Supported monster attribute keys:
    NAME: A string with the monster name, this should be manipulated such that any monster template used is distinct e.g.   Vampire1, Vampire2, etc...

    AC: The armor class of the enemy. This is currently only for display purposes and there are NO attack rolls performed by the system. Perform these with your dice or however you wish until attack rolls are built in.

    HP: The rolled health of the enemy. This does not yet accept a string formula from which to roll (coming soon)

Future battle.py Updates:
    1. Formula rolls for battle json hp values
    2. monster attribute key: `file` which will allow monster template to be pulled from another local template (this should only contain formula HP). Reused templates in a monster list will be generated as: `*template_name* (*count*)`
    3. Optional attack rolls that will be compared to monster AC if option enabled
    4. Other cool stuff!
    5. Other features brought to you by users like you! ... Please make an issue request before any Pull Request to ensure the functionality is actually desired.

General Future Updates:
    Other utils aside from `battle.py` are also planned. These include monster template generation.