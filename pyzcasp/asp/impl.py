# Copyright (c) 2014, Santiago Videla
#
# This file is part of pyzcasp.
#
# caspo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caspo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caspo.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-

import os, tempfile
from zope import component
import pyparsing as pypa
import re

from interfaces import *
        
class Term(object):
    interface.implements(ITerm)
    
    def __init__(self, predicate, arguments=[]):
        if not isinstance(predicate, basestring):
            raise TypeError("Predicate name must be string. %s %s" % (predicate, predicate.__class__))
        
        if len(predicate) == 0:
            raise ValueError("Predicate name must be a non-empty string.")
            
        self.__pred = predicate
        
        forbidden = filter(lambda arg: isinstance(arg, float) or isinstance(arg, complex), arguments)
        if len(forbidden) > 0:
            raise TypeError("Number arguments must be integers. The following arguments are forbidden: %s" % forbidden)
            
        self.__args = map(lambda arg: (isinstance(arg, basestring) and '"'+arg+'"') or arg, arguments)
    
    @property
    def pred(self):
        return self.__pred
    
    @property
    def args(self):
        return self.__args
        
    def arg(self, n):
        return (isinstance(self.__args[n], basestring) and self.__args[n][1:-1]) or self.__args[n]
            
    def __repr__(self):
        if len(self.args) == 0:
            return "Term(%s)" % (repr(self.__pred),)
        else:
            return "Term(%s,[%s])" % (repr(self.__pred),",".join(map(repr, self.__args)))
    
    def __str__(self):
        if len(self.__args) == 0:
            return self.__pred
        else:
            return self.__pred + "(" + ",".join(map(str, self.__args)) + ")"
    
    def __hash__(self):
        return hash(tuple([self.__pred] + self.__args))
    
    def __eq__(self,other):
        return self.__pred == other.pred and self.__args == other.args
        
    def __ne__(self, other):
        return not self.__eq__(other)

class TermSet(set):
    interface.implements(ITermSet)
    
    def __init__(self, terms=[], score=None):
        super(TermSet, self).__init__(terms)
        self.score = score
        
    def to_file(self, filename=None):
        if filename:
            file = open(filename,'w')
        else:
            fd, filename = tempfile.mkstemp('.lp')
            file = os.fdopen(fd,'w')
            cleaner = component.getUtility(ICleaner)
            cleaner.collect_file(filename)
            
        for term in self:
            file.write(str(term) + '.\n')
            
        file.close()
        return filename

class AnswerSet(object):
    interface.implements(IAnswerSet)
    
    def __init__(self, atoms=[], score=None):
        super(AnswerSet, self).__init__()
        self.atoms = atoms
        self.score = score
        
def grammar():
    lp = pypa.Suppress(pypa.Literal("("))
    rp = pypa.Suppress(pypa.Literal(")"))
    
    # used for recursive definition in `function` Token below
    term = pypa.Forward()
    terms = pypa.delimitedList(term)
    integer = pypa.Combine(pypa.Optional(pypa.Literal('+') ^ pypa.Literal('-')) + pypa.Word(pypa.nums))
    # TODO: the string '_' should not be accepted
    function = pypa.Word(pypa.alphas + '_', pypa.alphanums + '_') + pypa.Group(pypa.Optional(lp + pypa.Optional(terms) + rp))
    
    # default actions:
    #  - convert integers
    #  - convert predicates/functions and constants (predicate or function without args)
    #  - remove quotes from strings
    integer.setParseAction(lambda s,l,t: int(t[0]))
    function.setParseAction(lambda s,l,t: Term(t[0],t[1]))
    pypa.quotedString.setParseAction(pypa.removeQuotes)
    
    # complete the recursive definition started with Forward
    term << (function ^ integer ^ pypa.quotedString)

    return term, function, integer


def cleanrun(fn):
    def decorator(*args, **kwargs):
        try:
            retval = fn(*args, **kwargs)
        finally:
            cleaner = component.getUtility(ICleaner)
            cleaner.clean_files()
            
        return retval

    return decorator
    
class ProcessError(Exception):
    interface.implements(IProcessError)
    
    def __init__(self, prg, code, stdout, stderr):
        self.prg = prg
        self.code = code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        return "Return code %d not allowed for %s. %s" % (self.code, self.prg, self.stderr)