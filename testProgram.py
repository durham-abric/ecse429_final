import sys

def main(arg1, arg2, arg3, arg4):

    #Calculate values based on input argument
    #Mutants will change the relationship between a, b, c
    a = arg1 * arg2
    b = a - arg3
    c = (a + b) * (arg4 * b - a)

    printed = False
    orderings = []

    #Print order (greatest -> smallest) of values {a, b, c}... if a > b and b == c, output should be 'abc or acb'
    if a >= b and b >= c:
        orderings.append("abc")
    if a >= c and c >= b:
        orderings.append("acb")
    if b >= a and a >= c:
        orderings.append("bac")
    if b >= c and c >= a:
        orderings.append("bca")
    if c >= a and a >= b:
        orderings.append("cab")
    if c >= b and b >= a:
        orderings.append("cba")

    return " or ".join(orderings)

