# Aureliano
Aureliano was created as a generic framework to automate some development tasks, with a main thought in mind; easy extensibility.

## Main Features
* New commands can be created quickly by creating a new drived class of `BaseCommand`. See [How to write new commands]() for more info.
* Commands' file can be used to run the same series of commands several times.
* Multiline commands to invoke the same command with different parameters:
  * Can be very useful one the command would unnecessarily execute the same initialization code every time you invoke. (Like connecting to a server or initalizing the environment)
  * Single and multiline comments are also supported.

## How to invoke
The best starting point would be `$Aureliano -h`
Aureliano can be invoked with one command at a time (-r), with a commands' file (-f) or in an interactive mode.

A test command is also present, well, obviously for testing. This is the one used in the following examples.
It is deactivated by default. To activate it, you just need to remove the '\'#\'' from [#from Commands.CmdTest import CmdTest](Commands/__init__.py)

### One command
Example:
```
$Aureliano -r test main ok
```

### Commands' files
Commands' can have one-liners like running the commands with "-r".
But can also include multiline commands (if supported by the command).

#### Mutliline commands
#### Comments


Examples can be found in [Test](Test)

### Interactive mode
Invoking `$Aureliano` starts it in interactive mode

## How to write new commands

## Status 
Aureliano is already useable and commands can be (\*relatively) easily added.


Check the project's [TODO list](TODO.md).

\**Well, you just need to know how to write regular expressions. ;-)*
