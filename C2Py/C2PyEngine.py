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

This module is the core of the C2Py library and does all the heavy logic of struct conversion
"""

import re
import string
import ctypes

__author__ = "Sagie Levy"
__copyright__ = "Copyright 2015, Tandem Group Software"
__license__ = "Apache"

# Global methods and 'constants'
HIERARCHY_SEPARATOR = "."
POINTER_MARK = "*"
FIRST_READABLE_CHAR_INDEX = 32
DEFAULT_ENUM_VAL = -1

# This might not be true for all users, but I think it's better off limiting characters like this
LAST_READABLE_CHAR_INDEX = 126

FORMAT_MAP = {
    # Not using c_char because it limits char use to strings only, not "bytes" or numeric values, as well
    "char": ctypes.c_byte,
    "signed char": ctypes.c_byte,
    "unsigned char": ctypes.c_ubyte,
    "_Bool": ctypes.c_bool,
    "short": ctypes.c_short,
    "unsigned short": ctypes.c_ushort,
    "int": ctypes.c_int,
    "unsigned int": ctypes.c_uint,
    "unsigned": ctypes.c_uint,
    "signed": ctypes.c_int,
    "long": ctypes.c_long,
    "unsigned long": ctypes.c_ulong,
    "long long": ctypes.c_longlong,
    "unsigned long long": ctypes.c_ulonglong,
    "float": ctypes.c_float,
    "double": ctypes.c_double,
    "long double": ctypes.c_longdouble,
    "char *": ctypes.c_char_p,
    "void *": ctypes.c_void_p
}

# Important regular expressions to parse C structs to groups of fields (in strings) and from them create formats
# Not broken down to multiple lines for readability
STRUCTS_REGEX = re.compile(
    r"(typedef\s+)?(?P<PACKED>\w+)?\s*(?P<TYPE>union|struct|enum)\s+(?P<NAME2>\w+)\s*\{(?P<FIELDS>.*?(?:\{.*?\}.*?)*?)\}(?P<NAME>[^;]*);",
    re.S)
ENUM_TYPES_REGEX = re.compile(r"(?P<NAME>\w+)\s*(=(?P<DEF>.[^,]*)|,|$)", re.S)
BASIC_TYPES_REGEX = re.compile(
    r"typedef\s*(volatile)?(?P<DEF>[^\(\[{;,]*[\s|*])(?P<TYPE>\w+\s*)(?P<ARRAY>\[.*?\])?(;|,(?P<ADDITIONAL_TYPES>.*?;))\s*(?://\s*@!\s*SN\s+([^\n\r]+)[\n\r$])?",
    re.S)
COMMENT_REMOVE = re.compile(r"//.*", re.MULTILINE)
FIELDS_REGEX = re.compile(
    r"\s*(static|const)?\s*(static|const)?\s*(volatile)?\s*(?P<KEYWORD>struct|union|enum)?\s*(?P<TYPE>.*?(\s*\*)?)\s*(?:\{(?P<SUB_FIELDS>.*?)\}\s*)?\s*(?P<NAME>\w+)?\s*(?:\s*(?P<ARRAY>\[[^\n\r;]+)\s*\s*)*(?::\s*(?P<BIT_FIELD>[^\[\]\{\};\n\r]+)?)?;",
    re.S)


def is_readable_char(numeric_value):
    """
    Attempt to convert int parameter to a character
    :param numeric_value: Input as int
    :return: True if input may be a char. False if not
    """
    try:
        return chr(numeric_value) and FIRST_READABLE_CHAR_INDEX <= numeric_value <= LAST_READABLE_CHAR_INDEX
    except ValueError:
        return False


def print_dynamic_func(self):
    """
    Calls the recursive print function. The "self" param is problematic here
    :return: String representation of given struct
    """
    return recursive_print(self)


def recursive_print(obj_to_parse, header="", obj_type=None):
    """
    Print all values from the struct or union
    :param obj_type: The ctypes type of current object
    :param obj_to_parse: Prints values from given object
    :param header: Parents of current object
    :return: String representation of object
    """
    if issubclass(type(obj_to_parse), (ctypes.Structure, ctypes.Union)):
        # Go into every field in the struct and print it
        complete_result = "\n" if len(header.split(HIERARCHY_SEPARATOR)) > 1 else ""

        for field in obj_to_parse._fields_:
            field_name = field[0]
            field_type = field[1]
            curr_item = getattr(obj_to_parse, field_name)

            # Concatenate the items
            complete_result += ("\t" * len(header.split(HIERARCHY_SEPARATOR))) + header + field_name + \
                               (" {" if issubclass(type(curr_item),
                                (ctypes.Structure, ctypes.Union)) else ": ") + \
                recursive_print(curr_item, header + field_name + HIERARCHY_SEPARATOR, field_type) + \
                               ("\n" + ("\t" * (len(header.split(HIERARCHY_SEPARATOR)) - 1)) + "}" if
                                len(header.split(HIERARCHY_SEPARATOR)) > 1 and obj_to_parse._fields_[-1] == field
                                else "\n")

        # Finally return the total string of the scope
        return complete_result
    elif issubclass(type(obj_to_parse), ctypes.Array):
        # Print every item in the array
        # The _array_ attribute is the original type of this array
        return '[' + ', '.join(recursive_print(item, header, obj_to_parse._type_) for item in obj_to_parse) + ']'
    elif obj_type in (ctypes.c_byte, ctypes.c_ubyte):
        # Print byte as a character if it is readable
        return chr(obj_to_parse) if is_readable_char(obj_to_parse) else hex(obj_to_parse)
    elif issubclass(type(obj_to_parse), (int, long)):
        # Print integers in hex
        return hex(obj_to_parse)
    else:
        return str(obj_to_parse)


class C2PyConverter(object):
    """
    This class processes C code (without macros and other defines - a.k.a intermediate files (*.i)) and creates a
    duplicate class in Python with the same structure. If a byte buffer is given, this converter will also populate the
    struct with the appropriate values
    """

    @staticmethod
    def _generate_new_struct(param_struct_type, pragma_pack=None):
        """
        Generate a new class of some dynamic structure
        :param param_struct_type: Structure type
        :param pragma_pack: Pragma packing value if defined for the given struct
        :return: New empty struct class (currently only pragma packed 1).
        """
        class DynamicStruct(ctypes.Structure):
            """
            A little-endian struct
            """
            # These attributes MUST be defined as such.
            # The ctypes module uses them so their names must be as following.
            if pragma_pack is not None:
                # Define pragma packing if value was given
                _pack_ = pragma_pack
            struct_type = param_struct_type

            # Hold ref to the print function
            print_dynamic = print_dynamic_func

            # When required representation, "str(struct)", show the attributes of the struct and their values
            def __repr__(self):
                repr_val = self.struct_type + " {\n"
                repr_val += self.print_dynamic() + "}"

                return repr_val

        return DynamicStruct

    @staticmethod
    def _generate_new_union(param_union_name, pragma_pack=None):
        """
        Generate a new class of some dynamic union
        :param param_union_name: Union instance
        :param pragma_pack: Pragma packing value if defined for the given struct
        :return: New empty union class (currently only pragma packed 1).
        """
        class _DynamicUnion(ctypes.Union):
            # These attributes MUST be defined as such.
            # The ctypes module uses them so their names must be as following.
            if pragma_pack is not None:
                # Define pragma packing if value was given
                _pack_ = pragma_pack
            union_type = param_union_name

            # Hold ref to the print function
            printDynamic = print_dynamic_func

            # When required representation, "str(union)", show the attributes of the union and their values
            def __repr__(self):
                repr_val = self.union_type + " {\n"
                repr_val += self.printDynamic() + "}"

                return repr_val

        return _DynamicUnion

    def _generate_new_dynamic(self, object_type, object_name, pragma_pack=None):
        """
        Generate a new class of some dynamic union or struct
        :param object_type: union or struct
        :param object_name: Instance name
        :param pragma_pack: Pragma packing value if defined for the given struct
        :return: New empty relevant class (currently only pragma packed 1).
        """
        if object_type == "struct":
            return self._generate_new_struct(object_name, pragma_pack)
        elif object_type == "union":
            return self._generate_new_union(object_name, pragma_pack)

    def __init__(self):
        self._result = None
        self._valueIndex = 0
        self._content = ""
        self._basics_dic = {}
        self._enum_types = []
        self._structures_dic = {}
        self._pointer_struct_dic = {}
        self._pragma_pack_dic = {}
        self._pragma_stack = []
        self._result = None
        self._dynamic_structure = self._generate_new_struct("")

    def clear_content(self):
        """
        Resets the content holder variable
        :return:
        """
        self._content = ""

    def add_content(self, more_content):
        """
        Append C code to the already set content.
        Please note that this method does not process the content, but the processing must be done
        before attempting struct conversion.
        :param more_content: Content to add to the content holder
        :return:
        """
        self._content += more_content + '\n'

    def convert(self, struct_type, data_bytes, offset=0):
        """
        Parse a struct from the C code and populate it with buffer values
        :param struct_type: The name of the struct type
        :param data_bytes: The buffer to read from (as a list of integers)
        :param offset: The offset to begin reading from
        :return: The resulting struct or union populated with selected data
        """
        # Reset relevant variables
        self._result = None
        self._valueIndex = 0

        if struct_type not in self._structures_dic and struct_type not in self._pointer_struct_dic:
            raise SyntaxError("The required structure is not provided by the config file: '{0}'".
                              format(struct_type))
        else:
            # Select relevant struct dictionary
            matching_struct_dict = self._structures_dic \
                if struct_type in self._structures_dic else self._pointer_struct_dic

            self._dynamic_structure = self._extract_instance(
                matching_struct_dict[struct_type].group("FIELDS").strip(" \t\n\r"),
                matching_struct_dict[struct_type].group("TYPE").strip(" \t\n\r"),
                struct_type)

        self._result = self._create_union_result(self._dynamic_structure,
                                                 bytearray(data_bytes)[offset: offset +
                                                                       ctypes.sizeof(self._dynamic_structure)])
        return self._result.struct_data

    def parse(self):
        """
        Parse the entire set content to prepare for future reading of structs.
        Split the data parsed into specific relevant dictionaries.
        :return:
        """
        # Clear all global variables before parsing
        self._enum_types = []
        self._pragma_stack = []
        self._basics_dic.clear()
        self._structures_dic.clear()
        self._pointer_struct_dic.clear()
        self._pragma_pack_dic.clear()

        # Remove all comments
        self._content = COMMENT_REMOVE.sub("", self._content)

        # Go over all the structs unions and enums in the code
        for match in STRUCTS_REGEX.finditer(self._content):
            for name_or_ptr in match.group("NAME").split(","):

                # Check that string isn't null or just whitespace
                # And that the name is of a union or a struct, but NOT an enum
                if name_or_ptr not in ("", None) and match.group("TYPE").strip(" \t\n\r") in ("struct", "union"):
                    name_or_ptr = name_or_ptr.strip(" \t\n\r")

                    # Don't cause multiple keys
                    if name_or_ptr in self._structures_dic:
                        break

                    # Pointers to pointers dict and struct names to struct dict
                    if POINTER_MARK not in name_or_ptr:
                        self._structures_dic[name_or_ptr] = match
                    else:
                        self._pointer_struct_dic[name_or_ptr.replace(POINTER_MARK, "")] = match

            # If no break occurred, that is, if NAME tag wasn't found or TYPE was not struct or union
            else:
                # If this is a struct or a union, it may not have a typedef in which 'struct NAME2' must be used
                if match.group("TYPE") in ("struct", "union") and match.group("NAME") in ("", None):
                    # Set the default name as the name of the struct
                    self._structures_dic[match.group("NAME2").strip(" \t\n\r")] = match

                # If type is actually an enum, add it to the fields dictionary for future use first
                elif match.group("TYPE") == "enum":
                    # Get the enum name
                    enum_name = match.group("NAME").strip(" \t\n\r") if match.group("NAME") not in ("", None) \
                        else match.group("NAME2").strip(" \t\n\r")

                    # Add to the list of known enums
                    self._enum_types.append(enum_name)

                    # Keep previous, init with -1
                    prev_enum_val = -1

                    # Go over all enum fields
                    for i, enum_data in enumerate(ENUM_TYPES_REGEX.finditer(match.group("FIELDS"))):
                        # Create global variables from enum fields, so they will be available for all! Viva La France!
                        if enum_data.group("DEF") is None:
                            enum_value = prev_enum_val + 1
                        else:
                            trimmed_code_line = enum_data.group("DEF").translate(None, " \t\n\r")

                            # Get all the operands in the string
                            for operand in re.finditer("\w*", trimmed_code_line):
                                operand = operand.group()

                                # Check if string is actually a number with the "UL" extension at the end
                                if operand.endswith("UL") and self._is_number(operand[:-2]):
                                    # Also remove ...UL because it means Unsigned Long and python can't parse it
                                    trimmed_code_line = trimmed_code_line.replace(operand, operand.rstrip("UL"))

                            # Reset variable. If eval fails, this value shall be placed
                            enum_value = DEFAULT_ENUM_VAL

                            # Remove bad spaces and stuff like that. 
                            try:
                                enum_value = eval(trimmed_code_line)
                            except:
                                # Can't evaluate this line of code..
                                # This must be some kind of crazy corner case code that's probably not very important
                                # If it is, please implement some logic that would allow evaluating this. Thanks!
                                print("Can't evaluate the following string: " + trimmed_code_line)

                        # Add enum value to the globals of this module for future use.. Yes, it's necessary.
                        e_field_name = enum_data.group("NAME").strip(" \t\n\r")
                        if e_field_name not in globals():
                            globals()[e_field_name] = enum_value
                            prev_enum_val = enum_value

        for match in BASIC_TYPES_REGEX.finditer(self._content):
            curr_var_type = match.group("TYPE").strip(" \t\n\r")

            if curr_var_type not in self._basics_dic:
                self._basics_dic[curr_var_type] = match

                # Check for additional types
                additional_types = match.group("ADDITIONAL_TYPES")
                if additional_types is not None:
                    for currAdditional in additional_types.split(","):
                        self._basics_dic[currAdditional.strip(" \t\n\r")] = match

    @staticmethod
    def _is_number(value):
        """
        Validate parameter is number (i.e. check if characters are for representing hex value)
        :param value: Value to check
        :return: True if value is a number. False if not
        """
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def _make_array(arrType, dimensions):
        """
        Create an array in ctypes.
        Array will be 'n' dimensions depending on the length of the dimensions list. Evaluate string to code
        :param arrType: The type of the array variable
        :param dimensions: A list of dimensions. Each value represents the number of cells in dimension 'n'
        :return: Generic ctypes array
        """
        # Deal with cases were the outermost dimension is omitted or is 0 a.k.a "Struct Hack".
        if dimensions[-1] == POINTER_MARK or dimensions[-1] == 0:
            #######################################################################
            # THIS IS RELEVANT WHEN COMPILING WITH VISUAL STUDIO - POINTER WAS 4BYTES #
            # if len(dimensions) == 1:
            # # In case the hack field is the only field in the struct, it is treated as a normal pointer
            # return ctypes.c_void_p
            #######################################################################

            # For GCC, no memory at all is allocated for this pointer NO MATTER WHAT.
            # This field's size would be allocated at runtime. That's out of scope for our C2Py engine
            return None

        # Default value for the first dimension
        result = "(arrType * dimensions[0])"

        for i in xrange(1, len(dimensions)):
            result = "({0} * dimensions[{1}])".format(result, i)

        return eval(result)

    def _extract_instance(self, struct_data, object_type, struct_type_name):
        """
        Extracts a struct by its type and returns its ctypes dynamically built struct or union.
        Will recursively parse and build the struct or union and any inner structs
        :param struct_data: The C code of the current struct
        :param object_type: The type of the current object being parsed
        :param struct_type_name: Name of struct or union type
        :return: Dynamic struct or union with appropriate fields
        """
        attributes = []
        curr_dynamic = self._generate_new_dynamic(object_type, struct_type_name,
                                                  self._pragma_pack_dic[struct_type_name]
                                                  if struct_type_name in self._pragma_pack_dic else None)

        for fieldMatch in FIELDS_REGEX.finditer(struct_data):
            # Define and init current type
            curr_type = None
            sub_fields = fieldMatch.group("SUB_FIELDS")

            # Get to the source of all fields till all primitives are reached
            if not (sub_fields is None or sub_fields.isspace()):
                raise NotImplementedError
            else:
                # Find filled type and name
                field_type = fieldMatch.group("TYPE").strip(" \t\n\r")

                # TODO Not the best implementation. Should Override NAME key with value of NAME2 if former is None
                field_name = fieldMatch.group("NAME").strip(" \t\n\r") if fieldMatch.group("NAME") not in ("", None) \
                    else fieldMatch.group("NAME2").strip(" \t\n\r")
                field_length = fieldMatch.group("ARRAY")
                bitfield_length = fieldMatch.group("BIT_FIELD")

                # If the current field is array, do the following
                if field_length not in (None, ""):
                    field_length = self._parse_length(field_length.strip(" \t\n\r"))

                # If field is a struct, set a new class/struct in the field
                if field_type in self._structures_dic:
                    # Remove whitespace before using the struct code, because apparently it may cause
                    # "Catastrophic Backtracking"!! Very scary                    
                    curr_struct = self._extract_instance(self._structures_dic[field_type].
                                                         group("FIELDS").strip(" \t\n\r"),
                                                         self._structures_dic[field_type].
                                                         group("TYPE").strip(" \t\n\r"),
                                                         field_type)
                    # Add an array or a single value
                    if field_length not in (None, ""):
                        attributes.append((field_name, self._make_array(curr_struct, field_length)))
                    else:
                        attributes.append((field_name, curr_struct))

                # If the field is a pointer to a struct, treat it as just another pointer
                elif field_type in self._pointer_struct_dic:
                    curr_type = ctypes.c_void_p
                elif field_type in self._enum_types:
                    # Treat all enums as signed int. This is compiler dependant really but this would do
                    curr_type = FORMAT_MAP.get("int")
                else:
                    # Add type if it is a primitive.
                    curr_type = self._get_type(field_type)

                    # Make it an array if field length given
                    if field_length not in (None, ""):
                        curr_type = self._make_array(curr_type, field_length)

                # If the type is indeed primitive, append it to the attributes name along with its
                # type. Has to be a string too
                if curr_type is not None:
                    # If the current field is a bitfield, add the value to the fields list initializer
                    if bitfield_length not in (None, ""):
                        attributes.append((field_name, curr_type, int(bitfield_length.strip(" \t\n\r"))))
                    else:
                        # Append a new primitive normally
                        attributes.append((field_name, curr_type))

        # Create the final _fields_ attribute
        curr_dynamic._fields_ = attributes

        # return formatStr, attributes
        return curr_dynamic

    def _get_type(self, field_type):
        """
        :param field_type: The name of the field type in C to convert to the python format
        :return: A primitive data type if found, or a typedef name of some type
        """
        # If field type is a pointer, simply select the c_void_p type
        if POINTER_MARK in field_type:
            return ctypes.c_void_p

        if field_type in self._basics_dic:
            # Get the type within the current typedef. If it's another typedef this will be called again
            # If it's a primitive value the format map will convert it
            return self._get_type(self._basics_dic[field_type].group("DEF").strip(" \t\n\r"))

        elif field_type in FORMAT_MAP:
            return FORMAT_MAP[field_type]

        else:
            # This is so that the current type will be none
            raise Exception("Type unknown: '" + str(field_type) + "'. Maybe a some code's missing?")

    def _parse_length(self, field_length):
        """
        Parse the given size of an array
        Will raise exception if the expression is invalid or not supported somehow
        :param field_length: The expression within the array brackets in C
        :return: The size of the array
        """
        result = []

        # Go over each dimension
        for match in re.finditer("\[.*?\]", field_length):
            curr_dimension = match.group()

            # First off, convert all brackets to parenthesises
            curr_dimension = curr_dimension.translate(None, "[]")

            # If length is a number, append it and move on to the next dimension
            if curr_dimension.isdigit():
                result.append(string.atoi(curr_dimension))
            # Check for an empty expression. If empty, this is a pointer. e.g. char[] == char*
            elif curr_dimension == "":
                result.append(POINTER_MARK)
            else:
                # Deal with sizeof if found.
                sizeof_pos = curr_dimension.find("sizeof")

                if sizeof_pos != -1:
                    sizeof_inner = curr_dimension[curr_dimension[sizeof_pos:].index("(") + sizeof_pos + 1:
                                                  curr_dimension[sizeof_pos:].index(")") + sizeof_pos]

                    if any(sizeof_inner in currList for currList in [self._basics_dic, FORMAT_MAP]):

                        # If the sizeof function holds a primitive or typedef of a primitive, get its value
                        sizeof_value = ctypes.sizeof(self._get_type(sizeof_inner))
                    else:
                        # The item is a struct. Calculate the struct size
                        sizeof_value = ctypes.sizeof(self._extract_instance(self._structures_dic[sizeof_inner].
                                                                            group("FIELDS").strip(" \t\n\r"),
                                                                            self._structures_dic[sizeof_inner].
                                                                            group("TYPE").strip(" \t\n\r"),
                                                                            sizeof_inner))

                    # Remove the sizeof text, replace it with the actual size
                    curr_dimension = curr_dimension.replace(curr_dimension[sizeof_pos:
                                                                           curr_dimension[sizeof_pos:].index(")") +
                                                                           sizeof_pos + 1],
                                                            str(sizeof_value))
                result.append(self._get_exec_result(curr_dimension))

        # Return list reversed to generate a ctypes array in the same manner
        # as has been defined in the intermediate file
        return result[::-1]

    @staticmethod
    def _get_exec_result(field_length):
        """
        Executes the expression and returns the result.
        An exception shall be raised if the expression cannot be evaluated
        :param field_length: The field length in C
        :return: The expression result value.
        """
        try:
            result = None

            # Check for expression. such as (a * b) + 4... etc.
            exec "result = " + field_length
            return result
        except:
            raise Exception("expression unsupported: " + field_length)

    @staticmethod
    def _create_union_result(dynamic_struct, buffer_data):
        """
        Creates a union of the buffer of data and the dynamic structure
        :param dynamic_struct: The resulting struct or union
        :param buffer_data: The data to populate the struct or union with
        :return: The given struct or union, populated with given data
        """

        class UnionWithData(ctypes.Union):
            """
            This union binds the buffer with the struct or union by holding them as two fields (that's how unions work
            in C). Only the struct field should be returned, however, so the user won't be able to access (or know
            about) the buffer array field.
            """
            _pack_ = 1
            _fields_ = [("input_buffer", ctypes.c_byte * ctypes.sizeof(dynamic_struct)),
                        ("struct_data", dynamic_struct)]

        result = UnionWithData()

        # Fill data with given buffer.
        # Attempt to fill ONLY if the size of the buffer matches that of the struct.
        # Otherwise an exception will occur. If buffer is not set, the struct will be clean (all values = 0)
        if len(buffer_data) == ctypes.sizeof(dynamic_struct):
            result.input_buffer[:] = buffer_data

        return result