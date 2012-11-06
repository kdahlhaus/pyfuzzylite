'''
Created on 10/10/2012

@author: jcrada
'''


#TODO: Copy matlab membership functions
from math import isinf
class Term(object):
    '''
    Provides the necessary properties for any linguistic term
    '''
    
    def __init__(self, name, minimum, maximum):
        self.name = name
        self.minimum = minimum
        self.maximum = maximum
    
    def discretize(self, divisions=100, align='left'):
        if  isinf(self.minimum) or isinf(self.maximum):
            raise ValueError('cannot discretize a term whose minimum or maximum is infinity')
        dx = (self.maximum - self.minimum) / divisions
        x = None
        y = None
        shift = 0.0
        if align == 'left': pass
        elif align == 'center': shift = 0.5
        elif align == 'right': shift = 1.0
        for i in range(0, divisions ):
            x = self.minimum + (i + shift) * dx
            y = self.membership(x)
            yield (x, y)
    
    def toFCL(self):
        '''Returns a string in Fuzzy Control Language.'''
        return 'TERM %s := %s' % (self.name, self)
    
    def membership(self, x): raise NotImplementedError()



class Triangle(Term):
    '''
    Defines a triangular term using minimum as the left vertex,
    middle as the center vertex, and maximum as the right vertex
    '''
    
    def __init__(self, name, minimum, middle_vertex, maximum):
        Term.__init__(self, name, minimum, maximum)
        self.middle_vertex = middle_vertex
    
    def __str__(self):
        return '%s (%s, %s, %s)' % (self.__class__.__name__,
                                    self.minimum, self.middle_vertex, self.maximum)

    def membership(self, x):
        if x <= self.minimum or x >= self.maximum:
            return 0.0
        elif x == self.middle_vertex:
            return 1.0
        elif x < self.middle_vertex :
            return (x - self.minimum) / (self.middle_vertex - self.minimum)
        else:
            return (self.maximum - x) / (self.maximum - self.middle_vertex) 

class Trapezoid(Term):
    '''
    Defines a trapezoidal term using minimum and maximum as left-most and
    right-most vertices, and b and c as left and right vertices.
    '''
    
    def __init__(self, name, minimum, b, c, maximum):
        Term.__init__(self, name, minimum, maximum)
        self.b = b 
        self.c = c
        
    def __str__(self):
        return '%s (%s, %s, %s, %s)' % (self.__class__.__name__,
                                    self.minimum, self.b, self.c, self.maximum)
        

    def membership(self, x):
        if x <= self.minimum or x >= self.maximum: 
            return 0.0
        elif x <= self.b:
            return (x - self.minimum) / (self.b - self.minimum)
        elif x <= self.c:
            return 1.0
        elif x <= self.maximum:
            return (self.maximum - x) / (self.maximum - self.c)
        else: return 0.0
        
class Rectangle(Term):
    '''Defines a rectangular term in the range [minimum, maximum].'''
    def __init__(self, name, minimum, maximum):
        Term.__init__(self, name, minimum, maximum)
    
    def __str__(self):
        return '%s (%s, %s)' % (self.__class__.__name__,
                                    self.minimum, self.maximum)
    
    def membership(self, x):
        return 1.0 if self.minimum <= x <= self.maximum else 0.0

class Function(Term):
    '''Defines a linguistic term by a function given as a lambda expression.'''
    def __init__(self, name, lambda_expression, minimum, maximum):
        Term.__init__(self, name, minimum, maximum)
        self.lambda_expression = lambda_expression
    
    def __str__(self):
        return '%s %s (%s, %s)' % (self.__class__.__name__,
                                    self.lambda_expression,
                                    self.minimum, self.maximum)

    def membership(self, x):
        return self.lambda_expression(x, self.minimum, self.maximum)

from fuzzylite.operator import FuzzyOr
from collections import OrderedDict
class Cumulative(Term):
    '''Defines a linguistic term with other terms.'''
    def __init__(self, name, accumulate=FuzzyOr.Max):
        Term.__init__(self, name, float('-inf'), float('inf'))
        self.terms = OrderedDict()
        self.accumulate = accumulate
    
    def __str__(self):
        terms = ['[' + str(term) + ']' for term in self.terms]
        return '%s (%s, %s) {%s}' % (self.__class__.__name__,
                                    self.minimum, self.maximum,
                                    ' , '.join(terms)) 
    
    def aggregate(self, term, alphacut=1.0):
        import math
        if math.isinf(self.minimum) or term.minimum < self.minimum:
            self.minimum = term.minimum
        if math.isinf(self.maximum) or term.maximum > self.maximum:
            self.maximum = term.maximum
        self.terms[term] = alphacut
        
    def clear(self):
        self.minimum = float('-inf')
        self.maximum = float('inf')
        self.terms = OrderedDict()
    
    def toFCL(self):
        terms = ['[' + term.toFCL() + ']' for term in self.terms]
        return 'TERM := %s {%s}' % (self.__class__.__name__, 
                                    ' , '.join(terms)) 
    
    def membership(self, x):
        mu = 0.0
        for term in self.terms:
            mu = self.accumulate(mu, term.membership(x))
        return mu 

if __name__ == '__main__':
    
    a = Triangle('Low', 0, 5, 10)
    for pair in a.discretize(10):
        print(pair)
    print(a)
    print(a.toFCL())
    #Test: Composite
    composite = Cumulative('mix')
    composite.aggregate(Triangle('a', 0, 5, 10))
    composite.aggregate(Rectangle('a', 0, 5))
    print(composite)
    print(composite.toFCL())
    
    
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
