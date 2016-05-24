class colors:
	red       = '\033[91m'
	green     = '\033[92m'
	yellow    = '\033[93m'
	blue      = '\033[94m'
	magenta   = '\033[95m'
	cyan      = '\033[96m'
	end       = '\033[0m'
	bold      = '\033[1m'
	underline = '\033[4m'

	def __init__(self, *args):
		text = ' '.join(args[1:])
		print getattr(self, args[0]), text, self.end


def main():
	print 'Color testing:'
	print colors.red + 'red' + colors.end
	print colors.green + 'green' + colors.end
	print colors.yellow + 'yellow' + colors.end
	print colors.blue + 'blue' + colors.end
	print colors.magenta + 'magenta' + colors.end
	print colors.cyan + 'cyan' + colors.end

	print '\nColored:'
	colors('red', 'red')
	colors('green', 'green')
	colors('yellow', 'yellow')
	colors('blue', 'blue')
	colors('magenta', 'magenta')
	colors('cyan', 'cyan', 'multi','argument')

if __name__ == '__main__':
	main()
