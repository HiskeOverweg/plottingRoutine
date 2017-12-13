# -*- coding: utf-8 -*-
"""
Created on Sun Nov  5 13:20:24 2017

Adapted from
https://docs.scipy.org/doc/numpy-1.13.0/user/basics.subclassing.html
@author: hiske
"""
import numpy as np


class data(np.ndarray):

    def __new__(cls, input_array, u=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.u = u
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.u = ''
