# KIT Assignments Downloader 
[![Build Status](https://travis-ci.org/jonasstr/kit-assignments-downloader.svg?branch=master)](https://travis-ci.org/jonasstr/kit-assignments-downloader)

An unofficial assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).  

## Why do I need this?

With kit-dl, keeping your assignments up to date has become a thing of the past.  
Kita automatically logs in to your ilias account, downloads the latest assignment of all your classes and moves them to the correct folders in your KIT directory - with just one command.

## Requirements
Platform: **Windows**   
Browser: **Firefox**  
Support for more operating systems and browsers may be added in the future.  
Make sure [Python 3](https://www.python.org/downloads/) (including pip and tkinter) is installed on your computer.

## Installation and setup
 
To install this package open a console and type:

    pip install kit-dl
  
To complete the installation use the following command:

    kit-dl setup      
Note: The setup assistant requires you to input your ilias user name and password which will be stored locally in a file called user.yml. **Do not share this file!**

## Getting started

After the setup is complete, you can start downloading assignments. Type `-h` or `--help` after a specific command for more information about that command. For a list of currently supported courses see section supported courses.

Download the latest assignments for all your courses:
```
kit-dl update
```
---
You can also update one or more specific courses:
```
kit-dl update [COURSE_NAMES]...
```
**Example:** `kit-dl update la gbi`  
Update your 'Lineare Algebra I' and 'Grundbegriffe der Informatik' assignments.

---
If you only want to download specific assignments you can use:
```
kit-dl get [COURSE_NAMES]... ASSIGNMENT_NUM
```
**Example:** `kit-dl get la gbi 12`  
Download the assignment #12 from both 'Lineare Algebra I' and 'Grundbegriffe der Informatik'.  
**Example:** `kit-dl get la gbi 10-12` or `kit-dl get la gbi 10,11,12`  
Download the assignments #10 to #12.
  
 ## Supported courses
 Here is a list of all currently supported courses (from Ilias and external sites):  
 * GBI: Grundbegriffe der Informatik
 * HM: Höhere Mathematik 1 ([http://www.math.kit.edu/iana2/edu/hm1info2018w/de](http://www.math.kit.edu/iana2/edu/hm1info2018w/de))
 * LA: Lineare Algebra 1
 * PRG: Programmieren
 
 ## Documentation
 See full [documentation](https://github.com/jonasstr/kit-assignments-downloader/blob/master/docs.md).
  
 ## Adding new courses
 
If you can't find a specific course in the list above, feel free to open a pull request.  
A command line assistant similar to `setup` is currently a planned feature.

## License
[MIT](https://github.com/jonasstr/kit-assignments-downloader/blob/master/LICENSE)
