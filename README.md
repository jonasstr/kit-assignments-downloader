# KIT Assignments Downloader

An unofficial KIT assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).


## Why do I need this?

Using *kita*, you will not have to care about keeping your assignments up to date **ever again**.  
*Kita* automatically logs in to your ilias account, downloads the latest assignment of all your classes and moves them to the correct folders in your KIT directory - with just one command.

*Contents*: **[Requirements](#requirements)** | **[Installation and setup](#installation-and-setup)** | **[Getting started](#getting-started)** | **[Supported courses](#supported-courses)** | **[Adding new courses](#adding-new-courses)**

## Requirements

If you are using Windows, make sure [Python 3](https://www.python.org/downloads/) (including pip and tkinter) is installed on your computer. Also note that kita currently only supports the **Firefox** browser.

## Installation and setup
 
To install this package open a console and type:

    pip install kita
  
To complete the installation use the following command:

    kita setup
      
Note: The setup assistant requires you to input your ilias user name and password which will be stored locally in a file called user.yml. **Do not share this file!**

## Getting started

After the setup is complete, you can start downloading assignments. Type `-h` or `--help` after a specific command for more information about that command. For a list of currently supported courses see [Supported courses](#supported-courses).

Download the latest assignments for all your courses:
```
kita update
```
---
You can also update one or more specific courses:
```
kita update [COURSE_NAMES]...
```
**Example:** `kita update la gbi`  
Update your 'Lineare Algebra I' and 'Grundbegriffe der Informatik' assignments.

---
If you only want to download specific assignments you can use:
```
kita get [COURSE_NAMES]... ASSIGNMENT_NUM
```
**Example:** `kita get la gbi 12`  
Download the assignment #12 from both 'Lineare Algebra I' and 'Grundbegriffe der Informatik'.  
**Example:** `kita get la gbi [10-12]` or `kita get la gbi [10,11,12]`  
Download the assignments #10 to #12.
  
 ## Supported courses
 Here is a list of all currently supported courses (from Ilias and external sites):  
 * GBI: Grundbegriffe der Informatik
 * HM: Höhere Mathematik 1 ([http://www.math.kit.edu/iana2/edu/hm1info2018w/de](http://www.math.kit.edu/iana2/edu/hm1info2018w/de))
 * LA: Lineare Algebra 1
 * PRG: Programmieren
  
 ## Adding new courses
 
If you can't find a specific ilias course in list above, use the following command:
```
kita add
``` 
which will guide you through adding your own courses. Please consider [contributing]() your newly created courses, so that others will be able to download assignments for them as well. 

## License
[MIT](https://github.com/jonasstr/scripts/blob/master/LICENSE)
