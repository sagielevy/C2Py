/*
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
*/

#ifndef HEADER
#define HEADER

typedef unsigned int U_32;
typedef unsigned short U_16;
typedef U_32 my_Num;

# define SOME_MACRO (1 + 2) * 2

enum someEnum {
	val1,
	val2,
	val3 = SOME_MACRO
};

typedef enum otherEnum
{
	first = val3,
	second,
	third
} otherEnum;

typedef struct Test1
{
	unsigned int a;
	char b;
	double c;
} Test1;

//#pragma pack(push, 1)
typedef struct Test2
{
	int a;
	Test1 b;
	double c;
} Test2;
//#pragma pack(pop)

//#pragma pack(push, 2)
typedef struct Test3
{
	int a;
	char b;
	Test1 c;
} Test3;
//#pragma pack(pop)

#define A_NUMBER 5

typedef struct Test4
{
	int array[3];
	short nums[A_NUMBER];
	Test3 recursion;
} Test4;

typedef struct Test5
{
	U_32 firstArr[2][3];
	U_16 secondArr[6];
	U_16 shorty;
	my_Num four_bytes;
} Test5;

typedef struct Test6
{
	unsigned int aPartOne : 12;
	unsigned int aPartTwo : 10;
	unsigned int aPartThree : 1;
	char* someChar;
} Test6, *PointerToTest6;

// Recursive declaration of structs
struct Test8
{
  // No typedef for this one
  struct Test7
  {
	  // Test different enums
	  otherEnum firstEnum;
	  enum someEnum secondEnum;
  	  otherEnum thirdEnum;
  };
	struct Test7 explicitNames;
};

typedef union Test9
{
	short smaller;
	unsigned char very;
	char small;
	unsigned long long large;
} Test9;

union Test10
{
	char fieldOne[sizeof(Test2)];
	Test2 fieldTwo;
};

// Struct hack, with other fields
typedef struct Test11
{
	char string[13];
	char omittedSize[][3];
} *Test11_PTR, Test11;

// Struct hack, with only the special field
typedef struct Test12
{
	char omittedSize[0];
} *Test12;

#endif