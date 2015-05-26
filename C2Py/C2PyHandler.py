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

This module wraps up the handling of the C2Py converter to make C2Py library API more user friendly
"""

import os.path as path
import C2PyEngine

__author__ = "Sagie Levy"
__copyright__ = "Copyright 2015, Tandem Group Software"
__license__ = "Apache"


class C2pyStructsAbsHandler(object):
    """
    This class handles the parsing of the given code (C intermediate files) and the creation of
    dynamic python class objects representing the C structures with values from the given memory buffer
    """

    def __init__(self, intermediate_file_path):
        """
        Read and prepare the first given C intermediate file for use
        :param intermediate_file_path: Initial C structs file
        :return:
        """
        self.converter = C2PyEngine.C2PyConverter()

        # Read the first given intermediate c file and process it
        self.add_intermediate_file(intermediate_file_path)
        # self._process_c_structs()

    def add_intermediate_file(self, c_content_path):
        """
        Read the intermediate file and process the new data
        :param c_content_path: Path to C file
        :return:
        """
        with open(path.abspath(c_content_path)) as intermediateFile:
            self.converter.add_content(intermediateFile.read())

        # Should this be here? Bad performance if the user adds multiple files.
        # On the other hand, doesn't need to manually call this method
        self._process_c_structs()

    def clear_content(self):
        """
        Clear the current set C code from the converter
        :return:
        """
        self.converter.clear_content()

    def _read_from_memory(self):
        """
        Return the memory buffer to be read.
        This method must be overridden to provide a memory reading algorithm!
        If not overridden, an exception will be raised (sort of an abstract method).
        :return:
        """
        raise Exception("Unimplemented method. Please override this method - return the memory buffer")

    def _process_c_structs(self):
        """
        Process current set C code by calling the converter's parse method
        :return:
        """
        self.converter.parse()

    def convert(self, struct_declaration, offset=0):
        """
        Create a struct from C code and populate it with byte buffer
        :param struct_declaration: The struct name. Optional: An instance name
        :param offset: The offset from the beginning of the byte buffer
        :return: A tuple. First: Class object with attributes named after given struct field names and values as
        those in the buffer. Second: the size of the struct in bytes, may be used as offset by the user
        """
        result = self.converter.convert(struct_type=struct_declaration,
                                        data_bytes=self._read_from_memory(),
                                        offset=offset)
        return result


###################################################
# Some default implementations of generic handler #
###################################################


class DefaultBinaryFileC2PyHandler(C2pyStructsAbsHandler):
    """
    Default implementation for converting structs and populating them with buffer from binary files
    """

    def __init__(self, intermediate_file_path, binary_data_path):
        """
        :param intermediate_file_path: Path to intermediate file
        :param binary_data_path: path to binary data
        :return:
        """
        super(DefaultBinaryFileC2PyHandler, self).__init__(intermediate_file_path)
        with open(binary_data_path, "rb") as bin_data:
            # Must return a string/byte array!
            # Couple notes, currently only #pragma pack(1) is supported!!
            # Make sure to define this in your C files and validate output
            self.bin_data = bin_data.read()

    def _read_from_memory(self):
        """
        Override for getting buffer for converter
        """
        return self.bin_data


class DefaultNoBufferC2PyHandler(C2pyStructsAbsHandler):
    """
    Default implementation for converting structs without populating them with a buffer
    """

    def _read_from_memory(self):
        """
        Override for getting buffer for converter
        """
        return 0


class DefaultRuntimeBufferC2PyHandler(C2pyStructsAbsHandler):
    """
    Default implementation for converting structs with a buffer of bytes received at runtime
    """

    def __init__(self, intermediate_file_path):
        """
        :param intermediate_file_path: Path to intermediate file
        :return:
        """
        super(DefaultRuntimeBufferC2PyHandler, self).__init__(intermediate_file_path)

        # Define byte buffer attribute for future use
        self.byte_buffer = 0

    def _read_from_memory(self):
        """
        Override for getting buffer for converter
        """
        return self.byte_buffer

    def convert(self, struct_declaration, offset=0, byte_buffer=0):
        """
        Override for original handler's convert method.
        :param struct_declaration: super
        :param offset: super
        :param byte_buffer: Buffer to fill given struct or union with. Make sure buffer size is equal to given
        struct or union
        :return: super
        """
        self.byte_buffer = byte_buffer
        return super(DefaultRuntimeBufferC2PyHandler, self).convert(struct_declaration, offset)