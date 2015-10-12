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
        if len(ast) == 0:
            raise LispError("Calls on empty list")

        form = ast[0]
        if is_special_form(form):
            return eval_special_form(ast, env)
        elif is_math(form):
            return eval_math(ast, env)
        elif is_closure(form):
            return eval_closure(ast, env)
        elif is_symbol(form):
            return eval_user_form(ast, env)
        else:
            return call(ast, env)

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


@expected_length(3)
def eval_lambda(ast, env):
    params = ast[1]
    if not is_list(params):
        raise LispError('Lambda parameters must be a list')
    body = ast[2]
    return Closure(env, params, body)


def eval_closure(ast, env):
    closure = ast[0]
    args = [evaluate(arg, env) for arg in ast[1:]]
    l_args = len(args)
    l_params = len(closure.params)
    if l_args != l_params:
        raise LispError(
            '{} wrong number of arguments, expected {} got {}'.format(
                ast, l_params, l_args
            )
        )
    env = closure.env.extend(dict(zip(closure.params, args)))
    return evaluate(closure.body, env)


def eval_user_form(ast, env):
    closure = env.lookup(ast[0])
    e = [closure]
    e.extend(ast[1:])
    return evaluate(e, env)


def call(ast, env):
    evaluated = [evaluate(a, env) for a in ast]
    if not is_closure(evaluated[0]):
        raise LispError("{} is not a function in {}".format(
            evaluated[0], evaluated
        ))
    return evaluate(evaluated, env)


SPECIAL_FORMS = {
    'quote': eval_quote,
    'atom': eval_atom,
    'eq': eval_eq,
    'if': eval_if,
    'define': eval_define,
    'lambda': eval_lambda
}


def is_special_form(form):
    return form in SPECIAL_FORMS.iterkeys()


def eval_special_form(ast, env):
    return SPECIAL_FORMS[ast[0]](ast, env)
