
CC := g++
TARGET := main.x

CFLAGS := -std=c++11 -Wall -c -Iinclude -pedantic -pthread `pkg-config --cflags opencv`
LFLAGS := `pkg-config --libs opencv` -pthread -Iinclude

SRC := $(wildcard src/*.cpp)
HEADER :=$(include/*.hh)
OBJS := $(SRC:.cpp=.o)


all: $(TARGET)

$(TARGET): $(OBJS) $(HEADER)
	$(CC) $(OBJS) $(LFLAGS) -o $(TARGET)	

%.o: %.cpp $(HEADER)
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf src/*.o *.dat *.pdf $(TARGET)
