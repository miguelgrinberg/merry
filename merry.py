import inspect
import logging
from functools import wraps

getargspec = None
if getattr(inspect, 'getfullargspec', None):
    getargspec = inspect.getfullargspec
else:
    # this one is deprecated in Python 3, but available in Python 2
    getargspec = inspect.getargspec


class _Namespace:
    pass


def _wrap_async(fn):
    async def _inner(*args, **kwargs):
        if inspect.iscoroutinefunction(fn):
            return await fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs)
    return _inner


class Merry(object):
    def __init__(self, logger_name='merry', debug=False):
        self.__logger = logging.getLogger(logger_name)
        self.g = _Namespace()
        self.__debug = debug
        self.__except = {}
        self.__force_debug = []
        self.__force_handle = []
        self.__else = None
        self.__finally = None

    def _try(self, f):
        if inspect.iscoroutinefunction(f):
            @wraps(f)
            async def async_wrapper(*args, **kwargs):
                ret = None
                try:
                    ret = await f(*args, **kwargs)

                    # note that if the function returned something, the else clause
                    # will be skipped. This is a similar behavior to a normal
                    # try/except/else block.
                    if ret is not None:
                        return ret
                except Exception as e:
                    # find the best handler for this exception
                    handler = None
                    for c in self.__except.keys():
                        if isinstance(e, c):
                            if handler is None or issubclass(c, handler):
                                handler = c

                    # if we don't have any handler, we let the exception bubble up
                    if handler is None:
                        raise e

                    # log exception
                    self.__logger.exception('[merry] Exception caught')

                    # if in debug mode, then bubble up to let a debugger handle
                    debug = self.__debug
                    if handler in self.__force_debug:
                        debug = True
                    elif handler in self.__force_handle:
                        debug = False
                    if debug:
                        raise e

                    # invoke handler
                    return await _wrap_async(self.__except[handler])()
                else:
                    # if we have an else handler, call it now
                    if self.__else is not None:
                        return await _wrap_async(self.__else)()
                finally:
                    # if we have a finally handler, call it now
                    if self.__finally is not None:
                        alt_ret = await _wrap_async(self.__finally)()
                        if alt_ret is not None:
                            ret = alt_ret
                        return ret
            return async_wrapper
        else:
            @wraps(f)
            def wrapper(*args, **kwargs):
                ret = None
                try:
                    ret = f(*args, **kwargs)

                    # note that if the function returned something, the else clause
                    # will be skipped. This is a similar behavior to a normal
                    # try/except/else block.
                    if ret is not None:
                        return ret
                except Exception as e:
                    # find the best handler for this exception
                    handler = None
                    for c in self.__except.keys():
                        if isinstance(e, c):
                            if handler is None or issubclass(c, handler):
                                handler = c

                    # if we don't have any handler, we let the exception bubble up
                    if handler is None:
                        raise e

                    # log exception
                    self.__logger.exception('[merry] Exception caught')

                    # if in debug mode, then bubble up to let a debugger handle
                    debug = self.__debug
                    if handler in self.__force_debug:
                        debug = True
                    elif handler in self.__force_handle:
                        debug = False
                    if debug:
                        raise e

                    # invoke handler
                    return self.__except[handler]()
                else:
                    # if we have an else handler, call it now
                    if self.__else is not None:
                        return self.__else()
                finally:
                    # if we have a finally handler, call it now
                    if self.__finally is not None:
                        alt_ret = self.__finally()
                        if alt_ret is not None:
                            ret = alt_ret
                        return ret
            return wrapper

    def _except(self, *args, **kwargs):
        def decorator(f):
            for e in args:
                self.__except[e] = f
            d = kwargs.get('debug', None)
            if d:
                self.__force_debug.append(e)
            elif d is not None:
                self.__force_handle.append(e)
            return f
        return decorator

    def _else(self, f):
        self.__else = f
        return f

    def _finally(self, f):
        self.__finally = f
        return f

    # namespace accessors

    def __getattr__(self, key):
        return getattr(self.g, key)

    def __setattr__(self, key, value):
        if hasattr(self, key):
            super().__setattr__(key, value)
        else:
            setattr(self.g, key, value)

    def __delattr__(self, key):
        if not hasattr(self, key):
            delattr(self.g, key)

    def __dir__(self):
        return dir(self.g)
