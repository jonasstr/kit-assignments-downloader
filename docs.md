# Documentation

## Options

Show the help message (can be used together with a command):
```
kit-dl --help
```
Show general information about the current user and courses:
```
kit-dl --info
```

## Commands

### Setup
Start the command line based setup assistant or change previous settings.  
Usage: `kit-dl setup [OPTIONS]`  

| Option           |  Description                                                                                                                                                                             
|------------------|--------------------------------------------------------------------------------------------------------------|
| `-cf`, `--config` | Allows you to change the download locations for your courses (updates the config.yml file). Note: This can only be used if `kit-dl setup` or `kit-dl setup --user` was used before.                                                              |
| `-u`, `--user`    | Change user specific settings such as the ilias user name and password or the root path for downloading                                                                                                                     assignments (updates the user.yml file).                                                                                       |

### Update
Update one or more courses by downloading the latest assignments.  
Usage: `kit-dl update [OPTIONS] [COURSE_NAMES]...`

| Option           |  Description                                                                                                                                                                             
|------------------|--------------------------------------------------------------------------------------------------------------|
| `-a`, `--all`       | Update assignment directories for all your current courses (default if no `COURSE_NAMES                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             ` have been specified).                                             |
| `-hl`, `--headless` /  `-sh`, `--show` | Start the browser in headless mode (no visible UI) (default) or open your browser when downloading assignments to view the navigation between sites live.                                                                |

### Get
Download one or more assignments from your courses (specified during setup) with the given assignment number(s).  
Usage: `kit-dl get [OPTIONS] [COURSE_NAMES]... ASSIGNMENT_NUM`

`ASSIGNMENT_NUM` can be specified in different ways:  
* a single assignment: `a`
* multiple: `a-b` (from `a` to and including `b`) or `a,b,c,..` (all in the sequence)



## Libraries
- [selenium](https://github.com/SeleniumHQ/selenium)
- [click](https://github.com/pallets/click)
- [ruamel.yaml](https://bitbucket.org/ruamel/yaml)
- [colorama](https://github.com/tartley/colorama)
