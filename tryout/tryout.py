import inspect
from colors import colors

class tryout(object):
	exclude = [
		'__init__',
		'_finishTest',
		'_handleError',
		'run',
	]
	def __init__(self, bail=True):
		self.bail = bail
		self.methods = inspect.getmembers(self, predicate=inspect.ismethod)
		self.methods = [method[0] for method in self.methods if method[0] not in self.exclude]
		# colors('cyan','Tests:')
		# print '\n'.join(self.methods)

	def _handleError(self, err=None, caughtException=False):
		if not err:
			return

		colors('red', 'Error:\n', err)

		if not self.bail:
			# if the error is a caught exception
			# _finishTest won't have been called, so call it here
			if caughtException:
				return self._finishTest()
			return

		self.callback(err)
		self.numTests = 0
		self.callback = None

	def _finishTest(self, err=None):
		self._handleError(err)

		self.testNum += 1

	def run(self, callback=None):
		self.callback = callback
		self.testNum = 0
		self.numTests = len(self.methods)
		while self.testNum < self.numTests:
			colors('cyan', 'Running:', self.methods[self.testNum])
			try:
				getattr(self, self.methods[self.testNum])(self._finishTest)
			except Exception as err:
				self._handleError(err, caughtException=True)

		if self.callback:
			self.callback(None)

def main():
	class testStuff(tryout):
		def runA(self, done):
			print 'Test A'
			done()

		def runB(self, done):
			print 'Test B'
			done()

		def errorC(self, done):
			print 'Test C'
			done('omg error')

		def runD(self, done):
			print 'Test D'
			done()

	tests = testStuff()
	def testsComplete(err):
		print 'All done'
		print 'Error:', err

	print '\n\nThis will bail on error\n'
	tests.run(testsComplete)

	print '\n\nThis will run all tests\n'
	tests.bail = False
	tests.run(testsComplete)

if __name__ == '__main__':
	main()