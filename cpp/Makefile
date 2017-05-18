BUILD_DIR = build
INCLUDE_DIR = include
COVERAGE_DIR = coverage

ifeq ($(PREFIX),)
	PREFIX := /usr/local
endif

INSTALL_TARGET_DIR := $(DESTDIR)$(PREFIX)
INSTALL_LIB_DIR := $(INSTALL_TARGET_DIR)/lib
INSTALL_INCLUDE_DIR := $(INSTALL_TARGET_DIR)/include

GCOV = gcov
GCOVR = gcovr
INSTALL = install
CXXFLAGS += -std=c++14
ifneq ($(DEBUG),)
	CXXFLAGS += -g --coverage -O0
endif
CXXFLAGS += -Weverything -Werror -Wno-c++98-compat -Wno-error=shadow -Wno-padded
CPPFLAGS += -I $(INCLUDE_DIR)

SOURCES = multijob.cpp 	\
		  Args.cpp 		\
		  MultijobError.cpp \
		  conversion.cpp

OBJECTS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.o)

DEPS = $(SOURCES:%.cpp=$(BUILD_DIR)/%.d)

.PHONY: build clean install test

build: $(BUILD_DIR)/libmultijob.a $(OBJECTS)

-include $(DEPS)

$(BUILD_DIR)/%.o : %.cpp
	@ [ -d $(BUILD_DIR) ] || mkdir $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(CPPFLAGS) -MMD -MF $(BUILD_DIR)/$*.d -c -o $@ $<

test: $(BUILD_DIR)/test
	@ rm -f $(BUILD_DIR)/*.gcda
	prove $(BUILD_DIR)/test
	cd $(BUILD_DIR); $(GCOVR) --gcov-executable='$(GCOV)' --html --html-details -o ../$(COVERAGE_DIR)/index.html -r ..

$(BUILD_DIR)/test: $(BUILD_DIR)/test.o $(OBJECTS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

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
