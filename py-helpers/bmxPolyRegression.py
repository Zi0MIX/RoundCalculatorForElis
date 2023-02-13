# Univariate linear regression - least squares
# PARAM1 - the degree, as a natural number = {1,2,..}
# PARAM2 - xs
# PARAM3 - ys
# @return The Coefficients of the fitted polynomial

# e.g.
# $ python3 polyRegression.py 1 "187.553 187.317 180.252 79.2687 167.998 23.7884" "135 135 141 230 152 279"
# > -0.8802032869356541 299.86729983516096
# > R^2: 0.9999943625520571

# since degree = 1, we're fitting to the family of equations of the form: y = mx + b,
#   -0.8802032869356541 is m, the slope
#   299.86729983516096 is b, the y value of the y-intercept
#   R^2 is the error. closer to 1.0, the more accurate the fit. The closer to 0, the more inaccurate the fit.

import sys
import numpy
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

def stringToListFloats(str):
    """
    Given a string of ints, e.g. "1 2 3"
    Return a list of ints, e.g. [1 2 3]
    """
    a_list = str.split()
    map_object = map(float, a_list)
    return list(map_object)

def parseInput():
    if (len(sys.argv) < 3):
        raise Exception("Must have 3 arguments")

    degree = -1
    # Insure degree is an integer
    try:
        an_integer = int(sys.argv[1])
        degree = an_integer
    except ValueError:
        print("Degree must be an integer")

    xs = stringToListFloats(sys.argv[2])
    ys = stringToListFloats(sys.argv[3])
    return degree, xs, ys

def main():
    degree, xs, ys = parseInput()
    
#    e.g. xs = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#    e.g. ys = [1.1, 3.9, 11.2, 21.5, 34.8, 51, 70.2, 92.3, 117.4, 145.5]
    coeffs = numpy.polyfit(xs, ys, deg=degree)
    
    # Print Result
    for c in range(len(coeffs)):
        print(coeffs[c], end=" ")
        
    # Calculate the Coefficient of Determination
    predicted = []
    for x in xs:
        sum = 0
        for c in range(len(coeffs)):
            sum += coeffs[c]*pow(x, len(coeffs) - c - 1)
        predicted.append(sum)
    
    r_squared = r2_score(ys, predicted)
    print("\n" + "R^2: " + str(r_squared))

if __name__ == "__main__":
    main()

