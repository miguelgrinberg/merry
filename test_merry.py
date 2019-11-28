import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import unittest

import coverage

cov = coverage.coverage()
cov.start()

from merry import Merry


class TestMerry(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
