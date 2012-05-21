from setuptools import setup, find_packages

setup(
    name = "pwtools",
    version = "0.4",
    description = "Password generation and security checking",
    license = "MIT License",
    long_description = """\
pwtools provides a robust password generator and a password security checker
based on the design of libpasswdqc.  pwtools does not use code from libpasswdqc,
but is implemented in pure Python.
""",
    author = "Alastair Houghton",
    author_email = "alastair@alastairs-place.net",
    url = "http://alastairs-place.net/pwtools",
    classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Topic :: System',
    ],
    packages = find_packages()
)
