# KIT Assignments Downloader

An unofficial KIT assignments downloader for [ilias.studium.kit.edu](http://ilias.studium.kit.edu/).

## Why do I need this?

If you feel like logging in to Ilias each week and downloading the latest assignments manually takes too much time, then this project might be for you. Just type in ``kita update`` followed by the name of the class and kita will automatically log in to your Ilias account, download the latest assignments of all your classes and copy them to your preferred KIT folder.


## Installation and usage

If you are on Windows, you need to make sure [Python 3](https://www.python.org/downloads/) is installed on your computer.  
Then open a console and type:

    pip install kita
  
Before you can download anything, kita needs to know your ilias and user name and password. This command will create a user.yml file containing your login credentials. To get started, type:

    kita setup
      
Note: Your user name and password will only be stored locally at... **Never share the user.yml file with anyone!** Feel free to check out the source code for more info.
