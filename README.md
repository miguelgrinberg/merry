# merry

[![Build Status](https://travis-ci.org/miguelgrinberg/merry.svg?branch=master)](https://travis-ci.org/miguelgrinberg/merry)

Decorator based error handling for Python

## Installation

Merry is installed with pip:

    $ pip install merry

## Getting Started

The purpose of merry is to help you move error handling code away from your
application logic. Take, for example, this function, which embeds error
handling code:

```python
def write_to_file(filename, data):
    try:
        with open(filename, 'w') as f:
            f.write(data)
    except IOError:
        print('Error: can't write to file')
    except Exception as e:
        print('Unexpected error: ' + str(e))

write_to_file('some_file', 'some_data')
```

Even with this simple example, you can see how the indentation forced by the
try/except block makes the code much harder to read and visually follow.

Merry allows you to move exception handlers to external functions, so that
they don't interfere with the application logic:

```python
from merry import Merry

merry = Merry()

@merry._try
def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)

@merry._except(IOError)
def ioerror():
    print('Error: can't write to file')

@merry._except(Exception)
def catch_all(e):
    print('Unexpected error: ' + str(e)

write_to_file('some_file', 'some_data')
```

While in this example there are more lines of code after merry is used, the
key benefit is that the application logic, which is in the `write_to_file`
function, is now completely clean of try/except statements. The exception
handlers become auxiliary functions that can even be moved to a separate
module so that they stay completely out of the way.

## Access to the Exception Object

The decorated exception handlers can optionally take one argument. If you
include this argument, then merry sends the exception object.

```python
@merry._except(Exception)
def catch_all(e):
    print('Unexpected error: ' + str(e)
```

## The `else` and `finally` clauses

For cases that require a more complex try/except block, there are also
decorators available for `else` and `finally`:

```python
@merry._else
def else_clause():
    print('No exceptions where raised!')

@merry._finally
def finally_clause():
    print('Clean up time!')
```

## Returning values

Returning values from functions protected with the `try` decorator or the
corresponding `except`, `else` and `finally` handlers follow certain rules
that try to implement a behavior similar to a Python try/except:

- The value returned by a function decorated with the `try` decorator is
  normally returned to the caller.
- If there is an exception, then the value returned by the `except` handler
  that matches the exception is returned to the caller.
- The `else` handler only runs if the `try` function does not raise an
  exception and returns `None`
- If the `try` function returns `None` and there is an `else` handler, then
  its return value is given to the caller.
- If there is a `finally` handler and it returns a value that is not `None`,
  then this value takes the place of any other returned value.

## Passing context to error handlers

In many cases, exception handlers need to have access to application state to
do their work. When using merry, the `merry.g` object can be used as storage
of application state that needs to be accessible to error handlers:

```python
@merry._try
def app_logic():
    db = open_database()
    merry.g.database = db  # save it in the error context just in case
    # do database stuff here

@merry._except(Exception)
def catch_all():
    db = getattr(merry.g, 'database', None)
    if db is not None and is_database_open(db):
        close_database(db)
    print('Unexpected error, quitting')
    sys.exit(1)
```

## Debug mode

When working with debuggers, it is a good idea to let all exceptions reach the
top of the stack, so that the debugger handles them. With merry, if you enable
debug mode all exceptions bubble all the way up:

```python
merry = Merry(debug=True)
```

But when working in debug mode, there might be certain exceptions that are
expected to trigger and do not need to bubble up. For this reason, the debug
mode can be overriden by individual error handlers:

```python
@merry._except(IOError, debug=False)
def ioerror():
    # this function will run even in debug mode
    print('Error: can't write to file')
```

The reverse is also possible. If you are running with debug mode turned off,
but want to suspend an exception handler and have that exception bubble up,
just set `debug=True` for that handler.

## Logging

When an application is running in production mode, it is desired that all
errors are suppressed and instead they are sent to a log. Merry creates a
logger on which it writes all the exceptions it handles, include their
backtraces. This logger is a standard instance of the Python standard library
logging class.

The default logger instance is called `'merry'`, and can be referenced as
`merry.logger`. If desired, merry can hook up to a logger object owned by the
application:

```python
custom_logger = logging.getLogger('my_logger')
custom_logger.setLevel(logging.INFO)
merry = Merry(logger_name='my_logger')
```

By default, the logger created by merry does not have any handlers attached,
so caught exceptions will not be logged anywhere. If you want exceptions to be
written to the console, you can add a handler that writes to stderr:

```python
merry = Merry()
merry.logger.addHandler(logging.StreamHandler(sys.stderr))
```

The log level and format can be adjusted as well. See the documentation on the
logging module for more information on how to do this.
