from io import StringIO
import logging
import pytest
from merry import Merry


class TestMerry:
    def test_simple_except(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        f()
        assert m.g.except_called

    @pytest.mark.asyncio
    async def test_async_simple_except(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert m.g.except_called

    def test_simple_except2(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv(e):
            assert isinstance(e, ZeroDivisionError)
            m.g.except_called = True

        @m._try
        def f():
            1/0

        f()
        assert m.g.except_called

    @pytest.mark.asyncio
    async def test_async_simple_except2(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv(e):
            assert isinstance(e, ZeroDivisionError)
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert m.g.except_called

    def test_except_parent(self):
        m = Merry()
        m.g.except_called = False

        @m._except(Exception)
        def catch_all(e):
            pass

        @m._except(ArithmeticError)
        def arith_error(e):
            assert isinstance(e, ZeroDivisionError)
            m.g.except_called = True

        @m._except(BaseException)
        def base_error(e):
            pass

        @m._except(ValueError)
        def value_error(e):
            pass

        @m._try
        def f():
            1/0

        f()
        assert m.g.except_called

    @pytest.mark.asyncio
    async def test_async_except_parent(self):
        m = Merry()
        m.g.except_called = False

        @m._except(Exception)
        def catch_all(e):
            pass

        @m._except(ArithmeticError)
        async def arith_error(e):
            assert isinstance(e, ZeroDivisionError)
            m.g.except_called = True

        @m._except(BaseException)
        def base_error(e):
            pass

        @m._except(ValueError)
        def value_error(e):
            pass

        @m._try
        async def f():
            1/0

        await f()
        assert m.g.except_called

    def test_except_finally(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv(e):
            m.g.except_called = True

        @m._else
        def else_clause():
            m.g.else_called = True

        @m._finally
        def finally_clause():
            m.g.finally_called = True

        @m._try
        def f():
            1/0

        f()
        assert m.g.except_called
        assert not m.g.else_called
        assert m.g.finally_called

    @pytest.mark.asyncio
    async def test_async_except_finally(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv(e):
            m.g.except_called = True

        @m._else
        async def else_clause():
            m.g.else_called = True

        @m._finally
        async def finally_clause():
            m.g.finally_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert m.g.except_called
        assert not m.g.else_called
        assert m.g.finally_called

    def test_else_finally(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(Exception)
        def catch_all(e):
            pass

        @m._except(ArithmeticError)
        def arith_error(e):
            m.g.except_called = True

        @m._else
        def else_clause():
            m.g.else_called = True

        @m._finally
        def finally_clause():
            m.g.finally_called = True

        @m._try
        def f():
            pass

        f()
        assert not m.g.except_called
        assert m.g.else_called
        assert m.g.finally_called

    @pytest.mark.asyncio
    async def test_async_else_finally(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(Exception)
        def catch_all(e):
            pass

        @m._except(ArithmeticError)
        def arith_error(e):
            m.g.except_called = True

        @m._else
        def else_clause():
            m.g.else_called = True

        @m._finally
        def finally_clause():
            m.g.finally_called = True

        @m._try
        async def f():
            pass

        await f()
        assert not m.g.except_called
        assert m.g.else_called
        assert m.g.finally_called

    def test_return_prevents_else(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv(e):
            m.g.except_called = True

        @m._else
        def else_clause():
            m.g.else_called = True

        @m._finally
        def finally_clause():
            m.g.finally_called = True

        @m._try
        def f():
            return 'foo'

        f()
        assert not m.g.except_called
        assert not m.g.else_called
        assert m.g.finally_called

    @pytest.mark.asyncio
    async def test_async_return_prevents_else(self):
        m = Merry()
        m.g.except_called = False
        m.g.else_called = False
        m.g.finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv(e):
            m.g.except_called = True

        @m._else
        def else_clause():
            m.g.else_called = True

        @m._finally
        def finally_clause():
            m.g.finally_called = True

        @m._try
        async def f():
            return 'foo'

        await f()
        assert not m.g.except_called
        assert not m.g.else_called
        assert m.g.finally_called

    def test_unhandled(self):
        m = Merry()

        @m._try
        def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            f()

    @pytest.mark.asyncio
    async def test_async_unhandled(self):
        m = Merry()

        @m._try
        async def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            await f()

    def test_return_value_if_no_error(self):
        m = Merry()

        @m._try
        def f():
            return 'foo'

        @m._else
        def else_clause():
            return 'bar'

        assert f() == 'foo'

    @pytest.mark.asyncio
    async def test_async_return_value_if_no_error(self):
        m = Merry()

        @m._try
        async def f():
            return 'foo'

        @m._else
        async def else_clause():
            return 'bar'

        assert await f() == 'foo'

    def test_return_value_from_except(self):
        m = Merry()

        @m._except(ZeroDivisionError)
        def zerodiv():
            return 'foo'

        @m._try
        def f():
            1/0

        assert f() == 'foo'

    @pytest.mark.asyncio
    async def test_async_return_value_from_except(self):
        m = Merry()

        @m._except(ZeroDivisionError)
        async def zerodiv():
            return 'foo'

        @m._try
        async def f():
            1/0

        assert await f() == 'foo'

    def test_return_value_from_else(self):
        m = Merry()

        @m._else
        def else_clause():
            return 'foo'

        @m._try
        def f():
            pass

        assert f() == 'foo'

    @pytest.mark.asyncio
    async def test_async_return_value_from_else(self):
        m = Merry()

        @m._else
        async def else_clause():
            return 'foo'

        @m._try
        async def f():
            pass

        assert await f() == 'foo'

    def test_return_value_from_finally(self):
        m = Merry()

        @m._try
        def f():
            pass

        @m._finally
        def finally_clause():
            return 'bar'

        assert f() == 'bar'

    @pytest.mark.asyncio
    async def test_async_return_value_from_finally(self):
        m = Merry()

        @m._try
        async def f():
            pass

        @m._finally
        def finally_clause():
            return 'bar'

        assert await f() == 'bar'

    def test_return_value_from_finally2(self):
        m = Merry()

        @m._try
        def f():
            return 'foo'

        @m._finally
        def finally_clause():
            return 'bar'

        assert f() == 'bar'

    @pytest.mark.asyncio
    async def test_async_return_value_from_finally2(self):
        m = Merry()

        @m._try
        async def f():
            return 'foo'

        @m._finally
        async def finally_clause():
            return 'bar'

        assert await f() == 'bar'

    def test_return_value_from_finally3(self):
        m = Merry()

        @m._try
        def f():
            1/0

        @m._except(ZeroDivisionError)
        def zerodiv():
            return 'foo'

        @m._finally
        def finally_clause():
            return 'bar'

        assert f() == 'bar'

    @pytest.mark.asyncio
    async def test_async_return_value_from_finally3(self):
        m = Merry()

        @m._try
        async def f():
            1/0

        @m._except(ZeroDivisionError)
        async def zerodiv():
            return 'foo'

        @m._finally
        async def finally_clause():
            return 'bar'

        assert await f() == 'bar'

    def test_global_debug(self):
        m = Merry(debug=True)
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            f()
        assert not m.g.except_called

    @pytest.mark.asyncio
    async def test_async_global_debug(self):
        m = Merry(debug=True)
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            await f()
        assert not m.g.except_called

    def test_local_debug(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError, debug=True)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            f()
        assert not m.g.except_called

    @pytest.mark.asyncio
    async def test_async_local_debug(self):
        m = Merry()
        m.g.except_called = False

        @m._except(ZeroDivisionError, debug=True)
        async def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        with pytest.raises(ZeroDivisionError):
            await f()
        assert not m.g.except_called

    def test_local_debug_override(self):
        m = Merry(debug=True)
        m.g.except_called = False

        @m._except(ZeroDivisionError, debug=False)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        f()
        assert m.g.except_called

    @pytest.mark.asyncio
    async def test_async_local_debug_override(self):
        m = Merry(debug=True)
        m.g.except_called = False

        @m._except(ZeroDivisionError, debug=False)
        async def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert m.g.except_called

    def test_logger(self):
        m = Merry()
        m.g.except_called = False
        stream = StringIO()
        m.logger.addHandler(logging.StreamHandler(stream))

        @m._except(ZeroDivisionError)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        f()
        assert 'Traceback' in stream.getvalue()
        assert 'ZeroDivisionError: ' in stream.getvalue()

    @pytest.mark.asyncio
    async def test_async_logger(self):
        m = Merry()
        m.g.except_called = False
        stream = StringIO()
        m.logger.addHandler(logging.StreamHandler(stream))

        @m._except(ZeroDivisionError)
        async def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert 'Traceback' in stream.getvalue()
        assert 'ZeroDivisionError: ' in stream.getvalue()

    def test_custom_logger(self):
        my_logger = logging.getLogger('foo')
        stream = StringIO()
        my_logger.addHandler(logging.StreamHandler(stream))

        m = Merry(logger_name='foo')
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            m.g.except_called = True

        @m._try
        def f():
            1/0

        f()
        assert 'Traceback' in stream.getvalue()
        assert 'ZeroDivisionError: ' in stream.getvalue()

    @pytest.mark.asyncio
    async def test_async_custom_logger(self):
        my_logger = logging.getLogger('foo')
        stream = StringIO()
        my_logger.addHandler(logging.StreamHandler(stream))

        m = Merry(logger_name='foo')
        m.g.except_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv():
            m.g.except_called = True

        @m._try
        async def f():
            1/0

        await f()
        assert 'Traceback' in stream.getvalue()
        assert 'ZeroDivisionError: ' in stream.getvalue()
