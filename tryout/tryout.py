import os
import sys
import inspect
from colors import colors
import time
import traceback
import imp

class TestSuite(object):
	timeout = 5000
	_timeoutTime = 9999999999
	_errors = 0
	_lineLength = 50
	_lineColor = 'cyan'
	_isTestSuite = True
	_ignore = [
		'run',
		'setUp',
		'tearDown',
		'assertEqual',
		'assertTrue',
		'assertIn'
	]

	title = 'Generic Tests'

	def __init__(self, bail=True):
		self.bail = bail
		self._methods = inspect.getmembers(self, predicate=inspect.ismethod)
		# exclude run and any method that starts with _
		self._methods = [method[0] for method in self._methods if method[0] not in self._ignore and method[0][0] != '_']

	def assertEqual(self, a, b):
		if not a == b:
			raise Exception(str(a) + ' != ' + str(b))

	def assertTrue(self, a):
		if not a:
			raise Exception(str(a) + ' != True')

	def assertIn(self, a, b):
		if not a in b:
			raise Exception(str(a) + ' not in ' + str(b))

	def _handleError(self, err=None, execInfo=None, caughtException=False):
		if not err:
			return

		self._errors += 1

		if not self.bail:
			colors('red', '\nError:\n')
			# if err is an actual error and not a string
			# and we have execInfo, print that instead
			if type(err) == Exception and execInfo:
				err = execInfo
			print str(err)

			# if the error is a caught exception
			# _finishTest won't have been called, so call it here
			if caughtException:
				return self._finishTest()
			return

		self._numTests = 0
		# if we have a callback, let that handle the errors
		if self._callback:
			self._callback(err, execInfo)
			self._callback = None
			return

		print ''
		if type(err) == str:
			raise Exception(err)
		raise err

	def _finishTest(self, err=None):
		self._handleError(err)

		self._testNum += 1

	def _runTest(self):
		testFunction = getattr(self, self._methods[self._testNum])

		# run the tearDown function w/ optional callback
		# when tearDown is done, call _finishTest
		def tearDown():
			try:
				hasCallback = len(
					inspect.getargspec(self.tearDown).args) > 1
				if hasCallback:
					self.tearDown(self._finishTest)
				else:
					self.tearDown()
					self._finishTest()
			except Exception as err:
				if self.bail:
					colors('red', '\nError:\n')
					raise err
				self._handleError(err, traceback.format_exc(), caughtException=True)

		# run the test w/ tearDown as the callback
		def runTest():
			# the callback is optional, so we try to pass it
			# first, then catch the argument error and try it
			# without the callback
			hasCallback = len(
				inspect.getargspec(testFunction).args) > 1
			erroredOnFunction = True
			try:
				if hasCallback:
					testFunction(tearDown)
				else:
					testFunction()
					erroredOnFunction = False
					tearDown()
			except Exception as err:
				if self.bail:
					colors('red', '\nError:\n')
					# try to run the tearDown even though we've
					# errored
					if erroredOnFunction:
						tearDown()
					if hasattr(err, 'message') and \
						'\n' not in err.message:
						print traceback.format_exc()
						sys.exit()
					else:
						raise err
				# if we're not bailing, just handle the error
				self._handleError(err, traceback.format_exc(), caughtException=True)

		# run the setUp function w/ optional callback
		try:
			hasCallback = len(
					inspect.getargspec(self.setUp).args) > 1
			if hasCallback:
				self.setUp(runTest)
			else:
				self.setUp()
				runTest()
		except Exception as err:
			if self.bail:
				colors('red', '\nError:\n')
				raise err
			self._handleError(err, traceback.format_exc(), caughtException=True)

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def run(self, callback=None):
		colors('magenta', '\n\n Suite:', colors.end + self.title)
		colors('magenta', '=' * self._lineLength)

		self._callback = callback
		self._testNum = 0
		self._errors = 0
		self._numTests = len(self._methods)

		while self._testNum < self._numTests and \
			time.time() < self._timeoutTime:
			startingErrors = self._errors
			self._timeoutTime = time.time() + self.timeout

			methodName = self._methods[self._testNum] \
				.replace('_', ' ')

			colors('cyan', '\n Test:', colors.end + methodName)
			colors(self._lineColor, '=' * self._lineLength)

			self._runTest()

			if self._errors > startingErrors:
				colors('red', '\n Failed')
			else:
				colors('green', ' Passed')

		colors('cyan','\n\n Results:')
		colors(self._lineColor, '=' * self._lineLength)
		passed = self._numTests - self._errors
		passed = str(passed) + ' passed'
		failed = self._errors
		failed = str(failed) + ' failed'
		title = '    ' + self.title + ':' + colors.end
		if self._errors > 0:
			colors('red', title, passed + ',', failed)
		else:
			colors('green', title, passed)
		colors(self._lineColor, '=' * self._lineLength)

		if self._callback:
			self._callback(None)

def run(test, callback=None, *args, **kwargs):
	suite = test(*args, **kwargs)
	suite.run(callback)

def runFolder(path):
	root = os.path.dirname(path)

	files = os.listdir(root)
	for f in files:
		if f == '__main__.py' or f[0] == '.' or f[-2:] != 'py':
			continue
		moduleName = f.split('.')[0]
		modulePath = os.path.join(root, f)
		mod = imp.load_source(moduleName, modulePath)
		# get all the test suites for a given file
		suites = [getattr(mod, c) for c in dir(mod) if hasattr(getattr(mod, c), '_isTestSuite')]
		for suite in suites:
			run(suite)


def main():
	class testStuff(TestSuite):
		title = 'tests/testStuff.py'

		def runA(self, done):
			print 'Test A'
			done()

		def errorC(self, done):
			print 'Test C'
			raise Exception('omg error')

		def runB(self, done):
			print 'Test B'
			done()

	def testsComplete(err):
		print 'Error:', err


	print 'Run all tests with a callback'
	run(testStuff, testsComplete, bail=False)

	print 'Tryout bails on error by default'
	run(testStuff)


if __name__ == '__main__':
	main()
