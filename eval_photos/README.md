# Eval photos

`capstone_eval.py` reads `labels.json` from this folder. Copy `labels.example.json` to `labels.json` and fill it in by hand.

- **wardrobe**: photos of clothes, with every visible item listed by category (`tops, bottoms, outerwear, shoes, accessories`). Label what a person would count, *before* you see what the model says. The eval scores how many labeled items got a prediction in the same category.
- **profile**: full-body photos of one person. Each one is analyzed every trial, and the eval reports whether the undertone came out the same across all trials.
- **bad**: real photos that should be refused: food or a landscape (expect 422 from scan), a group photo (expect 422 from profile). Six synthetic bad inputs (text file, empty, 9 MB, blank, corrupt) run automatically, with no files needed.
- **occasions**: run against the example wardrobe. An outfit passes when it names at least 2 owned items and invents none.

Only commit photos you're comfortable making public, and only photos of people who agreed. You can keep the images out of git (add `eval_photos/*.jpg` to `.gitignore`) and commit just `labels.json` and the results.
