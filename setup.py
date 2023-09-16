from setuptools import setup

setup(
    name='Fkdm Downloader Manager',             # Replace with your app name
    version='1.0',                  # Replace with your app version
    description='Free yet simple and fast downloader manager',  # Replace with a short description
    author='Fidele K',             # Replace with your name
    author_email='your@email.com',  # Replace with your email
    url='https://github.com/itfidele/fkdm',  # Replace with your project's URL
    packages=['fkdm'],           # Replace 'yourapp' with your package name(s)
    install_requires=[
        # List your project's dependencies here
        'PyQt5',
        'qtawesome',
        'notify-py',
        'pycurl',

    ],
    entry_points={
        'console_scripts': [
            'fkdm = fkdm.main',  # Replace 'yourapp' with your actual entry point
        ],
    },
)
