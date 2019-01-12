from logging.handlers import RotatingFileHandler
from selenium.common.exceptions import TimeoutException
import logging

class ProgressBar:

	def __init__(self, message, suffix=False):
		self.output = "\r" + message
		self.done = ", done." if suffix else ""
		print(self.output, end="", flush=True)

	def __enter__(self):
		pass

	def __exit__(self, exc_type, exc_value, tb):
		if isinstance(exc_value, TimeoutException):
			self.done = ", cancelled!"
		print(self.done, end="\n", flush=False)

def bar(message, suffix=False):
	return ProgressBar(message, suffix)

class Logger:

	def __init__(self):
		logger = logging.getLogger("Application log")
		logger.handlers=[]
		logger.setLevel(logging.ERROR)
		handler = RotatingFileHandler("app.log", maxBytes=10000)
		formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		self.logger = logger

	def log(self, exc_type, format_exc):
		self.logger.error(exc_type)
		self.logger.error(format_exc)