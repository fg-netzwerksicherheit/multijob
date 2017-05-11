BUILD_DIR = build
INCLUDE_DIR = include

ifeq ($(PREFIX),)
	PREFIX := /usr/local
endif

INSTALL_TARGET_DIR := $(DESTDIR)$(PREFIX)
INSTALL_LIB_DIR := $(INSTALL_TARGET_DIR)/lib
INSTALL_INCLUDE_DIR := $(INSTALL_TARGET_DIR)/include

INSTALL=install
CXX = clang++
CXXFLAGS += -std=c++14
CXXFLAGS += -Weverything -Werror -Wno-c++98-compat
CPPFLAGS += -I $(INCLUDE_DIR)

SOURCES = multijob.cpp 	\
		  Args.cpp 		\
		  MultijobError.cpp

OBJECTS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.o)

DEPS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.d)

.PHONY: build clean install debug

build: $(BUILD_DIR)/libmultijob.a $(OBJECTS)

-include $(DEPS)

debug: CXXFLAGS += -g --coverage -O0
debug: build

$(BUILD_DIR)/%.o : %.cpp
	@ [ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -MMD -MF $(BUILD_DIR)/$*.d -c -o $@ $<

$(BUILD_DIR)/libmultijob.a: $(OBJECTS)
	$(AR) rcs $@ $^

clean:
	rm -rf $(BUILD_DIR)

install: build
	$(INSTALL) -d $(INSTALL_LIB_DIR) $(INSTALL_INCLUDE_DIR)
	$(INSTALL) -m 644 -t $(INSTALL_LIB_DIR) $(BUILD_DIR)/libmultijob.a
	$(INSTALL) -m 644 -t $(INSTALL_INCLUDE_DIR) ./include/multijob.h
	$(INSTALL) -d        $(INSTALL_INCLUDE_DIR)/multijob
	$(INSTALL) -m 644 -t $(INSTALL_INCLUDE_DIR)/multijob ./include/multijob/*.h
