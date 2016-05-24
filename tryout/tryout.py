import inspect
from colors import colors
import time
import traceback

class tryout(object):
	timeout = 5000
	_timeoutTime = 9999999999

	def __init__(self, bail=True):
		self.bail = bail
		self._methods = inspect.getmembers(self, predicate=inspect.ismethod)
		# exclude run and any method that starts with _
		self._methods = [method[0] for method in self._methods if method[0] != 'run' and method[0][0] != '_']
		colors('cyan','Running:')
		print ','.join(self._methods)

	def _handleError(self, err=None, execInfo=None, caughtException=False):
		if not err:
			return
		colors('red', '\n Error:\n', '=' * 30)

		if not self.bail:
			colors('red', str(err))
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

		if type(err) == Exception:
			raise err
		raise Exception(err)

	def _finishTest(self, err=None):
		self._handleError(err)

		self._testNum += 1

	def run(self, callback=None):
		self._callback = callback
		self._testNum = 0
		self._numTests = len(self._methods)

		while self._testNum < self._numTests and \
			time.time() < self._timeoutTime:

			self._timeoutTime = time.time() + self.timeout

			colors('cyan', '\n Running:', self._methods[self._testNum])
			colors('cyan', '=' * 30)
			try:
				getattr(self, self._methods[self._testNum])(self._finishTest)
			except Exception as err:
				self._handleError(err, traceback.format_exc(), caughtException=True)

		if self._callback:
			self._callback(None)




def main():
	class testStuff(tryout):
		def runA(self, done):
			print 'Test A'
			done()

		def errorC(self, done):
			print 'Test C'
			done('omg error')

		def runB(self, done):
			print 'Test B'
			done()

	def testsComplete(err):
		print 'Error:', err

	tests = testStuff()

	print 'Run all tests with a callback'
	tests.bail = False
	tests.run(testsComplete)

	print 'Bails on error by default'
	tests.run()


if __name__ == '__main__':
	main()