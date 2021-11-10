# Hofstadter's Law: It always takes longer than you expect, even when you take into account Hofstadter's Law.
# Austin Z. Henley, 2021
# http://www.austinhenley.com/

import sys, re, requests

# Display error and abort.
def abort(msg):
    sys.exit("Error: " + msg)

# Manages a line of source code.
class Line:
    def __init__(self, text):
        self.index = 0
        self.tokens = []
        self.text = text
        self.tokenize()

    def tokenize(self):
        while self.index < len(self.text):
            if self.index > 0 and not self.text[self.index].isspace():  # Expect a space between tokens.
               abort("Unexpected token.")
            t = self.nextToken()
            if t is not None:
                self.tokens.append(t)

    # Gets next token. The 8 legal commands are: # ? ! @ + "regex" https://url.com/ /filepath.txt 
    def nextToken(self):
        length = len(self.text)
        # Skip all leading whitespace.
        while self.index < length and self.text[self.index].isspace():
            self.index += 1
        start = self.index

        if self.index == length:
            return None

        # Stdin/stdout.
        if self.text[self.index] == '#':
            self.index += 1
            return ('#', '#')

        # Equal to, not equal to, swap, or concatenate.
        elif self.text[self.index] in ['?', '!', '@', '+']:
            self.index += 1
            while self.index < length and self.text[self.index].isdigit():
                self.index += 1
            if self.index+1 == start:    # Must be one digit after the symbol.
                abort(f"Expected number after {self.text[start]}.")
            return (self.text[start], self.text[start+1:self.index])

        # Regex.
        elif self.text[self.index] == '"':
            escaped = False
            self.index += 1
            while self.text[self.index] != '"' or escaped:
                if escaped:
                    escaped = False
                elif self.text[self.index] == '\\':
                    escaped = True
                self.index += 1
                if self.index == length:
                    abort("Regex string is not closed.")
            self.index += 1
            return ("R", self.text[start+1:self.index-1])    # Omit quotes.

        # URL.
        elif self.text.startswith("http"):
            while self.index < len(self.text) and not self.text[self.index].isspace():
                self.index += 1
            return ("U", self.text[start:self.index])

        # File path.
        else:
            escaped = False
            while self.index < length and not self.text[self.index].isspace() or escaped:
                if escaped:
                    escaped = False
                elif self.text[self.index] == '\\':
                    escaped = True 
                self.index += 1
            return ("D", self.text[start:self.index])


# Evaluates the program a token at a time in the correct order.
class Evaluator:
    def __init__(self, lines):
        self.lines = lines
        self.values = {}
        self.nextLine = 0 # Next line to execute.
        self.indices = [0] * len(lines) # Next token of each line to execute.
        self.frozen = set()

    def getValue(self, key):
        if key in self.values:
            return self.values[key]
        return ""

    def setValue(self, key, val):
        if key != "0":
            self.values[key] = val

    def getCurrentValue(self):
        return self.getValue(str(self.nextLine+1))

    def setCurrentValue(self, val):
        self.setValue(str(self.nextLine+1), val)

    def start(self):
        while len(self.frozen) < len(self.lines):
            self.tick()

    def tick(self):
        # Get next token to execute. 
        line = self.lines[self.nextLine]
        #if len(line.tokens) == 0: return    # Empty line. #TODO: Empty line at end of file...
        #if self.nextLine in self.frozen: return # TODO: If this is last line...

        if len(line.tokens) > 0 and self.nextLine not in self.frozen:
            toktype, tokliteral = line.tokens[self.indices[self.nextLine]]

            ### Execute!

            # Either print current line's value or read input to it.
            if toktype == '#':
                # Stdout.
                if self.getCurrentValue() != "":
                    print(self.getCurrentValue())
                # Stdin.
                else:
                    self.setCurrentValue(input())

            # If equal, continue. Else, restart line.
            elif toktype == '?':
                if self.getCurrentValue() != self.getValue(tokliteral):
                    self.indices[self.nextLine] = -1

            # If not equal, continue. Else, restart line.
            elif toktype == '!':
                if self.getCurrentValue() == self.getValue(tokliteral):
                    self.indices[self.nextLine] = -1

            # Swap value with specified line's value.
            elif toktype == '@':
                tmp = self.getValue(tokliteral)
                self.setValue(tokliteral, self.getCurrentValue())
                self.setCurrentValue(tmp)

            # Concatenate current line's value with specified line's value and store.
            elif toktype == '+':
                other = self.getValue(tokliteral)
                self.setCurrentValue(self.getCurrentValue() + other)

            # Run regex on current line's value.
            elif toktype == 'R':
                try:
                    regex = re.compile(tokliteral)
                    result = regex.search(self.getCurrentValue())
                    if result:
                        self.setCurrentValue(result.group())
                    else:
                        self.setCurrentValue("")
                except Exception as err:
                    abort("Invalid regex. " + str(err))

            # Either HTTP POST the current line's value or save the response from HTTP GET.
            elif toktype == 'U':
                # HTTP POST.
                if self.getCurrentValue() != "":
                    try:
                        response = requests.post(tokliteral, data = self.getCurrentValue(), timeout = 0.5)
                        self.setCurrentValue(response.text) # TODO: Should this save the response or throw it away?
                    except:
                        self.setCurrentValue("") # TODO: Should this record "" or do nothing?
                # HTTP GET.
                else:
                    try:
                        response = requests.get(tokliteral, timeout = 0.5)
                        self.setCurrentValue(response.text)
                    except:
                        self.setCurrentValue("")

            # Either write the current line's value to file or read to it.
            elif toktype == 'D':
                # Write to file.
                if self.getCurrentValue() != "":
                    try:
                        with open(tokliteral, 'w') as f:
                            f.write(self.getCurrentValue())
                    except:
                        abort("Unable to write to file.")
                # Read from file
                else:
                    try:
                        with open(tokliteral, 'r') as f:
                            self.setCurrentValue(f.read())
                    except:
                        abort("Unable to read from file.")

            # Famous last words: should never happen.
            else:
                abort("Unknown token.")

        # Update nextLine's new index.
        self.indices[self.nextLine] += 1
        if self.indices[self.nextLine] >= len(self.lines[self.nextLine].tokens):
            #self.indices[self.nextLine] = 0
            self.frozen.add(self.nextLine)
        # Update nextLine.
        self.nextLine += 1
        if self.nextLine >= len(self.lines):
            self.nextLine = 0


def main(file=sys.argv[1]):
    try:
        with open(file, 'r') as f:
            lines = [Line(l) for l in f.readlines()]
    except:
        abort("Could not open source file.")

    evaluator = Evaluator(lines)
    evaluator.start()

# if this is the main program, run main()
if __name__ == '__main__':
    main()