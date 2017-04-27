package multijob

import "fmt"
import "strconv"

type JobArgvConfig struct {
	jobIDKey        string
	repetitionIDKey string
}

var defaultJobArgvConfig JobArgvConfig = JobArgvConfig{"--id", "--rep"}

// ParseCommandline turns the command line arguments (see "os.Args") into a
// queryable "Args" object.
//
// Argument "argv" contains the arguments to be parsed.
//
// Argument "config" will usually be "nil", but can be explicitly provided to
// override the "--id" or "--rep" special argument names.
func ParseCommandline(argv []string, config *JobArgvConfig) (args *Args, err error) {
	if config == nil {
		config = &defaultJobArgvConfig
	}

	separator := "--"

	specialArgs, normalArgs, err := separateArgvIntoSpecialAndNormalKVs(
		argv, separator)

	jobIDStr, ok := specialArgs[config.jobIDKey]
	if !ok {
		err = fmt.Errorf("multijob: special JobID argument %q required",
			config.jobIDKey)
		return
	}

	repetitionIDStr, ok := specialArgs[config.repetitionIDKey]
	if !ok {
		err = fmt.Errorf("multijob: special RepetitionID argument %q required",
			config.repetitionIDKey)
		return
	}

	delete(specialArgs, config.jobIDKey)
	delete(specialArgs, config.repetitionIDKey)

	if len(specialArgs) > 0 {
		err = fmt.Errorf(
			"multijob: unknown special arguments before %q separator: ",
			separator,
			joinKeys(specialArgs, " "))
        return
	}

	jobID, err := strconv.Atoi(jobIDStr)
	if err != nil {
		err = fmt.Errorf("multijob: can't parse JobID %q: %s", jobIDStr, err.Error())
		return
	}

	repetitionID, err := strconv.Atoi(repetitionIDStr)
	if err != nil {
		err = fmt.Errorf("multijob: can't parse RepetitionID %q: %s", repetitionIDStr, err.Error())
	}

	args = &Args{jobID, repetitionID, normalArgs}
	return
}

type Args struct {
	JobID        int
	RepetitionID int
	args         map[string]string
}

// GetStr retrieves a string value from the command line arguments.
func (args *Args) GetStr(key string) (value string, err error) {
	value, ok := args.args[key]
	if !ok {
		err = fmt.Errorf("multijob: no %q argument", key)
	}
	return
}
