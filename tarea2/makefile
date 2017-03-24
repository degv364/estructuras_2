CFLAGS = -std=c++11 -Wall -c $(DEBUG) -pedantic -pthread `pkg-config --cflags --libs opencv`
LFLAGS = -std=c++11 -Wall $(DEBUG) -pedantic -pthread `pkg-config --cflags --libs opencv`
CC=g++
TARGET=main.x
SRC=image_wrapper.cpp
OBJS=main.cpp image_wrapper.o

all: $(TARGERT)

$(TARGET): $(OBJS)
	$(CC) $(LIBS) $(LFLAGS) $(OBJS) -o $(TARGET)	

image_wrapper.o: $(SRC)
	$(CC) $(CFLAGS) $(SRC)

clean:
	rm  *.o $(TARGET)
