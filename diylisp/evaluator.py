# -*- coding: utf-8 -*-

import operator
from functools import wraps

from .ast import (
    is_atom, is_boolean, is_closure, is_integer, is_list, is_string, is_symbol
)
from .parser import unparse
from .types import Closure, Environment, LispError, String


"""
This is the Evaluator module. The `evaluate` function below is the heart
of your language, and the focus for most of parts 2 through 6.

A score of useful functions is provided for you, as per the above imports,
making your work a bit easier. (We're supposed to get through this thing
in a day, after all.)
"""


def evaluate(ast, env):
    """Evaluate an Abstract Syntax Tree in the specified environment."""

    if is_symbol(ast):
        return env.lookup(ast)
    elif is_boolean(ast):
        return ast
    elif is_integer(ast):
        return ast
    elif is_list(ast):
        form = ast[0]
        if is_special_form(form):
            return eval_special_form(ast, env)
        elif is_math(form):
            return eval_math(ast, env)

    return ast


def expected_length(ex_length):
    def deco(fn):
        @wraps(fn)
        def internal(ast, env):
            cur_len = len(ast)
            if cur_len != ex_length:
                raise LispError(
                    'Wrong number of arguments: {}, expected length: {}, '
                    'but got: {}'.format(ast, ex_length, cur_len)
                )
            return fn(ast, env)
        return internal
    return deco


@expected_length(2)
def eval_quote(ast, env):
    return ast[1]


@expected_length(2)
def eval_atom(ast, env):
    return is_atom(evaluate(ast[1], env))


@expected_length(3)
def eval_eq(ast, env):
    op1 = evaluate(ast[1], env)
    op2 = evaluate(ast[2], env)
    if is_atom(op1) and is_atom(op2):
        return op1 == op2
    else:
        return False


MATH_FUNC = {
    '+': operator.add,
    '-': operator.sub,
    '/': operator.div,
    '*': operator.mul,
    'mod': operator.mod,
    '>': operator.gt
}


def is_math(form):
    return form in MATH_FUNC.iterkeys()


@expected_length(3)
def eval_math(ast, env):
    op1 = evaluate(ast[1], env)
    op2 = evaluate(ast[2], env)
    if not (is_integer(op1) and is_integer(op2)):
        raise LispError(
            'Math operation {} require integer operands'.format(ast)
        )
    return MATH_FUNC[ast[0]](op1, op2)


@expected_length(4)
def eval_if(ast, env):
    cond = evaluate(ast[1], env)
    if cond:
        return evaluate(ast[2], env)
    else:
        return evaluate(ast[3], env)


@expected_length(3)
def eval_define(ast, env):
    var = ast[1]
    if not is_symbol(var):
        raise LispError('non-symbol assigment')
    val = evaluate(ast[2], env)
    env.set(var, val)
    return '{} = {}'.format(var, val)


SPECIAL_FORMS = {
    'quote': eval_quote,
    'atom': eval_atom,
    'eq': eval_eq,
    'if': eval_if,
    'define': eval_define
}


def is_special_form(form):
    return form in SPECIAL_FORMS.iterkeys()


def eval_special_form(ast, env):
    return SPECIAL_FORMS[ast[0]](ast, env)
