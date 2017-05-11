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

DEPS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.d)

-include $(DEPS)

.PHONY: build clean

build: $(BUILD_DIR)/libmultijob.a $(OBJECTS)

$(BUILD_DIR)/%.o : %.cpp
	@ [ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -MMD -MF $(BUILD_DIR)/$*.d -c -o $@ $<

$(BUILD_DIR)/libmultijob.a: $(OBJECTS)
	$(AR) rcs $@ $^

clean:
	rm -rf $(BUILD_DIR)
