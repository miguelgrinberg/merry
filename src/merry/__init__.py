from functools import wraps
import inspect
import logging


class _Namespace:
    pass


class Merry:
    """Initialze merry.

    :param logger_name: the logger name to use. The default is ``'merry'``.
    :param debug: set to ``True`` to enable debug mode, which causes all
                  errors to bubble up so that a debugger can catch them. The
                  default is ``False``.
    """
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
        """Decorator that wraps a function in a try block.

        Example usage::

            @merry._try
            def my_function():
                # do something here
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            ret = None
            try:
                ret = f(*args, **kwargs)

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
                if len(inspect.getfullargspec(self.except_[handler])[0]) == 0:
                    ret = self.except_[handler]()
                else:
                    ret = self.except_[handler](e)
            else:
                # if we have an else handler, call it now
                # note that if the main function returned something, the else
                # clause will be skipped. This is a similar behavior to a
                # normal try/except/else block.
                if ret is None and self.else_ is not None:
                    ret = self.else_()
            finally:
                # if we have a finally handler, call it now
                # if this function returns a value, it replaces what the main
                # function returned.
                if self.finally_ is not None:
                    alt_ret = self.finally_()
                    if alt_ret is not None:
                        ret = alt_ret
            return ret

        @wraps(f)
        async def async_wrapper(*args, **kwargs):
            ret = None
            try:
                ret = await f(*args, **kwargs)

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
                if len(inspect.getfullargspec(self.except_[handler])[0]) == 0:
                    ret = self.except_[handler]()
                else:
                    ret = self.except_[handler](e)
                if inspect.isawaitable(ret):
                    ret = await ret
            else:
                # if we have an else handler, call it now
                # note that if the main function returned something, the else
                # clause will be skipped. This is a similar behavior to a
                # normal try/except/else block.
                if ret is None and self.else_ is not None:
                    ret = self.else_()
                    if inspect.isawaitable(ret):
                        ret = await ret
            finally:
                # if we have a finally handler, call it now
                # if this function returns a value, it replaces what the main
                # function returned.
                if self.finally_ is not None:
                    alt_ret = self.finally_()
                    if inspect.isawaitable(alt_ret):
                        alt_ret = await alt_ret
                    if alt_ret is not None:
                        ret = alt_ret
            return ret

        return async_wrapper if inspect.iscoroutinefunction(f) else wrapper

    def _except(self, *args, **kwargs):
        """Decorator that registers a function as an error handler for one or
        more exception classes.

        Example usage::

            @merry._except(RuntimeError)
            def runtime_error_handler(e):
                print('runtime error:', str(e))

        :param args: the list of exception classes to be handled by the
                     decorated function.
        :param kwargs: configuration arguments. Pass ``debug=True`` to enable
                       debug mode for this handler, which bubbles up all
                       exceptions. Pass ``debug=False`` to prevent the error
                       from bubbling up, even if debug mode is enabled
                       globally.
        """
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
        """Decorator to define the ``else`` clause handler.

        Example usage::

            @merry._else
            def else_handler():
                print('no exceptions were raised')
        """
        self.else_ = f
        return f

    def _finally(self, f):
        """Decorator to define the ``finally`` clause handler.

        Example usage::

            @merry._finally
            def finally_handler():
                print('clean up')
        """
        self.finally_ = f
        return f
