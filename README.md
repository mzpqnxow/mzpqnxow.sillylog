# sillylog

A silly module for Python2/3 log handling

## More about this

The Python logging module provides very, very powerful and flexible logging capabilities. However, it is lacking in a "simple, but complete" logging mechanism. For this reason, I tend to be constantly rewriting logging code from scratch, or copying/pasting from old projects. Things I tend to want:

* Consistent naming for logging functions, regardless of scope
* Ability to easily define output format string specific to each log-level
* Ability to easily add log-levels to the logging system (e.g. logging.USER)
