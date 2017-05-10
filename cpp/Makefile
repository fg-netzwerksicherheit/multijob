BUILD_DIR = build
INCLUDE_DIR = include

CXX = clang++
CXXFLAGS += -std=c++14
CXXFLAGS += -Weverything -Werror -Wno-c++98-compat
CXXFLAGS += -g --coverage -O0
CPPFLAGS += -I $(INCLUDE_DIR)

SOURCES = multijob.cpp 	\
		  Args.cpp 		\
		  MultijobError.cpp

OBJECTS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.o)

.PHONY: build

build: $(OBJECTS)

$(BUILD_DIR)/%.o : %.cpp
	[ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -c -o $@ $<
