
# Dirwatcher

This long running program continuously searches text files within a directory for a specific "magic" word.

## running the program

```
$ python dirwatch.py -i 10 test
```
the above will launch the program to run at 10 second intervals and to search the "test" directory.
It will search for files within the directory and will then search the directory line by line, logging every time the "magic" word is found.
If the program is left to run, and you change the text files and add more magic words, it should log where the magic word is found, and it should only log a new magic word found once.

### CMD line help

usage:
```
$ python dirwatcher.py [-h], interval [-i], directory, magic
```

### error handling
The point of the program is to keep running if errors are encountered, so if it doesn't find the directory in question, it will keep running to see if the directory appears.
If the directory isn't there, once that directory is created, such as in the case of a logfile, it will then run through the program as normal.

