# Tryout
###Simple unit testing for Python.

Basic example:
```
	import tryout

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
	tryout.run(testStuff, testsComplete, bail=False)

	print 'Tryout bails on error by default'
	tryout.run(testStuff)
```

## Running A Folder of Tests

Save this as ```c:/someModule/tests/__main__.py```:
```
	import os
	import sys
	sys.path.append('c:/PATH/TO/tryout')

	import tryout
	tryout.runFolder(os.path.realpath(__file__))
```

Then run:

```
	c:/someModule >>> python tests
```
