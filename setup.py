from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as file:
	read_me = file.read()

setup(name='kita',
	version='0.1.0',
	description='An unofficial assignments downloader for the KIT Ilias website.',
	long_description=read_me,
	long_description_content_type='text/markdown',
	url='https://github.com/jonasstr/kita',
	license='MIT',
	author='Jonas Strittmatter',
	author_email='uzxhf@student.kit.edu',

	classifiers = [
		'Development Status :: 3 - ALPHA',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3.6',
		'Intended Audience :: End Users/Desktop',
		'Topic :: Utilities'
	],
	packages= find_packages(),	
	package_data={
		'': ['LICENSE', 'config.yml', 'geckodriver.exe'],
	},
	test_suite='tests',
	include_package_data=True,
	install_requires=[
		'click',
		'colorama',
		'ruamel.yaml>0.15',
		'selenium>=3'
	],
	entry_points={
		'console_scripts': [
			'kita=kita.cli:cli',
		],
	}
)
