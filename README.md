# sillylog

A silly module for Python2/3 log handling

## More about this

The Python logging module provides very, very powerful and flexible logging capabilities. However, it is lacking in a "simple, but complete" logging mechanism. For this reason, I tend to be constantly rewriting logging code from scratch, or copying/pasting from old projects. Things I tend to want:

* Consistent naming for logging functions, regardless of scope
* Ability to easily define output format string specific to each log-level
* Ability to easily add log-levels to the logging system (e.g. logging.USER)

## Maturity

*You* probably shouldn't use this. There's a lot of hardcoded stuff and it isn't really meant as an all purpose library, which is why it isn't published to PyPi. I'm curious how you might have even stumbled across this on GitHub. You must be pretty weird, or stalking me.

That all said, I will accept PR and issues happily. But for now, development is done because this is "good enough" for basic logging

## Caveats / Limitations

* This really isn't very dynamically configurable right now
* The settings that *I* like are more or less hardcoded
* A log file will be created in ~/log that you need to be aware of! Don't flood your disk or log sensitive stuff

## License

![License](img/BSD-3Clause.jpg)\
