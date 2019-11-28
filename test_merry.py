from merry import Merry
import logging
import asyncio
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest
import aiounittest

import coverage

cov = coverage.coverage()
cov.start()


class TestMerry(aiounittest.AsyncTestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        cov.stop()
        cov.report(include='merry.py')

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_simple_except(self):
        m = Merry()
        except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertTrue(except_called)

    def test_simple_except2(self):
        m = Merry()
        except_called = False

        @m._except(ZeroDivisionError, _as="e")
        def zerodiv():
            nonlocal except_called
            self.assertIsInstance(m.e, ZeroDivisionError)
            except_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertTrue(except_called)

    def test_except_parent(self):
        m = Merry()
        except_parent_called = False
        except_child_called = False

        @m._except(Exception)
        def catch_all():
            nonlocal except_parent_called
            except_parent_called = True

        @m._except(ArithmeticError, _as="e")
        def arith_error():
            nonlocal except_child_called
            self.assertIsInstance(m.e, ZeroDivisionError)
            except_child_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertTrue(except_child_called)
        self.assertFalse(except_parent_called)

    def test_except_finally(self):
        m = Merry()
        except_called = False
        else_called = False
        finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._else
        def else_clause():
            nonlocal else_called
            else_called = True

        @m._finally
        def finally_clause():
            nonlocal finally_called
            finally_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertTrue(except_called)
        self.assertFalse(else_called)
        self.assertTrue(finally_called)

    def test_else_finally(self):
        m = Merry()
        except_parent_called = False
        except_child_called = False
        else_called = False
        finally_called = False

        @m._except(Exception)
        def catch_all():
            nonlocal except_parent_called
            except_parent_called = True

        @m._except(ArithmeticError)
        def arith_error():
            nonlocal except_child_called
            except_child_called = True

        @m._else
        def else_clause():
            nonlocal else_called
            else_called = True

        @m._finally
        def finally_clause():
            nonlocal finally_called
            finally_called = True

        @m._try
        def f():
            pass

        f()
        self.assertFalse(except_child_called)
        self.assertFalse(except_parent_called)
        self.assertTrue(else_called)
        self.assertTrue(finally_called)

    def test_return_prevents_else(self):
        m = Merry()
        except_called = False
        else_called = False
        finally_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._else
        def else_clause():
            nonlocal else_called
            else_called = True

        @m._finally
        def finally_clause():
            nonlocal finally_called
            finally_called = True

        @m._try
        def f():
            return 'foo'

        f()
        self.assertFalse(except_called)
        self.assertFalse(else_called)
        self.assertTrue(finally_called)

    def test_unhandled(self):
        m = Merry()

        @m._try
        def f():
            1/0

        self.assertRaises(ZeroDivisionError, f)

    def test_return_value_if_no_error(self):
        m = Merry()

        @m._try
        def f():
            return 'foo'

        @m._except
        def except_clause():
            return 'baz'

        @m._else
        def else_clause():
            return 'bar'

        self.assertEqual(f(), 'foo')

    def test_return_value_from_except(self):
        m = Merry()

        @m._except(ZeroDivisionError)
        def zerodiv():
            return 'foo'

        @m._try
        def f():
            1/0

        self.assertEqual(f(), 'foo')

    def test_return_value_from_else(self):
        m = Merry()

        @m._else
        def else_clause():
            return 'foo'

        @m._except
        def except_clause():
            pass

        @m._try
        def f():
            pass

        self.assertEqual(f(), 'foo')

    def test_return_value_from_finally(self):
        m = Merry()

        @m._try
        def f():
            pass

        @m._finally
        def finally_clause():
            return 'bar'

        self.assertEqual(f(), 'bar')

    def test_return_value_from_finally2(self):
        m = Merry()

        @m._try
        def f():
            return 'foo'

        @m._finally
        def finally_clause():
            return 'bar'

        self.assertEqual(f(), 'bar')

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

        self.assertEqual(f(), 'bar')

    def test_global_debug(self):
        m = Merry(debug=True)
        except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        self.assertRaises(ZeroDivisionError, f)
        self.assertFalse(except_called)

    def test_local_debug(self):
        m = Merry()
        except_called = False

        @m._except(ZeroDivisionError, debug=True)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        self.assertRaises(ZeroDivisionError, f)
        self.assertFalse(except_called)

    def test_local_debug_override(self):
        m = Merry(debug=True)
        except_called = False

        @m._except(ZeroDivisionError, debug=False)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertTrue(except_called)

    def test_logger(self):
        m = Merry()
        except_called = False
        stream = StringIO()
        m._Merry__logger.addHandler(logging.StreamHandler(stream))

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertIn('Traceback', stream.getvalue())
        self.assertIn('ZeroDivisionError: ', stream.getvalue())

    def test_custom_logger(self):
        my_logger = logging.getLogger('foo')
        stream = StringIO()
        my_logger.addHandler(logging.StreamHandler(stream))

        m = Merry(logger_name='foo')
        except_called = False

        @m._except(ZeroDivisionError)
        def zerodiv():
            nonlocal except_called
            except_called = True

        @m._try
        def f():
            1/0

        f()
        self.assertIn('Traceback', stream.getvalue())
        self.assertIn('ZeroDivisionError: ', stream.getvalue())

    def test_same_signature_except_finally(self):
        m = Merry()
        foo = object()
        bar = object()

        f_args = None
        f_kwargs = None

        except_args = None
        except_kwargs = None

        finally_args = None
        finally_kwargs = None

        @m._except(Exception)
        def catch_all(*args, **kwargs):
            nonlocal except_args, except_kwargs
            except_args = args
            except_kwargs = kwargs

        @m._finally
        def finally_clause(*args, **kwargs):
            nonlocal finally_args, finally_kwargs
            finally_args = args
            finally_kwargs = kwargs

        @m._try
        def f(*args, **kwargs):
            nonlocal f_args, f_kwargs
            f_args = args
            f_kwargs = kwargs
            1/0

        f(foo, value=bar)
        self.assertSequenceEqual(f_args, [foo])
        self.assertIs(f_args[0], foo)
        self.assertSequenceEqual(except_args, [foo])
        self.assertIs(except_args[0], foo)
        self.assertSequenceEqual(finally_args, [foo])
        self.assertIs(finally_args[0], foo)
        self.assertDictEqual(f_kwargs, {'value': bar})
        self.assertIs(f_kwargs['value'], bar)
        self.assertDictEqual(except_kwargs, {'value': bar})
        self.assertIs(except_kwargs['value'], bar)
        self.assertDictEqual(finally_kwargs, {'value': bar})
        self.assertIs(finally_kwargs['value'], bar)

    def test_same_signature_else_finally(self):
        m = Merry()
        bar = object()
        foo = object()

        f_args = None
        f_kwargs = None

        else_args = None
        else_kwargs = None

        finally_args = None
        finally_kwargs = None

        @m._else
        def else_clause(*args, **kwargs):
            nonlocal else_args, else_kwargs
            else_args = args
            else_kwargs = kwargs

        @m._finally
        def finally_clause(*args, **kwargs):
            nonlocal finally_args, finally_kwargs
            finally_args = args
            finally_kwargs = kwargs

        @m._try
        def f(*args, **kwargs):
            nonlocal f_args, f_kwargs
            f_args = args
            f_kwargs = kwargs

        f(foo, value=bar)
        self.assertSequenceEqual(f_args, [foo])
        self.assertIs(f_args[0], foo)
        self.assertSequenceEqual(else_args, [foo])
        self.assertIs(else_args[0], foo)
        self.assertSequenceEqual(finally_args, [foo])
        self.assertIs(finally_args[0], foo)
        self.assertDictEqual(f_kwargs, {'value': bar})
        self.assertIs(f_kwargs['value'], bar)
        self.assertDictEqual(else_kwargs, {'value': bar})
        self.assertIs(else_kwargs['value'], bar)
        self.assertDictEqual(finally_kwargs, {'value': bar})
        self.assertIs(finally_kwargs['value'], bar)

    def test_context_getattr(self):
        m = Merry()
        expected_obj = object()
        except_obj = None
        finally_obj = None
        outside_obj1 = None
        outside_obj2 = None
        except_called = False
        finally_called = False

        def access_outside1():
            nonlocal outside_obj1
            outside_obj1 = m.o

        def access_outside2():
            nonlocal outside_obj1
            outside_obj1 = m.o

        @m._except(Exception)
        def catch_all(o):
            nonlocal except_obj, except_called
            # test getter
            except_obj = m.o
            except_called = True

        @m._finally
        def finally_clause(o):
            nonlocal finally_obj, finally_called
            finally_obj = m.o
            finally_called = True

        @m._try
        def f(o):
            m.o = o
            1/0

        self.assertRaises(RuntimeError, access_outside1)
        self.assertIsNot(outside_obj1, expected_obj)

        f(expected_obj)

        self.assertTrue(except_called)
        self.assertTrue(finally_called)

        self.assertIs(except_obj, expected_obj)
        self.assertIs(finally_obj, expected_obj)

        self.assertRaises(RuntimeError, access_outside2)
        self.assertIsNot(outside_obj2, expected_obj)

    def test_context_delattr(self):
        m = Merry()
        expected_obj1 = object()
        expected_obj2 = object()
        except_has_attr1 = False
        except_has_attr2 = False
        except_called = False

        def access_outside():
            del m.o2

        @m._except(Exception)
        def catch_all(o1, o2):
            nonlocal except_called, except_has_attr1, except_has_attr2
            except_has_attr1 = hasattr(m, "o1")
            del m.o1
            except_has_attr2 = hasattr(m, "o1")
            except_called = True

        @m._try
        def f(o1, o2):
            m.o1 = o1
            m.o2 = o2
            1/0


        f(expected_obj1, expected_obj2)

        self.assertTrue(except_called)
        self.assertTrue(except_has_attr1)
        self.assertFalse(except_has_attr2)

        self.assertRaises(RuntimeError, access_outside)

    def test_context_setattr(self):
        pass
    
    async def test_except_async(self):
        m = Merry()
        except_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv():
            nonlocal except_called
            await asyncio.sleep(0)
            except_called = True

        @m._try
        async def f():
            1/0

        await f()
        self.assertTrue(except_called)

    async def test_except_finally_async(self):
        m = Merry()
        except_called = False
        finally_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv():
            nonlocal except_called
            await asyncio.sleep(0)
            except_called = True

        @m._finally
        async def finally_clause():
            nonlocal finally_called
            await asyncio.sleep(0)
            finally_called = True

        @m._try
        async def f():
            1/0

        await f()
        self.assertTrue(except_called)
        self.assertTrue(finally_called)
    
    async def test_else_async(self):
        m = Merry()
        except_called = False
        else_called = False

        @m._except(ZeroDivisionError)
        async def zerodiv():
            nonlocal except_called
            await asyncio.sleep(0)
            except_called = True

        @m._else
        async def else_clause():
            nonlocal else_called
            await asyncio.sleep(0)
            else_called = True

        @m._try
        async def f():
            pass

        await f()
        self.assertFalse(except_called)
        self.assertTrue(else_called)

    async def test_async_try_sync_handlers(self):
        m = Merry()
        except_called = False
        finally_called = False

        @m._except(ZeroDivisionError, _as="e")
        def zerodiv():
            nonlocal except_called
            self.assertIsInstance(m.e, ZeroDivisionError)
            except_called = True
        
        @m._finally
        def finally_clause():
            nonlocal finally_called
            finally_called = True

        @m._try
        async def f():
            await asyncio.sleep(0)
            1/0

        await f()
        self.assertTrue(except_called)
        self.assertTrue(finally_called)


if __name__ == '__main__':
    unittest.main()
