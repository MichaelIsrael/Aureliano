# Aureliano
Aureliano was created as a generic framework to automate some development tasks, with a main thought in mind; easy extensibility.

## Main Features
* New commands can be quickly added by creating a new drived class of `BaseCommand`. See [How to write new commands](#how-to-write-new-commands) for more info.
* Commands' file can be used to run the same series of commands several times.
* Multiline commands to invoke the same command with different parameters:
  * Can be very useful when the command would unnecessarily execute the same initialization code every time you invoke it. (Like connecting to a server or initalizing an environment)
  * Single and multiline comments are also supported.

## How to invoke
The best starting point would be `$Aureliano -h`.
Aureliano can be invoked with one command at a time (-r), with a commands' file (-f) or in an interactive mode.

A test command is also present, well, obviously for testing. This is the one used in the following examples.
It is deactivated by default. To activate it, you just need to remove the `'#'` from `#from Commands.CmdTest import CmdTest` in [Commands/__init__.py](Commands/__init__.py)

### One command
Example:
```
$Aureliano -r test main ok
```

### Commands' files
Commands' can have one-liners like running the commands with "-r".
But can also include multiline commands (if supported by the command).


#### Mutliline commands
Multiline commands can be invoked by typing the command and its main parameters plus a `{` following by on or more lines, each containing a set of multiline parameters. The scope ends with `}` in a new line.

#### Comments
There are two types of comments; single and multi-line.
Both can be used also inside the scope of multiline command.

##### Single line comments
Single line comments start with a '#'.

##### Multiline comments
Mutliline comments can be made as following.
```
#<
	First comment.
	Second comment.
#>
```



Example:
```
test MyName{
	#First action to execute
	ok
	#Second action to execute
	error_message
#<
	A few comments
	ok (A valid but commented action)
#>
}

```

_More examples can be found in [Test](Test)_

### Interactive mode
Invoking `$Aureliano` starts it in interactive mode


## How to write new commands
1. Create a child class of BaseCommand, whose name must start with "Cmd" (silly I know but there is always a \*\*reason).
2. Write what it does in its member variable \_BriefHelpStr.
3. Write the regular expressions of its parameters. (See [How parameters definition works](#how-parameters-definition-works))
4. Implement its run(self)-method.

### How parameters definition works
This is where it gets tricky.
There are two member variables responsible for the whole story:
```
SingleParametersRegex
MultiParametersRegex
```

SingleParametersRegex has to be implemented. Only MultiParametersRegex is allowed to remain None.
They are expected to be of type OrderedDict. _(But hey, this is Python! So as long as it looks like an OrderedDict you can use whatever type you want as long as you know what you are doing) ;-)_

Whether your command supports multiline or not depends on whether you implement MultiParametersRegex or leave it `None`.

when invoked, BaseCommand will do the following:
1. Go through the entries of both Parameters' OrderedDicts and create one Regex for each.
2. Depeding on whole the command was invoked:
  * If as a one-liner, both Regexes are assembled and executed on the whole command.
  * If as a multiline, the singleLine Regex is exectued on the main parameters (first line) and the Multiline Regex on every followling line.
3. A internal member dictionary `self.Args` is created and all parameters are stored in it.
4. The run() function is executed.

For a better understanding, see the implementation of the [test command](Aureliano/Commands/CmdTest.py)


## Status 
Aureliano is already useable and commands can be (\*relatively) easily added.

WARNING: The project started as a local script, and was modified, modularized and some private commands were removed before commiting it. So there might be several issues with it. Still a few tests were ran and worked..

Check the project's [TODO list](TODO.md).



\**Well, you just need to know how to write regular expressions. ;-)*
\*\* *The idea behind restricting the names of Commands to start with "Cmd" is to make it possible to create an intermediate class, a type of commands if you will, that serves as a parent class for several commands  and still wouldn't show up as a command itself (since its name wouldn't start with "Cmd").*
