# C2Py Struct Converter
Import memory dumps to Python classes generated according to defined C-structs, accelerating debugging and automation testing.

## What does it do?
C2Py is here to help you convert your C structs and unions to Python classes with the same fields, names types and everything!
That's not all though. C2Py can receive a buffer of bytes or memory dumps to assign to the struct's fields!

## Why use it? 
This project could be most likely be used for automation testing for C projects.
Another use is perhaps debug - reading and understanding a memory dump better by importing it to readable struct-like classes.

## Installation
This package requires Python 3.*
Simply download this project, open cmd or terminal and enter:
```console
  python /path/to/C2Py/setup.py install
```
And you're done!

## Usage & Examples
As mentioned in before, this package is to assist C developers use the ctypes module by automatically parsing (and populating) their structs.
This is done simply by providing the source files (intermediate files or *.i files - more on that later) and (optional) binary data files or byte arrays to provide 
data to assign to the parsed structs/unions.
```c
struct my_struct {
  int a;
  char c;
};
...

// Instance of my_struct, later saved into a binary file
struct my_struct instance;
instance.a = 5;
instance.c = 'o';
```
And the conversion (assuming there's a binary file with saved data from mentioned C struct):
```python
import C2PyHandler
binary_file_handler = C2PyHandler.DefaultBinaryFileC2PyHandler("path\\to\\SourceIntermediate.i", "path\\to\\binaryfile")
result_struct = binary_file_handler.convert(struct_declaration="my_struct")
print(result_struct.a) # Prints 5
print(result_struct.b) # Prints 'o'
```
The API is quite simple:

1. Create a new instance of the handler of you choice:
  * DefaultBinaryFileC2PyHandler - For populating the converted structs with data from binary files.
  * DefaultNoBufferC2PyHandler - For creating converted structs with all values initialized as 0.
  * DefaultRuntimeBufferC2PyHandler - For populating the converted structs with data provided at runtime (preferably via 'bytearray')
  * Create your own custom handler by overriding the "abstract" 'C2pyStructsAbsHandler'. This class has one unimplemented method: '_read_from_memory', which one must override should one write a custom handler.

2. Call the 'convert' method with the proper parameters. Do note that different parameters may be required, depending on the handler used.

For more examples and how-to's please refer to the test.py module and source code found in the 'tests\' directory.

**Intermediate files**
C2Py could receive .h or .c files, but it works best with .i files. This is because C2Py does not parse macros (#define ...),
but intermediate files, or preprocessed files, are files which are generated during compilation and deleted afterwards.
They aren't normally used by the average C developer. Don't worry if you've never heard of them (I haven't till I started working on this project).
All you need to do is add a flag to your compilation process to keep these files. If you're using gcc you may use the Makefile under 'tests\' for reference.

## Tests
All test related files can be found under the 'tests\' directory. 
This package comes with C source files and headers, to be used in conjunction with the Python test.
To compile and receive the relevant files:

1. Run a 'make' command when in the 'tests\' directory (this requires having a compiler like gcc installed).

  *IMPORTANT NOTE* Please use make sure to compile with the appropriate gcc version (32 or 64 bit) that suits your installed Python executable version.
  Otherwise some variable types may be in different sizes and the memory dump may not be read correctly.

  After compiling you should see three files have been generated: Source.i, SecondFile.i, generateTestData.exe.

2. Run the executable to generate a binary file which the test will read. Should be named 'output'.

3. In Python console, run the following:
   ```python
   import C2Py.tests.test as test
   test.run_test()
   ```
   Expect test output to the console. All tests should pass.
 
This package has been tested with gcc 4.9.2, Python 3.8.5

## Not Supported (nor will be)
Some potential features will unfortunately NOT be supported by this package:
* Generating an array of structs\unions. The convert method's first parameter will receive ONLY a struct declaration name or typedef name.
  to generate an array of structs while populating them from a binary file, for example, simply use a loop and the 'offset' parameter in 'convert()' to access the correct memory section in the file.
* char arrays (or strings). All chars shall be treated as bytes. Bytes with a value representing a readable ASCII character (currently set between the range of 32 to 126) shall be
  displayed as a character. All other values shall be displayed as integer in hex representation. All byte arrays shall be shown in a list form, never a string.

## Contributors
Sagie Levy

## License
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
