# Tryout
Simple unit testing for Python.

```
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
```
