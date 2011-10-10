import re
import string

class PasswordChecker:

    # Failure reasons
    ReasonSame = "the same as the old one"
    ReasonSimilar = "based on the old one"
    ReasonShort = "too short"
    ReasonLong = "too long"
    ReasonSimpleShort = "too simple for this length (not enough different kinds of character, and too short)"
    ReasonSimple = "too simple (not enough different kinds of character)"
    ReasonPersonal = "based on personal information"
    ReasonWord = "based on a dictionary word"
    ReasonSeq = "based on a common sequence of characters"

    def __init__(self, dictionary='/usr/share/dict/words'):
        """Create a new PasswordChecker object; takes an optional dictionary
        filename argument, which defaults to '/usr/share/dict/words'."""
        self.deLeet = string.maketrans('@483!|10$5+7',
                                       'aabeillosstt')
        self.charSetLengths = [ 10, 36, 62, 95 ]
        self.minLengths = [ None, 12, 8, 7 ]
        self.minWords = 3
        self.minPassphraseLen = 11
        self.matchLength = 4
        self.maxLength = None
        self.minLength = None
        self.trailingDigitsRegexp = re.compile('[0-9]+$')
        self.commonSequences = [
            '0123456789',
            '`1234567890-=',
            '~!@#$%^&*()_+',
            'abcdefghijklmnopqrstuvwxyz',
            'quertyuiop[]\\asdfghjkl;\'zxcvbnm,./',
            'quertyuiop{}|asdfghjkl;"zxcvbnm<>?',
            'quertyuiopasdfghjklzxcvbnm',
            '1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik,9ol.0p;/-[\'=]\\',
            'qazwsxedcrfvtgbyhnujmikolp'
            ]
        self.words = []

        f = open(dictionary)
        try:
            for line in f:
                self.words.append(line.strip(' \t\r\n'))
        except:
            f.close()
        
    def expectedDifferentChars(self, characterSetLen, length):
        """Return the expected number of different characters for a string
        of the specified length drawn randomly from a character set of given
        size."""
        return characterSetLen * (1 - pow (float(characterSetLen - 1)
                                           / characterSetLen, length - 1)) - 1

    def isSimplePassword(self, password, bias=0):
        """Return True if the password provided appears to be too simple,
        False otherwise.  Takes into account the numbers of digits, upper
        and lower case letters, non-ASCII characters and other characters.
        Also considers the number of 'words'.  Discounts are applied for
        leading uppercase characters and also for trailing digits."""
        length = len(password)
        if length == 0:
            return True

        # Count the various classes of characters
        digits = 0
        lowerCase = 0
        upperCase = 0
        others = 0
        unknowns = 0
        words = 0
        pwCharSet = set()
        p = None
        for c in password:
            if ord(c) >= 128:
                unknowns += 1
            elif c.isdigit():
                digits += 1
            elif c.islower():
                lowerCase += 1
            elif c.isupper():
                upperCase += 1
            else:
                others += 1

            if p is not None:
                if (c.isalpha() and not p.isalpha()) \
                   or p.isspace():
                    words += 1
            p = c
            pwCharSet.add(c)

        # Discount the effect of leading capital letters and trailing digits
        if password[0].isupper():
            upperCase -= 1

        m = self.trailingDigitsRegexp.search(password)
        if m:
            digits -= 1

        # Work out how many different kinds of characters we've seen
        classes = 0
        if digits:
            classes += 1
        if lowerCase:
            classes += 1
        if upperCase:
            classes += 1
        if others:
            classes += 1
        if unknowns and classes <= 1 and (classes == 0
                                          or digits != 0
                                          or words >= 2):
            classes += 1

        # Count the different characters
        diffChs = len(pwCharSet)

        if classes > 4:
            classes = 4

        # Consider each class
        while classes > 0:
            classes -= 1
            minLen = self.minLengths[classes]
            csLen = self.charSetLengths[classes]
            if minLen is not None \
               and length + bias >= minLen \
               and diffChs >= self.expectedDifferentChars(csLen, minLen):
                return False

        if bias > 0:
            blen = length + bias
        else:
            blen = length

        if self.minWords is not None \
           and words >= self.minWords \
           and blen > self.minPassphraseLen \
           and diffChs >= self.expectedDifferentChars(27, self.minPassphraseLen):
            return False

        return True

    def mapLeet(self, password):
        """Translate from 'leet'-speak to normal text."""
        return password.lower().translate(self.deLeet)

    def isBasedOn(self, needle, haystack, original, reversed=False,
                  discount=False):
        """Checks whether haystack is based on needle."""
        if self.matchLength is None:
            return False
        length = len(needle)
        worstBias = 0
        for offset in xrange(0, length - 1):
            for sublen in xrange(self.matchLength, length - offset):
                substr = needle[offset:offset+sublen]
                hofs = 0
                found = False
                while hofs < len(haystack):
                    pos = haystack.find(substr, hofs)
                    if pos == -1:
                        break
                    found = True
                    
                    if not discount:
                        if not reversed:
                            tmp = original[:pos] + original[pos+sublen:]
                        else:
                            rpos = length - pos
                            tmp = original[:rpos] + original[rpos+sublen:]
                        if self.isSimplePassword(tmp, self.matchLength - 1):
                            return True
                    else:
                        bias = self.matchLength - sublen - 1
                        if bias < worstBias:
                            if self.isSimplePassword(original, bias):
                                return True
                            worstBias = bias
                            
                    hofs = pos + 1

                # If no match of length sublen, then no match of length >sublen
                if not found:
                    break
                    
        return False

    def isBasedOnWord(self, needle, original, reversed=False):
        """Checks whether needle is based on a dictionary word, a common
        sequence or on a recent four-digit year."""
        if self.matchLength is None:
            return False

        for sequence in self.commonSequences:
            if self.isBasedOn(sequence, needle, original, reversed, True):
                return PasswordChecker.ReasonSeq

        for year in xrange(1900, 2040):
            if self.isBasedOn(str(year), needle, original, reversed, True):
                return PasswordChecker.ReasonSeq

        # For word matches, we don't try to use isBasedOn, because it's too
        # slow...
        bias = 0
        length = len(needle)
        for word in self.words:
            wordLength = len(word)
            if wordLength < self.matchLength \
                   or length > wordLength * 2 \
                   or wordLength > length \
                   or bias <= -wordLength:
                continue

            if needle.find(word) != -1:
                bias = -wordLength

        if bias != 0:
            if self.isSimplePassword(original, bias):
                return PasswordChecker.ReasonWord

        return False
    
    def checkPassword(self, password, old_password=None, username=None,
                      personal=None):
        """Checks password to see whether or not it is good.  Optionally
        compares the new password with the old password, a username and/or
        an array of other values to ensure that the password is not easily
        derived from the user's identity.

        Returns a reason string (see the ReasonXXX constants), or False if
        the password is OK."""
        if old_password is not None \
           and password == old_password:
            return PasswordChecker.ReasonSame
        
        if self.minLength is not None \
           and len(password) < self.minLength:
            return PasswordChecker.ReasonShort

        if self.maxLength is not None \
           and len(password) > self.maxLength:
            return PasswordChecker.ReasonLong
        
        if self.isSimplePassword (password):
            if self.minLengths[1] is not None \
               and len(password) < self.minLengths[1] \
               and self.minLengths[1] <= self.maxLength:
                return PasswordChecker.ReasonSimpleShort
            return PasswordChecker.ReasonSimple

        notLeet = self.mapLeet(password)
        notLeetReverse = notLeet[::-1]

        if old_password is not None:
            notLeetOld = self.mapLeet(old_password)
            if self.isBasedOn(notLeetOld, notLeet, password) \
               or self.isBasedOn(notLeetOld, notLeetReverse, password, True):
                return PasswordChecker.ReasonSimilar
            
        if username is not None:
            notLeetUser = self.mapLeet(username)
            if self.isBasedOn(notLeetUser, notLeet, password) \
               or self.isBasedOn(notLeetUser, notLeetReverse, password, True):
                return PasswordChecker.ReasonPersonal

        if personal is not None:
            for extra in personal:
                notLeetExtra = self.mapLeet(extra)
                if self.isBasedOn(notLeetExtra, notLeet, password) \
                       or self.isBasedOn(notLeetExtra, notLeetReverse,
                                         password, True):
                    return PasswordChecker.ReasonPersonal

        reason = self.isBasedOnWord(notLeet, password)
        if not reason:
            reason = self.isBasedOnWord(notLeetReverse, password)
        return reason
