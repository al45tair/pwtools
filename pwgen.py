import random
from wordset import words

class PasswordGenerator:

    separators = '-_!$&*+=23456789'
    
    def __init__(self):
        """Create a new PasswordGenerator object."""
        try:
            self.rnd = random.SystemRandom()
        except:
            self.rnd = random.Random()
        
    def generate(self, randomBits=47, maxLength=None):
        """Generate a random password containing at least randomBits of
        information, optionally with a maximum length."""
        
        # Restrict the number of random bits to a reasonable range
        bits = randomBits
        if bits < 26:
            bits = 26
        elif bits > 132:
            bits = 132

        # Work out how long our password will be
        count = 1 + (bits + (16 - 13)) / 17
        useSeparators = (bits + 12) / 13 != count
        length = count * 7 - 1

        # If it's too long, exit
        if maxLength and length > maxLength:
            return None

        output = []
        length = 0
        while bits > 0:
            wordNdx = self.rnd.randint(0, len(words)-1)
            
            word = words[wordNdx]
            if (self.rnd.randint(0, 1)):
                word = word.capitalize()

            output.append(word)

            length += len(word)
            bits -= 13

            if useSeparators and bits > 4:
                sepNdx = self.rnd.randint(0, len(self.separators)-1)
                output.append(self.separators[sepNdx])
                bits -= 4
            elif bits > 0:
                output.append(' ')

        return ''.join(output)

                
