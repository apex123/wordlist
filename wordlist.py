
############################################
#                                          #
# Wordlist generator, creates dictionaries #
# Developed by rexos.                      #
#                                          #
############################################

from itertools import product
from optparse import OptionParser
from collections import OrderedDict
import sys
import os

class Wordlist( object ):
    """
    Wordlist class is the wordlist itself, will do the job
    """
    def __init__( self, charset, minlen, maxlen, pattern, filedesc ):
        self.charset = list(set(charset))
        self.min = minlen
        self.max = maxlen
        self.pattern = pattern
        self.perms = {}
        self.filedesc = filedesc
        self.size = self.__total()

    def generate( self ):
        """
        Generates words of different length without storing
        them into memory, enforced by itertools.product
        """
        counter = 0
        for cur in range(self.min, self.max + 1):
            for word in product( self.charset, repeat=cur ):
                # write word to file or stdout
                print >> self.filedesc , ''.join(list(word))
                # if the list is saved to a file print out
                # a progress bar to stdout
                if self.filedesc != sys.stdout:
                    counter = counter + 1
                    self.__progress( counter )
        # once the work is done tell the kernel to point
        # the file pointer to the end of the file so as
        # to be able to get the file size.
        if self.filedesc != sys.stdout:
            self.filedesc.seek(0, os.SEEK_END)
            print( '\n' + __file__ + ' List size: ' +
                   str(self.filedesc.tell()) + ' bytes' )
        self.filedesc.close()

    def generate_with_pattern( self, data={}, composed='', prev=0 ):
        """
        Iterative-Recursive algorithm that creates the list
        based on a given pattern
        Each recursive call will concatenate a piece of string
        to the composed parameter
        data contains the dict created by scanning the pattern
        composed contains the current composed word (works recursively)
        prev is the index of the previous data object used.
        """
        if not prev:
            # the first call should scan the pattern first
            self.__create_perms()
            data = Pattern( self.pattern )
            data = data.scan()
        if data == {}:
            # if the known values in the pattern have been completely
            # used concat the last part, if any, and print it out
            if self.perms.get(len(self.pattern)-prev, None):
                for word in self.perms[len(self.pattern) - prev]:
                    print >> self.filedesc, composed+(''.join(list(word)))
            else:
                # the word is complete, print it out to file or stdout
                print >> self.filedesc, composed
        else:
            # pop a value from the pattern dict concat it to composed
            # concat a new part to the composed string and call this
            # function again with the new composed word
            num, val = data.popitem(last=False)
            for word in self.perms[num-prev]:
                self.generate_with_pattern( OrderedDict(data), composed +
                                            (''.join(list(word))) + val, num+1 )

    def __create_perms( self ):
        """
        Initializes the `perms` dict ensuring to do not
        repeat useless work.
        """
        prev = 0
        for ind, val in enumerate(list(self.pattern)):
            if val != '@': 
                if not self.perms.get((ind-prev), None):
                    self.perms[ind-prev] = list(product(self.charset,
                                                        repeat=(ind-prev)))
                prev = ind + 1

    def __total( self ):
        """
        Computes the number of words to be generated.
        It will be used to prompt a progress bar.
        """
        ary = range( self.min, self.max + 1 )
        length = len( self.charset )
        return sum( [ pow(length, x) for x in ary ] )

    def __progress( self, current ):
        """
        Prints out a progress bar reporting the work done
        so far.
        """
        val = int((current * 100) / float( self.size ))
        sys.stdout.write('\r')
        sys.stdout.write('Progress: %s%s %d%%' %
                         ('='*(val/5), ' '*(20-(val/5)), val))
        sys.stdout.flush()

class Pattern(object):
    """
    Pattern performs pattern scanning extracting
    values from it.
    """
    def __init__( self, raw ):
        if raw is None:
            raw = ''
        self.string = raw

    def scan( self ):
        res = OrderedDict()
        for ind, val in enumerate(self.string):
            if val != '@':
                res[ind] = val
        return res


def main():
    # command line option parsing
    parser = OptionParser()
    parser.add_option('-m', '--min', help='minimum word size')
    parser.add_option('-M', '--max', help='Maximum word size')
    parser.add_option('-o', '--out',
                      help='Saves output to specified file')
    parser.add_option('-p', help='Pattern to follow')

    opts, args = parser.parse_args()

    if not len(args):
        print('\n'+__file__+': charset required')
        exit(-1)


    minlen = opts.__dict__['min'] 
    if minlen is None:
        minlen = 1

    maxlen = opts.__dict__['max']
    if maxlen is None:
        maxlen = len(args[0])


    if opts.__dict__['out'] is None:
        filedesc = sys.stdout
    else:
        filedesc = open(opts.__dict__['out'], 'w')

    pattern = opts.__dict__['p']
    wordlist = Wordlist( args[0], int(minlen),
                         int(maxlen), pattern, filedesc )

    # if a pattern is given generate the list based on it
    if pattern:
        wordlist.generate_with_pattern()
    # generate normally otherwise
    else:
        wordlist.generate()
        wordlist.filedesc.close()

if __name__ == '__main__':
    main()
