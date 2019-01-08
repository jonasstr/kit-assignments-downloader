
class ProgressBar:

	def __init__(self, message, suffix=False):
		self.output = "\r" + message
		self.done = ": Done." if suffix else ""
		print(self.output, end="", flush=True)

	def complete(self):
		print(self.output + self.done, end="\n", flush=False)