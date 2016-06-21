import os
import sys
import inspect
from colors import colors
import time
import traceback
import threading
import imp

class TestSuite(object):
	timeout = 5
	_timeoutCheckin = .1
	_errors = 0
	_lineLength = 50
	_lineColor = 'cyan'
	_isTestSuite = True
	_ignore = [
		'run',
		'setUp',
		'setUpClass',
		'tearDown',
		'tearDownClass',
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
			self.callbackCalled = True
			try:
				hasCallback = len(
					inspect.getargspec(self.tearDown).args) > 1
				if hasCallback:
					self.callbackCalled = False
					functionThread = threading.Thread(
						target=startThread,
						args=(self.tearDown, self._finishTest)
						)
					functionThread.start()
					waitOnTest()
				else:
					self.tearDown()
					self._finishTest()
			except Exception as err:
				if self.bail:
					colors('red', '\nError:\n')
					raise err
				self._handleError(err, traceback.format_exc(), caughtException=True)

		def startThread(func, callback):
			func(callback)

		# wait on the callback to be called
		# if it's not been called, error out
		def waitOnTest():
			startTime = time.time()
			calls = 0
			callsPerPrint = 1 / self._timeoutCheckin
			while time.time() < startTime + self.timeout and \
				not self.callbackCalled:
				if calls > 0 and calls % callsPerPrint == 0:
					print 'Waiting on callback'
				time.sleep(self._timeoutCheckin)
				calls += 1

			# if we're out of the loop and the callback still
			# hasn't been called we've timed out and should bail
			if not self.callbackCalled:
				raise Exception('Test timed out after ' +
					str(self.timeout) + ' seconds')

		# run the test w/ tearDown as the callback
		def runTest():
			# the callback is optional so we check if this test
			# needs one
			hasCallback = len(
				inspect.getargspec(testFunction).args) > 1

			erroredOnTest = True
			try:
				if hasCallback:
					self.callbackCalled = False
					functionThread = threading.Thread(
						target=startThread,
						args=(testFunction, tearDown)
						)
					functionThread.start()
					waitOnTest()
				else:
					testFunction()
					erroredOnTest = False
					tearDown()
			except Exception as err:
				if self.bail:
					colors('red', '\nError:\n')
					# try to run the tearDown even though we've
					# errored
					if erroredOnTest:
						tearDown()
					if hasattr(err, 'message') and \
						'\n' not in err.message:
						trace = traceback.format_exc()
						print trace
						sys.exit(trace)
					else:
						raise err
				# if we're not bailing, just handle the error
				self._handleError(err, traceback.format_exc(), caughtException=True)

		# run the setUp function w/ optional callback
		try:
			hasCallback = len(
					inspect.getargspec(self.setUp).args) > 1
			if hasCallback:
				self.callbackCalled = False
				functionThread = threading.Thread(
					target=startThread,
					args=(self.setUp, runTest)
					)
				functionThread.start()
				waitOnTest()
			else:
				self.setUp()
				runTest()
		except Exception as err:
			if self.bail:
				colors('red', '\nError:\n')
				raise err
			self._handleError(err, traceback.format_exc(), caughtException=True)

	def setUpClass(self):
		'''
		Run before the entire suite runs
		'''
		pass

	def setUp(self):
		'''
		Run before each test
		'''
		pass

	def tearDownClass(self):
		'''
		Run after the entire suite runs
		'''
		pass

	def tearDown(self):
		'''
		Run after each test
		'''
		pass

	# Returns a tuple of number of tests passed
	#					 number of tests failed
	#					 if failure, error message
	#					 if failure, failed method
	def run(self, callback=None):
		colors('magenta', '\n\n Suite:', colors.end + self.title)
		colors('magenta', '=' * self._lineLength)

		self._callback = callback
		self._testNum = 0
		self._errors = 0
		self._numTests = len(self._methods)

		self._runningTests = True

		while self._testNum < self._numTests:
			startingErrors = self._errors

			# update the start time so self._timeoutThread
			# doesn't error out
			self._startTime = time.time()
			methodName = self._methods[self._testNum] \
				.replace('_', ' ')

			colors('cyan', '\n Test:', colors.end + methodName)
			colors(self._lineColor, '=' * self._lineLength)

			# Try _runTest() and catch any exceptions
			# BaseExceptions are caught to include sys.exit()
			# Exceptions are processed for summary output and re-raised
			try:
				self._runTest()
			except BaseException as err:
				# self._errors only incremented if bail=False, in _handleError,
				# incremement here if bail=True
				self._errors += 1
				passed = self._testNum - self._errors
				failed = self._errors
				return (passed, failed, err.message, methodName)

			if self._errors > startingErrors:
				colors('red', '\n Failed')
			else:
				colors('green', ' Passed')

		self._runningTests = False
		colors('cyan','\n\n Results:')
		colors(self._lineColor, '=' * self._lineLength)
		passed = self._numTests - self._errors
		msgPassed = str(passed) + ' passed'
		failed = self._errors
		msgFailed = str(failed) + ' failed'
		title = '    ' + self.title + ':' + colors.end
		if self._errors > 0:
			colors('red', title, msgPassed + ',', msgFailed)
		else:
			colors('green', title, msgPassed)
		colors(self._lineColor, '=' * self._lineLength)

		if self._callback:
			self._callback(None)

		return (passed, failed, None, None)

def run(test, callback=None, *args, **kwargs):
	suite = test(*args, **kwargs)

	error = None
	try:
		suite.setUpClass()
	except Exception as err:
		error = err

	if not error:
		try:
			passed, failed, errMessage, failedMethod = suite.run(callback)
		except Exception as err:
			error = err

	if not error:
		try:
			suite.tearDownClass()
		except Exception as err:
			error = err

	if error:
		raise error
	else:
		return (passed, failed, errMessage, failedMethod)

def runFolder(path):
	root = os.path.dirname(path)
	print 'running Folder'
	files = os.listdir(root)
	# testResults, a list of tuples, storing the testfile name, numPassed, numFailed, for all testfiles in a folder
	results = []
	for f in files:
		if f[0] == '.' or \
			f[-2:] != 'py' or \
			f[0] == '_':
			continue
		moduleName = f.split('.')[0]
		modulePath = os.path.join(root, f)
		mod = imp.load_source(moduleName, modulePath)
		# get all the test suites for a given file
		suites = [getattr(mod, c) for c in dir(mod) if hasattr(getattr(mod, c), '_isTestSuite')]

		totalPassed = 0
		totalFailed = 0
		for suite in suites:
			passed, failed, error, failedMethod = run(suite)
			totalPassed += passed
			totalFailed += failed
		results.append((f, totalPassed, totalFailed, error, failedMethod))

	# Folder summary
	folder = os.path.split(root)[1]
	colors('blue', '\n\n Folder Summary:', colors.end + root)
	colors('blue', '=' * TestSuite._lineLength + '\n')
	success = True
	for result in results:
		testPath = os.path.join(folder, result[0])
		testPassed = result[1]
		testFailed = result[2]
		testError = result[3]
		testMethod = result[4]
		if testFailed > 0:
			colors('red', testPath + colors.end + ': ' + str(testPassed) + ' passed, ' + str(testFailed) + ' failed\n')
			success = False
			print 'Failing on test '+ testMethod + ' with:'
			colors('red', '\nError:\n')
			print testError
		else:
			colors('green', testPath + colors.end + ': ' + str(testPassed) + ' passed\n')
	if success:
		print('All tests passed.\n')

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
