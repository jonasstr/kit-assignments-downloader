# KIT Assignments Downloader 
[![Build Status](https://travis-ci.com/jonasstr/scripts.svg?token=KxpvyZCyyQVwpjRDjaJm&branch=master)](https://travis-ci.com/jonasstr/scripts)

An unofficial assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).  



## Why do I need this?

With kita, keeping your assignments up to date has become a thing of the past.  
Kita automatically logs in to your ilias account, downloads the latest assignment of all your classes and moves them to the correct folders in your KIT directory - with just one command.

*Contents*: **[Requirements](#requirements)** | **[Installation and setup](#installation-and-setup)** | **[Getting started](#getting-started)** | **[Supported courses](#supported-courses)** | **[Documentation](#documentation)** | **[Adding new courses](#adding-new-courses)** | **[License](#license)**

## Requirements
Platform: **Windows**   
Browser: **Firefox**  
Support for more operating systems and browsers may be added in the future.  
Make sure [Python 3](https://www.python.org/downloads/) (including pip and tkinter) is installed on your computer.

## Installation and setup
 
To install this package open a console and type:

    pip install kita
  
To complete the installation use the following command:

    kita setup      
Note: The setup assistant requires you to input your ilias user name and password which will be stored locally in a file called user.yml. **Do not share this file!**

## Getting started

After the setup is complete, you can start downloading assignments. Type `-h` or `--help` after a specific command for more information about that command. For a list of currently supported courses see [supported courses](#supported-courses).

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
**Example:** `kita get la gbi 10-12` or `kita get la gbi 10,11,12`  
Download the assignments #10 to #12.
  
 ## Supported courses
 Here is a list of all currently supported courses (from Ilias and external sites):  
 * GBI: Grundbegriffe der Informatik
 * HM: Höhere Mathematik 1 ([http://www.math.kit.edu/iana2/edu/hm1info2018w/de](http://www.math.kit.edu/iana2/edu/hm1info2018w/de))
 * LA: Lineare Algebra 1
 * PRG: Programmieren
 
 ## Documentation
 See full [documentation](https://github.com/jonasstr/scripts/blob/master/docs.md).
  
 ## Adding new courses
 
If you can't find a specific course in the list above, use the following command:
```
kita add
``` 
which will guide you through adding your own courses. Please consider [contributing]() your newly created courses so that others will be able to download assignments for them as well. 

## License
[MIT](https://github.com/jonasstr/scripts/blob/master/LICENSE)
