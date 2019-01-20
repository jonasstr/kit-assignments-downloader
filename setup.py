from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file.
with open(path.join(here, 'README.md'), encoding='utf-8') as file:
	long_description = file.read()

setup(name='kita',
	version='1.0.0',
	description='An unofficial assignments downloader for the KIT Ilias website.',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/jonasstr/kita',
	author_email='uzxhf@student.kit.edu',

	classifiers = [
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.6'
	],
	packages=['kita', 'kita.misc'],	
	package_data={
		'': ['LICENSE', 'config.yml'],
	},
	include_package_data=True,
	install_requires=[
		'click'
		'ruamel.yaml>0.15',
		'selenium>=3'
	],
	entry_points='''
		[console_scripts]
		kita=kita.cli:main
	'''
)
