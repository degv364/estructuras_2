
CC := g++
TARGET := main.x

CFLAGS := -std=c++11 -Wall -c -pedantic -pthread `pkg-config --cflags opencv`
LFLAGS := `pkg-config --libs opencv` -pthread

SRC := $(wildcard *.cpp)
OBJS := $(SRC:.cpp=.o)


all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) $(LFLAGS) -o $(TARGET)	

%.o: %.cpp
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -rf *.o $(TARGET)
