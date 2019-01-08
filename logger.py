
class ProgressBar:

	def __init__(self, message, suffix=False):
		self.output = "\r" + message
		self.done = ", done." if suffix else ""
		print(self.output, end="", flush=True)

	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, tb):
		print(self.output + self.done, end="\n", flush=False)

def bar(message, suffix=False):
	return ProgressBar(message, suffix)