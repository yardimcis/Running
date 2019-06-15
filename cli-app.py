"""
                 CONFIGURATION
                       |
                    ___|____
    ARGUMENTS --->  |     | ------> STDOUT
    STDIN-------->  |     | ------> STDERR
    SIGNAL------->  |_____| ------> EXITCODE

"""

"""
    CLA LIBRARIES :
        getopt
        optparse
        argparse
"""
""" ### STRUCUTRE ###

    mytool-project/
        setup.py
        mytool
        mytoollib/
            __init__.py
            __main__.py
            mytool.py
            utils.py
"""
""" ### SETUPTOOLS ###
    #setup.py
    setup(name='mytool',
        version = '2.0',
        url = 'https://mytool.cppninja.io/',
        license = 'BSD License',
        author = 'Ferhat Yardimci',
        author_email = 'ferhatt.yardimci@gmail.com',
        description = 'tools with a purpose',
        keywords = 'utils',
        packages = 'mytoollib',
        scripts = ['mytool'],
        platforms = 'Linux',
        )
"""

#argparse Python3
from sys import stdin, stdout, stderr
from colorama import Fore, Back, Style
from argparse import ArgumentParser
from progressbar import *
import time
import compago
import logging
import getpass


def main_1():
    ap = ArgumentParser()
    ap.add_argument('name', nargs='?')
    args = ap.parse_args()
    name = (args.name or 'World')
    print("Hello,",name,"!")

def main_2():
    ap = ArgumentParser()
    ap.add_argument('-v', '--verbose', default=False, action='store_true',help='Increase Verbosity')
    ap.add_argument('-n', '--number', type=int, default=1, help="The number of times to greet NAME")
    ap.add_argument('name', help="The person to greet")
    args = ap.parse_args()

    for index in range(args.number):
        print("Hello,",args.name,"!")
    if args.verbose:
        print("I've finished now.")

#compago Python2.7
#usage $ ./program greet --to=ferhat

app = compago.Application()

@app.command
def greet(to="world"):
    print "hello,", to, "!"
    
@app.command
def ungreet(to="world"):
    print "goodbye,", to, "!"

#Input and Output
#stdout is the output of your program, can be piped
#stderr is the information of your program whats going on, can be logged

#logging
logging.basicConfig(level=logging.WARNING, format="%(msg)s")

if options.verbose:
    logging.getLogger().setLevel(logging.DEBUG)

LOG = logging.getLogger('logtest')

LOG.debug('Running main')
LOG.info('Every thing okay')
LOG.warning('EVERYTHING HAS GONE WRONG !!!')

#isatty()
print "piped input :", not stdin.isatty()
print "piped output :", not stdout.isatty()
print "piped error :", not stderr.isatty()

#User Credential
username = getpass.getuser()
password = getpass.getpass()

print ("You are {username}, and you should never use the password '{password}'again!")



#colour
print Fore.RED + 'some red text'
print Back.GREEN + 'and with a green backgrond'
print Style.BRIGHT + 'and in bright text'
print Fore.RESET + Back.RESET + Style.RESET_ALL
print 'back to normal now'

#Progress bar simple
progress = ProgressBar()
for i in progress(range(80)):
    time.sleep(0.01)

#Progress Bar complex
widgets = ['Loading :', Percentage(), '', Bar(), '', ETA(), '', FileTransferSpeed()]
pbar = ProgressBar(widgets=widgets, maxval=20000).start()

for i in range(20000):
    pbar.update(i)
    time.sleep(.005)
pbar.finish()

#Configuration
#INI Files
def ini_parser():
    from ConfigParser import SafeConfigParser
    from os.path import dirname, join, expanduser

    INSTALL_DIR = dirname(__file__)

    config = SafeConfigParser()
    config.read([
                join(INSTALL_DIR, 'defaults.ini'),
                expanduser('~/.tool.ini'),
                'config.ini'
                ])
    return config

"""
   ###  Keyboard Interrrupt ###

   def main():
       try:
           time.sleep(5)
        except KeyboardInterrupt:
            pass
    
    if __name__ == '__main__':
        main()
"""
#Signals Package
def signal():
    import signal
    signal.siginterrupt(signal.SIGINFO, False)
    signal.signal(signal.SIGINFO, mysiginfofunc)




if __name__ == "__main__":
    app.run()

