import inspect
from colors import colors
import time
import traceback

class tryout(object):
	timeout = 5000
	_timeoutTime = 9999999999
	_errors = 0
	_lineLength = 50

	title = 'Generic Tests'

	def __init__(self, bail=True):
		self.bail = bail
		self._methods = inspect.getmembers(self, predicate=inspect.ismethod)
		# exclude run and any method that starts with _
		self._methods = [method[0] for method in self._methods if method[0] != 'run' and method[0][0] != '_']

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

	def run(self, callback=None):
		colors('cyan', '\n\n Test Suite:', colors.end + self.title)
		colors('cyan', '=' * self._lineLength)

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
			colors('cyan', '=' * self._lineLength)
			try:
				getattr(self, self._methods[self._testNum])(self._finishTest)
			except Exception as err:
				if self.bail:
					colors('red', '\nError:\n')
					raise err
				self._handleError(err, traceback.format_exc(), caughtException=True)

			if self._errors > startingErrors:
				colors('red', '\nFailed')
			else:
				colors('green', 'Passed')

		colors('cyan','\n\n Results:')
		colors('cyan', '=' * self._lineLength)
		passed = self._numTests - self._errors
		passed = str(passed) + ' passed'
		failed = self._errors
		failed = str(failed) + ' failed'
		title = '    ' + self.title + ':' + colors.end
		if self._errors > 0:
			colors('red', title, passed + ',', failed)
		else:
			colors('green', title, passed)
		colors('cyan', '=' * self._lineLength)

		if self._callback:
			self._callback(None)




def main():
	class testStuff(tryout):
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
	tests = testStuff(bail=False)
	tests.run(testsComplete)

	print 'Bails on error by default'
	tests = testStuff()
	tests.run()


if __name__ == '__main__':
	main()
