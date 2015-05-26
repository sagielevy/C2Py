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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Header.h"


#define N 8
int main()
{
	Test1 instance = { -1, 'b', 2.5 };
	Test2 weird = { 10, { 456, 'r', 0.1 }, 42.0 };
	Test3 other = { -2, 'a', { 634534, '6', -469083479.5894 } };
	Test4 yoda = { { 7, 8, 9 }, { 300, 101, 7, 13, 12 }, { 2, 'w', { 634534, '6', 469083479089.5894 } } };
	Test5 ninja = { { { 1, 2, 3 }, { 4, 5, 6 } }, { 9, 9, 9, 9, 9, 9 }, 8, 1024 };
	Test6 bitfield = { 2000, 1000, 1, "That rug really tied the room together" };
	PointerToTest6 pointer = &bitfield;
	struct Test7 test7 = { first, val2, third };
	struct Test8 wowSoMany = { { second, val3, -500 } };
	Test9 someUnion = { -100 };
	union Test10 test10 = { 0, 0, 0, 0, 0, 0, 0, 0, 97, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };
	//Test11 hello = { "Hello, world!", { "ran", "dom", " st", "rin", "g.." } };
	Test11 hello;
	Test12 hacker = malloc(sizeof(struct Test12) + sizeof(char) * N);
	int i;
	FILE *fileWriter = NULL;

	// Populate allocated struct field
	for (i = 0; i < N; i++)
	{
		hacker->omittedSize[i] = '0' + i;
	}

	strncpy(hello.string, "Hello, world", 13);

	fileWriter = fopen("output", "wb");
	fwrite(&instance, sizeof(Test1), 1, fileWriter);
	fwrite(&weird, sizeof(Test2), 1, fileWriter);
	fwrite(&other, sizeof(Test3), 1, fileWriter);
	fwrite(&yoda, sizeof(Test4), 1, fileWriter);
	fwrite(&ninja, sizeof(Test5), 1, fileWriter);
	fwrite(pointer, sizeof(Test6), 1, fileWriter);
	fwrite(&test7, sizeof(struct Test7), 1, fileWriter);
	fwrite(&wowSoMany, sizeof(struct Test8), 1, fileWriter);
	fwrite(&someUnion, sizeof(Test9), 1, fileWriter);
	fwrite(&test10, sizeof(union Test10), 1, fileWriter);
	fwrite(&hello, sizeof(Test11), 1, fileWriter);
	fwrite(hacker, sizeof(struct Test12), 1, fileWriter);
	fclose(fileWriter);

	// For debug purposes
	printf("first sizeof %d, second sizeof %d, third sizeof %d, forth sizeof %d, fifth sizeof %d, sixth sizeof %d, seventh sizeof %d, eigth sizeof %d, nineth sizeof %d, tenth sizeof %d, eleventh sizeof %d, twelveth sizeof %d",
		sizeof(Test1), sizeof(Test2), sizeof(Test3), sizeof(Test4), sizeof(Test5), sizeof(Test6), sizeof(struct Test7), sizeof(struct Test8), sizeof(Test9), sizeof(union Test10), sizeof(Test11), sizeof(struct Test12));

	getchar(); // Pause
}