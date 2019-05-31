#!/usr/bin/env python
"""
Copyright (C) 2015 Tandem Group Software

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Unittest module to show (off) the usage of this library and also to check it for bugs.
"""

import unittest
import os
from C2Py import C2PyHandler
import ctypes

__author__ = "Sagie Levy"
__copyright__ = "Copyright 2015, Tandem Group Software"
__license__ = "Apache"

# Globals
MEMORY_OFFSET = 0


def _generate_new_struct(pragma_packing=None):
    class DynamicStruct(ctypes.Structure):
        """
        Dynamic struct
        """
        # These attributes MUST be defined as such.
        # The ctypes module uses them so their names must be as following.
        if pragma_packing is not None:
            # Define pragma packing if value was given
            _pack_ = pragma_packing

    return DynamicStruct


def _generate_new_union(pragma_packing=None):
    class DynamicUnion(ctypes.Union):
        """
        Dynamic Union with pragma pack 1
        """
        # These attributes MUST be defined as such.
        # The ctypes module uses them so their names must be as following.
        if pragma_packing is not None:
            # Define pragma packing if value was given
            _pack_ = pragma_packing

    return DynamicUnion


class C2PyTest(unittest.TestCase):
    def __init__(self, test_name, c2py_handler):
        super(C2PyTest, self).__init__(test_name)
        self.c2py_handler = c2py_handler

    def test1(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test1")
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        to_compare_class._fields_ = [("a", ctypes.c_uint32),
                                     ("b", ctypes.c_char),
                                     ("c", ctypes.c_double)]
        to_compare = to_compare_class()
        to_compare.a = 4294967295 # Python3
        to_compare.b = "b"
        to_compare.c = 2.5

        try:
            self.assertEqual(test_struct.a, to_compare.a)
            self.assertEqual(test_struct.b, ord(to_compare.b))
            self.assertEqual(test_struct.c, to_compare.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test2(self):
        global MEMORY_OFFSET

        # Get second struct, use size of the first struct as offset
        test_struct = self.c2py_handler.convert("Test2", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        inner_class = _generate_new_struct()

        inner_class._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_char),
                                ("c", ctypes.c_double)]

        to_compare_class._fields_ = [("a", ctypes.c_int),
                                     ("b", inner_class),
                                     ("c", ctypes.c_double)]

        to_compare = to_compare_class()
        to_compare.a = 10
        to_compare.c = 42.0
        to_compare.b.a = 456 # Python3 
        to_compare.b.b = "r"
        to_compare.b.c = 0.1

        try:
            self.assertEqual(test_struct.a, to_compare.a)
            self.assertEqual(test_struct.c, to_compare.c)
            self.assertEqual(test_struct.b.a, to_compare.b.a)
            self.assertEqual(test_struct.b.b, ord(to_compare.b.b))
            self.assertEqual(test_struct.b.c, to_compare.b.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test3(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test3", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        inner_class = _generate_new_struct()

        inner_class._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_char),
                                ("c", ctypes.c_double)]

        to_compare_class._fields_ = [("a", ctypes.c_int),
                                     ("b", ctypes.c_char),
                                     ("c", inner_class)]

        to_compare = to_compare_class()
        to_compare.a = -2
        to_compare.b = "a"
        to_compare.c.a = 634534 # Python3
        to_compare.c.b = "6"
        to_compare.c.c = -469083479.5894

        try:
            self.assertEqual(test_struct.a, to_compare.a)
            self.assertEqual(test_struct.b, ord(to_compare.b))
            self.assertEqual(test_struct.c.a, to_compare.c.a)
            self.assertEqual(test_struct.c.b, ord(to_compare.c.b))
            self.assertEqual(test_struct.c.c, to_compare.c.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test4(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test4", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        inner_class = _generate_new_struct()
        even_deeper = _generate_new_struct()

        even_deeper._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_byte),
                                ("c", ctypes.c_double)]

        inner_class._fields_ = [("a", ctypes.c_int),
                                ("b", ctypes.c_byte),
                                ("c", even_deeper)]

        array = ctypes.c_int * 3
        nums = ctypes.c_short * 5
        to_compare_class._fields_ = [("array", array),
                                     ("nums", nums),
                                     ("recursion", inner_class)]

        to_compare = to_compare_class()

        to_compare.array = array(7, 8, 9)
        to_compare.nums = nums(300, 101, 7, 13, 12)

        to_compare.recursion.a = 2
        to_compare.recursion.b = ord("w")
        to_compare.recursion.c.a = 634534 # Python3
        to_compare.recursion.c.b = ord("6")
        to_compare.recursion.c.c = 469083479089.5894

        try:
            for first, second in zip(test_struct.array, to_compare.array):
                self.assertEqual(first, second)

            for first, second in zip(test_struct.nums, to_compare.nums):
                self.assertEqual(first, second)

            self.assertEqual(test_struct.recursion.a, to_compare.recursion.a)
            self.assertEqual(test_struct.recursion.b, to_compare.recursion.b)
            self.assertEqual(test_struct.recursion.c.a, to_compare.recursion.c.a)
            self.assertEqual(test_struct.recursion.c.b, to_compare.recursion.c.b)
            self.assertEqual(test_struct.recursion.c.c, to_compare.recursion.c.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test5(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test5", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()

        # Make a [2][3] matrix of uint by first making the first uint array and then multiply it by num of rows
        firstArr = (ctypes.c_uint * 3) * 2
        secondArr = ctypes.c_ushort * 6
        to_compare_class._fields_ = [("firstArr", firstArr),
                                     ("secondArr", secondArr),
                                     ("shorty", ctypes.c_ushort),
                                     ("four_bytes", ctypes.c_uint)]

        to_compare = to_compare_class()

        to_compare.firstArr = firstArr((ctypes.c_uint * 3)(1, 2, 3), (ctypes.c_uint * 3)(4, 5, 6))
        to_compare.secondArr = secondArr(9, 9, 9, 9, 9, 9)
        to_compare.shorty = 8
        to_compare.four_bytes = 1024

        try:
            # Get to the values of the matrices
            for first_inner, second_inner in zip(test_struct.firstArr, to_compare.firstArr):
                for first_int, second_int in zip(first_inner, second_inner):
                    self.assertEqual(first_int, second_int)

            for first, second in zip(test_struct.secondArr, to_compare.secondArr):
                self.assertEqual(first, second)

            self.assertEqual(test_struct.shorty, to_compare.shorty)
            self.assertEqual(test_struct.four_bytes, to_compare.four_bytes)

            # Modify some values and check again
            to_compare.firstArr[0][2] = 100
            test_struct.firstArr[0][2] = 100
            self.assertEqual(test_struct.firstArr[0][2], to_compare.firstArr[0][2])
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test6(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test6", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        to_compare_class._fields_ = [("aPartOne", ctypes.c_uint, 12),
                                     ("aPartTwo", ctypes.c_uint, 10),
                                     ("aPartThree", ctypes.c_uint, 1),
                                     ("someChar", ctypes.c_char_p)]
        to_compare = to_compare_class()
        to_compare.aPartOne = 2000
        to_compare.aPartTwo = 1000
        to_compare.aPartThree = 1
        to_compare.someChar = 'The Dude abides'

        try:
            self.assertEqual(test_struct.aPartOne, to_compare.aPartOne)
            self.assertEqual(test_struct.aPartTwo, to_compare.aPartTwo)
            self.assertEqual(test_struct.aPartThree, to_compare.aPartThree)

            # This field is not comparable because it only stores the address.
            # The only thing we can do is check that 'b' is a pointer (size varies depending on OS - 32 or 64 bits)
            self.assertEqual(ctypes.sizeof(test_struct._fields_[-1][1]), ctypes.sizeof(ctypes.c_void_p))
            # self.assertEqual(test_struct.someChar, to_compare.someChar)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test7(self):
        global MEMORY_OFFSET

        # This struct does not have a typedef defined in the header file
        test_struct = self.c2py_handler.convert("Test7", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        to_compare_class._fields_ = [("firstEnum", ctypes.c_int),
                                     ("secondEnum", ctypes.c_int),
                                     ("thirdEnum", ctypes.c_int)]
        to_compare = to_compare_class()
        to_compare.firstEnum = 0x6
        to_compare.secondEnum = 1
        to_compare.thirdEnum = 8

        try:
            self.assertEqual(test_struct.firstEnum, to_compare.firstEnum)
            self.assertEqual(test_struct.secondEnum, to_compare.secondEnum)
            self.assertEqual(test_struct.thirdEnum, to_compare.thirdEnum)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test8(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test8", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        inner_class = _generate_new_struct()
        inner_class._fields_ = [("firstEnum", ctypes.c_int),
                                ("secondEnum", ctypes.c_int),
                                ("thirdEnum", ctypes.c_int)]
        to_compare_class._fields_ = [("explicitNames", inner_class)]
        to_compare = to_compare_class()
        to_compare.explicitNames.firstEnum = 7
        to_compare.explicitNames.secondEnum = 6
        to_compare.explicitNames.thirdEnum = -500

        try:
            self.assertEqual(test_struct.explicitNames.firstEnum, to_compare.explicitNames.firstEnum)
            self.assertEqual(test_struct.explicitNames.secondEnum, to_compare.explicitNames.secondEnum)
            self.assertEqual(test_struct.explicitNames.thirdEnum, to_compare.explicitNames.thirdEnum)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test9(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test9", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_union()
        to_compare_class._fields_ = [("smaller", ctypes.c_short),
                                     ("very", ctypes.c_ubyte),
                                     ("small", ctypes.c_byte),
                                     ("large", ctypes.c_ulonglong)]
        to_compare = to_compare_class()
        to_compare.smaller = -100

        try:
            self.assertEqual(test_struct.smaller, to_compare.smaller)
            self.assertEqual(test_struct.very, to_compare.very)
            self.assertEqual(test_struct.small, to_compare.small)
            self.assertEqual(test_struct.large, to_compare.large)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test10(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test10", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_union()
        inner_class = _generate_new_struct()
        even_deeper = _generate_new_struct()

        even_deeper._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_char),
                                ("c", ctypes.c_double)]

        inner_class._fields_ = [("a", ctypes.c_int),
                                ("b", even_deeper),
                                ("c", ctypes.c_double)]

        to_compare_class._fields_ = [("fieldOne", ctypes.c_byte * 25),
                                     ("fieldTwo", inner_class)]
        to_compare = to_compare_class()
        to_compare.fieldOne[:] = bytearray([0, 0, 0, 0, 0, 0, 0, 0, 97, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        try:
            self.assertTrue(all(origin == test for (origin, test) in zip(test_struct.fieldOne, to_compare.fieldOne)))
            self.assertEqual(test_struct.fieldTwo.a, to_compare.fieldTwo.a)
            self.assertEqual(test_struct.fieldTwo.c, to_compare.fieldTwo.c)
            self.assertEqual(test_struct.fieldTwo.b.a, to_compare.fieldTwo.b.a)
            self.assertEqual(test_struct.fieldTwo.b.b, ord(to_compare.fieldTwo.b.b))
            self.assertEqual(test_struct.fieldTwo.b.c, to_compare.fieldTwo.b.c)

            # Validate union functionality: Change values of fields of 'fieldTwo', check their effects on 'fieldOne'
            test_struct.fieldTwo.a = 100
            self.assertEqual(test_struct.fieldOne[0], 100)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test11(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test11", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        to_compare_class._fields_ = [("string", ctypes.c_char * 13)]
        to_compare = to_compare_class()
        to_compare.string = "Hello, world\0"
        try:
            self.assertTrue(all(chr(origin) == test for (origin, test) in zip(test_struct.string, to_compare.string)))
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

    def test12(self):
        global MEMORY_OFFSET

        test_struct = self.c2py_handler.convert("Test12", offset=MEMORY_OFFSET)
        size_of = ctypes.sizeof(test_struct)
        MEMORY_OFFSET += size_of
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        ###########################################################################
        # THIS IS RELEVANT WHEN COMPILING WITH VISUAL STUDIO - POINTER WAS 4BYTES #
        # to_compare_class = _generate_new_struct()
        # to_compare_class._fields_ = [("omittedSize", ctypes.c_void_p)]
        # to_compare = to_compare_class()
        #
        # try:
        #     # A pointer so values cannot be compared. Simply check that sizeof = 4 and type is void pointer
        #     self.assertEqual(test_struct._fields_[0][1], ctypes.c_void_p)
        # except AttributeError, ex:
        #     # Fail the test
        #     self.assertFalse(True, ex)
        #
        # self.assertEqual(size_of, ctypes.sizeof(to_compare))
        ###########################################################################

        try:
            # No attributes at all for this struct
            self.assertEqual(len(test_struct._fields_), 0)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        # self.assertEqual(size_of, ctypes.sizeof(to_compare))
        self.assertEqual(size_of, 0)

    def test13(self):
        ###########################
        # Using no buffer handler #
        ###########################

        # Validate all fields == 0
        test_struct = self.c2py_handler.convert("Test4")
        size_of = ctypes.sizeof(test_struct)
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_struct()
        inner_class = _generate_new_struct()
        even_deeper = _generate_new_struct()

        even_deeper._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_byte),
                                ("c", ctypes.c_double)]

        inner_class._fields_ = [("a", ctypes.c_int),
                                ("b", ctypes.c_byte),
                                ("c", even_deeper)]

        array = ctypes.c_int * 3
        nums = ctypes.c_short * 5
        to_compare_class._fields_ = [("array", array),
                                     ("nums", nums),
                                     ("recursion", inner_class)]

        to_compare = to_compare_class()

        to_compare.array = array(0, 0, 0)
        to_compare.nums = nums(0, 0, 0, 0, 0)

        to_compare.recursion.a = 0
        to_compare.recursion.b = 0
        to_compare.recursion.c.a = 0
        to_compare.recursion.c.b = 0
        to_compare.recursion.c.c = 0

        try:
            for first, second in zip(test_struct.array, to_compare.array):
                self.assertEqual(first, second)

            for first, second in zip(test_struct.nums, to_compare.nums):
                self.assertEqual(first, second)

            self.assertEqual(test_struct.recursion.a, to_compare.recursion.a)
            self.assertEqual(test_struct.recursion.b, to_compare.recursion.b)
            self.assertEqual(test_struct.recursion.c.a, to_compare.recursion.c.a)
            self.assertEqual(test_struct.recursion.c.b, to_compare.recursion.c.b)
            self.assertEqual(test_struct.recursion.c.c, to_compare.recursion.c.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))

        # Test adding more content to the handler
        self.c2py_handler.add_intermediate_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "SecondFile.i"))

        # Test a struct from the new file
        test_struct = self.c2py_handler.convert("SecFileStrct")
        size_of = ctypes.sizeof(test_struct)
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        try:
            self.assertTrue(test_struct.number == 0)
            self.assertTrue(test_struct.otherHeaderFileStruct.a == 0)
            self.assertTrue(test_struct.otherHeaderFileStruct.b == 0)
            self.assertTrue(test_struct.otherHeaderFileStruct.c == 0)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        # Test a struct from the old file
        test_struct = self.c2py_handler.convert("Test3")
        size_of = ctypes.sizeof(test_struct)
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        try:
            self.assertTrue(test_struct.a == 0)
            self.assertTrue(test_struct.b == 0)
            self.assertTrue(test_struct.c.a == 0)
            self.assertTrue(test_struct.c.b == 0)
            self.assertTrue(test_struct.c.c == 0)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

    def test14(self):
        ################################
        # Using runtime buffer handler #
        ################################

        byte_buffer = bytearray([0, 5, 0, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 99, 0, 0, 0,
                                 0, 0, 0, 0, 0, 64, 122, 64, 0, 0, 0, 0, 0, 16, 113, 64])
        test_struct = self.c2py_handler.convert("Test10", offset=1, byte_buffer=byte_buffer)
        size_of = ctypes.sizeof(test_struct)
        print(test_struct)
        print("Size of struct: " + str(size_of) + "\n")

        to_compare_class = _generate_new_union()
        inner_class = _generate_new_struct()
        even_deeper = _generate_new_struct()

        even_deeper._fields_ = [("a", ctypes.c_uint32),
                                ("b", ctypes.c_byte),
                                ("c", ctypes.c_double)]

        inner_class._fields_ = [("a", ctypes.c_int),
                                ("b", even_deeper),
                                ("c", ctypes.c_double)]

        to_compare_class._fields_ = [("fieldOne", ctypes.c_byte * 25),
                                     ("fieldTwo", inner_class)]
        to_compare = to_compare_class()
        to_compare.fieldTwo.a = 5
        to_compare.fieldTwo.b.a = 100
        to_compare.fieldTwo.b.b = 99
        to_compare.fieldTwo.b.c = 420
        to_compare.fieldTwo.c = 273

        try:
            self.assertTrue(all(origin == test for (origin, test) in zip(test_struct.fieldOne, to_compare.fieldOne)))
            self.assertEqual(test_struct.fieldTwo.a, to_compare.fieldTwo.a)
            self.assertEqual(test_struct.fieldTwo.c, to_compare.fieldTwo.c)
            self.assertEqual(test_struct.fieldTwo.b.a, to_compare.fieldTwo.b.a)
            self.assertEqual(test_struct.fieldTwo.b.b, to_compare.fieldTwo.b.b)
            self.assertEqual(test_struct.fieldTwo.b.c, to_compare.fieldTwo.b.c)
        except AttributeError as ex:
            # Fail the test
            self.assertFalse(True, ex)

        self.assertEqual(size_of, ctypes.sizeof(to_compare))


def run_test():
    """
    Run the entire test
    :return:
    """
    # Create the handlers. Could take some time, depending on the size of the intermediate file
    file_path = os.path.dirname(os.path.abspath(__file__))
    binary_file_handler = C2PyHandler.DefaultBinaryFileC2PyHandler(os.path.join(file_path, "Source.i"),
                                                                   os.path.join(file_path, "output"))
    no_buffer_handler = C2PyHandler.DefaultNoBufferC2PyHandler(os.path.join(file_path, "Source.i"))
    runtime_buffer_handler = C2PyHandler.DefaultRuntimeBufferC2PyHandler(os.path.join(file_path, "Source.i"))

    suite = unittest.TestSuite()

    # Default binary file handler tests
    suite.addTest(C2PyTest('test1', binary_file_handler))
    suite.addTest(C2PyTest('test2', binary_file_handler))
    suite.addTest(C2PyTest('test3', binary_file_handler))
    suite.addTest(C2PyTest('test4', binary_file_handler))
    suite.addTest(C2PyTest('test5', binary_file_handler))
    suite.addTest(C2PyTest('test6', binary_file_handler))
    suite.addTest(C2PyTest('test7', binary_file_handler))
    suite.addTest(C2PyTest('test8', binary_file_handler))
    suite.addTest(C2PyTest('test9', binary_file_handler))
    suite.addTest(C2PyTest('test10', binary_file_handler))
    suite.addTest(C2PyTest('test11', binary_file_handler))
    suite.addTest(C2PyTest('test12', binary_file_handler))

    # Default no buffer handler tests
    suite.addTest(C2PyTest('test13', no_buffer_handler))

    # Default runtime buffer handler tests
    suite.addTest(C2PyTest('test14', runtime_buffer_handler))

    unittest.TextTestRunner().run(suite)

if __name__ == "__main__":
    run_test()
