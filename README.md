# KIT Assignments Downloader

An unofficial KIT assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).

## Why do I need this?

If you feel like logging in to Ilias each week and downloading the latest assignments manually takes too much time, then this project might be for you. Just type in ``kita update`` followed by the name of the class and kita will automatically log in to your Ilias account, download the latest assignments of all your classes and copy them to your preferred KIT folder.

## Installation and setup

If you are on Windows, make sure [Python 3](https://www.python.org/downloads/) is installed on your computer.  
Then open a console and type:

    pip install kita
  
Before you can download anything, kita needs to know your ilias user name and password. This command will create a user.yml file containing your login credentials. To get started, type:

    kita setup
      
Note: Your user name and password will only be stored locally. **Never share the user.yml file!** Feel free to check out the source code for more info.

## Usage

After the setup is complete, you can start downloading assignments. Type `-h` or `--help` after a specific command for more information about that command. Use `--visible` or `-v` to open the browser instead of downloading the assignments in the background (default: `--headless`/`-hl`).  
If you want to add your own classes, see [...]

```
kita update [OPTIONS] [CLASS_NAMES]...
```
**Example:** `kita update la`  
Scans your 'Lineare Algebra 1' directory as specified during setup. Downloads the latest assignment for this class and renames the files.  

**Options:**
`--all`/`-a` update assignment directories for all your classes.

    kita get [OPTIONS] [CLASS_NAMES]... ASSIGNMENT_NUM
    
**Example:** `kita get la 9`  
Downloads the 9th assignment from your class Lineare Algebra 1. You can download assignments from multiple classes at once by separating the classes by a space, e.g: `kita get la gbi 9`.  
 
**Options:**: 
`--move`/`-mv`: move and rename your downloaded files if you have specified a location in the user.yml file.  
`--all`/`-a`: Download assignments for all your classes.  
  ```update```
  ```move```
  
 ## Adding your own classes
 
If you can't find a specific ilias class in the provided config.yml file, use the following command:
```
kita add
``` 
which will guide you through setting up your own classes.
Please consider [contributing]() your added classes, so that others will be able to download assignments for that class as well. 
