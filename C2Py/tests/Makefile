CC=gcc
CFLAGS=-I.
DEPS = Header.h
OBJ_1 = Source.o
OBJ_2 = SecondFile.o

%.o: %.c $(DEPS)
	$(CC) -c -save-temps -o $@ $< $(CFLAGS)

all : makesourcetest makesecondfiletest clean
	
makesourcetest: $(OBJ_1)
	gcc -o generateTestData.exe $^ $(CFLAGS)

makesecondfiletest: $(OBJ_2)
	gcc -o $@ $^ $(CFLAGS)

clean:
	rm -f *.o *.s makesecondfiletest*