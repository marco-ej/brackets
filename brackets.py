import timeit
import numpy as np
import urllib.request


def short_version(s):
    """
    This function is written in an attempt to be as concise as possible; the body is 101 characters long (excluding whitespace and this docstring). 
    Did anybody get it in under 100?
    
    It leverages the fact that in ASCII, '(' and ')' are 40 and 41; '[' and ']' are 91 and 93; and '{' and '}' are 123 and 125. The "distance" between matching
    symbols is always 1 or 2.

    We can reach the last return statement with inputs such as "(", so it's important to check that the b list is actually empty!
    """
    
    b = []
    for c in s:
        if c in "([{":
            b.append(c)
        if c in ")]}":
            if not b or ord(c) - ord(b[-1]) > 2:
                return False
            b.pop()
    return not b


def fast_version_1(s):
    """
        The first attempt at a faster version is identical to the short version above, with the difference that we now check for "low-hanging fruit"
        at the start of the function to quickly return without having to parse the whole string. This turns out to be much faster on long incorrect inputs,
        however by necessity it will actually be slower on long and correct inputs due to the added checks.
    """

    # Quick sanity checks
    if s.count("(") != s.count(")") or \
       s.count("[") != s.count("]") or \
       s.count("{") != s.count("}"):
        return False

    # Identical behaviour as before
    brackets = []
    for character in s:
        if character in "([{":
            brackets.append(character)
        elif character in ")]}":
            if not brackets or ord(character) - ord(brackets[-1]) > 2:
                return False
            brackets.pop()   

    # N.B. we can safely return True thanks the the sanity checks that rule out reaching this stage with an input like "("
    return True


def fast_version_2(s):
    """
        In the second version I tried to get fancy to hopefully squeeze out some improvements, but it looks like I failed as the simple version above
        outperforms this one. There's a lesson here somewhere...
        
        I'm sure that someone much smarter than me has figured out a way to avoid painfully iterating over each single character. I tried to think of
        smart ways to check larger chunks of the string at a time but I couldn't figure out a solution. I'm curious to see what other people came up with!
    """

    # Same sanity checks as before as I can't imagine cutting them
    if s.count("(") != s.count(")") or \
       s.count("[") != s.count("]") or \
       s.count("{") != s.count("}"):

        return False

    # I assumed that accessing a fixed-size array and incrementing/decrementing a counter + doing a hashmap lookup each loop would be quicker than dynamically growing and 
    # shrinking a list + casting two characters to integers. Apparently I was wrong
    # N.B. in the absolute worst case scenario of something like "((()))" the array will only ever need to be half as big as the input thanks to the sanity checks above.
    brackets = np.empty(len(s) // 2 + 1)
    b_index = 0
    b_dict = {"(": 0, 
              ")": 1,
              "[": 2,
              "]": 3,
              "{": 4,
              "}": 5
    }
    
    for character in s:
        if character in "([{":
            brackets[b_index] = b_dict[character]
            b_index += 1
        elif character in ")]}":
            # If the index is 0 - we're out
            # If the previous position in the array contains anything other than a matching open bracket - we're out
            if not b_index or brackets[b_index - 1] != b_dict[character] - 1:              
                return False
            b_index -= 1

    return True


def run_tests():
    """
        Run some very simple tests to check that all three versions work correctly. 
    """
    
    true_tests = [
        "()()",
        "[][]{}",
        "(([]))",
        "{{[(())]}}",
        "(((((())))))",
        "",
        "((()))[[]](({}()[[]]))",
        "(I love)(easyJet)",
        "(easyJet (is) great)",
        "hi everyone"
    ]
    
    false_tests = [
        "(",
        "{[}]",
        ")(",
        "([{})]",
        "]",
        "(I) love )RyanAir("
    ]
    
    for true_test in true_tests:
        assert(short_version(true_test))
        assert(fast_version_1(true_test))
        assert(fast_version_2(true_test))
    
    for false_test in false_tests:
        assert(not short_version(false_test))
        assert(not fast_version_1(false_test))
        assert(not fast_version_2(false_test))

    print("All tests completed")


if __name__ == "__main__":
    run_tests()

    # Obligatory KJB test
    king_james_bible = urllib.request.urlopen("https://www.gutenberg.org/cache/epub/73388/pg73388.txt").read().decode("utf-8")
    
    print(short_version(king_james_bible))
    print(fast_version_1(king_james_bible))
    print(fast_version_2(king_james_bible))

    # Construct the worst possible input - a string with 10 million open parentheses followed by 10 million closed parentheses. The function will have to
    # parse through each single character before concluding that the input is indeed valid.
    n = 10000000
    terrible_input = "(" * n + ")" * n
    
    def time_fast_1():
        fast_version_1(terrible_input)
    
    def time_fast_2():
        fast_version_2(terrible_input)

    # Time each function, taking the lowest measurement as it's the closest to its true performance
    # see https://stackoverflow.com/questions/8220801/how-to-use-timeit-module#comment12782516_8220943
    
    # |----------------------------------|
    # | WARNING: this will take a while. |
    # |----------------------------------|
    
    results = timeit.Timer(time_fast_1).repeat(10, 10)
    print(min(results) / 10)
    # On my machine: 1.383984149400203 seconds

    results = timeit.Timer(time_fast_2).repeat(10, 10)
    print(min(results) / 10)
    # On my machine: 2.8208240321997438 seconds, more than twice as long!!