from setuptools import setup


def readme():
	with open('README.rst') as f:
		return f.read()


setup(name='jk_fileaccess',
	version='0.2017.1.15',
	description='Provides a uniform interface to process files that are either stored locally or remotely.',
	author='Jürgen Knauth',
	author_email='pubsrc@binary-overflow.de',
	license='Apache 2.0',
	url='https://github.com/jkpubsrc/python-module-jk-fileaccess',
	download_url='https://github.com/jkpubsrc/python-module-jk-fileaccess/tarball/0.2017.1.15',
	keywords=['file', 'filesystem', 'ssh', 'sftp', 'iterating'],
	packages=['jk_fileaccess'],
	install_requires=[
		"jk_temporary",
		"sh",
		"pysftp"
	],
	include_package_data=True,
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 3.5',
		'License :: OSI Approved :: Apache Software License'
	],
	long_description=readme(),
	zip_safe=False)

