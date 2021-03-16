# Alfred
A natural language terminal interface

# Overview

Alfred is a natural language terminal interface, which aims to provide a (simple) way to perform terminal commands with natural language. If you're wondering where Alfred's name comes from, look no further than everyone's favorite Gotham City savior, Batman. Just as Alfred maintains the Batcave, so too does the Alfred chatbot maintain your terminal environment for you. Simply ask him to do one of the (admittedly, few) things he knows how to do, and he'll try his best to help you out.

# Features

Alfred currently understands how to do the following:
* List directories with `ls`
* Move files/directories with `mv`
* Copy files with `cp`
* Remove files/directories with `rm` (recursive removals are implemented with `rm -rf`, so be aware of the risk associated with that)
* Execute arbitrary commands, e.g. "Do `<command>`"
* Chain commands together conjunctively, e.g. "List the contents of `dir` then move everything in `dir` to `dir2`"

Alfred also has a very limited "memory" -- he can remember the last path you mention, and recall it for the word "there", e.g. "List the contents of `dir` then move everything from there to `dir2`".

# Installation & Use

To use Alfred, clone this repo and execute `python main.py` from the root project directory (your specific Python command may be different, but Alfred requires Python 3.7+ to run).

When talking with Alfred, all paths must be specified either absolutely or relative to the directory he's running in, otherwise he won't be able to find them.

# Known Issues

Alfred isn't without his flaws unfortunately; here are current known issues to be aware of:
1. Alfred doesn't know how to handle Oxford commas, so make sure not to include two conjunctive terms in a row (e.g. a comma and then "and").
2. Alfred also doesn't understand when you Include backticks in any terminal input, so please don't confuse him with that :(
