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

@merry._except(IOError)
def ioerror():
    print('Error: can't write to file')

@merry._except(Exception)
def catch_all(e):
    print('Unexpected error: ' + str(e)

@merry._try
def write_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(data)

write_to_file('some_file', 'some_data')
```

While in this example there is more total lines of code after merry is used,
the key benefit is that the application logic, which is in the `write_to_file`
function, is now completely clean of try/except statements. The exception
handlers become auxiliary functions that can be moved to a separate module so
that they stay out of the way.

The decorated exception handlers can take zero or one argument. If they take
an argument, then merry sends the exception object.

## The `else` and `finally` clauses

For cases where a more complex try/except block is required, there are also
decorators available for `else` and `finally`:

```python
@merry._else
def else_clause():
    print('No exceptions where raised!')

@merry._finally
def finally_clause():
    print('Clean up time!')
```

## Passing context to error handlers

In many cases, exception handlers need to have access to application state to
do their work. When using merry, the `merry.g` object can be used to set
application state that needs to be accessible to error handlers:

```python
@merry._except(Exception)
def catch_all():
    db = getattr(merry.g, 'database', None)
    if db is not None and is_database_open(db):
        close_database(db)
    print('Unexpected error, quitting')
    sys.exit(1)

@merry._try
def app_logic():
    db = open_database()
    merry.g.database = db  # save it in the error context just in case
    # do database stuff here
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
    print('Error: can't write to file')
```

## Logging

Conversely, when an application is running in production mode, it is desired
that all errors are suppressed and instead they are sent to a log. Merry
creates a logger on which it writes all the exceptions it handles, include
their backtraces. This logger is a standard instance of the Python standard
library logging class.

The logger instance is called `'merry'` by default, and can be referenced as
`merry.logger`. If desired, merry can hook up to a logger owned by the
application:

```python
custom_logger = logging.getLogger('my_logger')
custom_logger.setLevel(logging.INFO)
merry = Merry(logger_name='my_logger')
```

By default, the logger created by merry does not have any handlers attached,
so caught exceptions will not be printed anywhere. If you want exceptions
to be printed to the console, you can add a handler that writes to stderr:

```python
merry = Merry()
merry.logger.addHandler(logging.StreamHandler(sys.stderr))
```

The log level and format can be adjusted as well. See the documentation on the
logging module for more information on how to do this.
