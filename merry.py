from functools import wraps
import inspect
import logging


class _Namespace:
    pass


class Merry(object):
    def __init__(self, logger_name='merry', debug=False):
        self.logger = logging.getLogger(logger_name)
        self.g = _Namespace()
        self.debug = debug
        self.except_ = {}
        self.force_debug = []
        self.force_handle = []
        self.else_ = None
        self.finally_ = None

    def _try(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                f(*args, **kwargs)
            except Exception as e:
                # find the best handler for this exception
                handler = None
                for c in self.except_.keys():
                    if isinstance(e, c):
                        if handler is None or issubclass(c, handler):
                            handler = c

                # if we don't have any handler, we let the exception bubble up
                if handler is None:
                    raise e

                # log exception
                self.logger.exception('[merry] Exception caught')

                # if in debug mode, then bubble up to let a debugger handle
                debug = self.debug
                if handler in self.force_debug:
                    debug = True
                elif handler in self.force_handle:
                    debug = False
                if debug:
                    raise e

                # invoke handler
                if len(inspect.getargspec(self.except_[handler])[0]) == 0:
                    self.except_[handler]()
                else:
                    self.except_[handler](e)
            else:
                # if we have an else handler, call it now
                if self.else_ is not None:
                    self.else_()
            finally:
                # if we have a finally handler, call it now
                if self.finally_ is not None:
                    self.finally_()
        return wrapper

    def _except(self, *args, **kwargs):
        def decorator(f):
            for e in args:
                self.except_[e] = f
            d = kwargs.get('debug', None)
            if d:
                self.force_debug.append(e)
            elif d is not None:
                self.force_handle.append(e)
            return f
        return decorator

    def _else(self, f):
        self.else_ = f
        return f

    def _finally(self, f):
        self.finally_ = f
        return f
