# KIT Assignments Downloader

An unofficial KIT assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).

## Why do I need this?

Using *kita*, you will **NEVER** have to care about keeping your assignments up to date ever again.  
*Kita* automatically logs in to your ilias account, downloads the latest assignment of all your classes and moves them to the correct folders in your KIT directory - with just one command.

## Requirements

If you are using Windows, make sure [Python 3](https://www.python.org/downloads/) (including pip and tkinter) is installed on your computer. Also note that kita currently only supports the **Firefox** browser.

## Installation and setup
 
To install this package open a console and type:

    pip install kita
  
To complete the installation use the following command:

    kita setup
      
Note: The setup assistant requires you to input your ilias user name and password which will be stored locally in a file called user.yml. **Do not share this file!**

## Getting started

After the setup is complete, you can start downloading assignments. Type `-h` or `--help` after a specific command for more information about that command.  
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
  
 ## Supported classes
 Here is a list of all currently supported classes (from Ilias and external sites):  
 * GBI: Grundbegriffe der Informatik
 * HM: Höhere Mathematik 1 ([http://www.math.kit.edu/iana2/edu/hm1info2018w/de](http://www.math.kit.edu/iana2/edu/hm1info2018w/de))
 * LA: Lineare Algebra 1
 * PRG: Programmieren
  
 ## Adding new classes
 
If you can't find a specific ilias class in the above list of supported classes, use the following command:
```
kita add
``` 
which will guide you through setting up your own classes. Please consider [contributing]() your added classes, so that others will be able to download assignments for that class as well. 
