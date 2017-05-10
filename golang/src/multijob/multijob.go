// Parse the Multijob command line interface.
// This allows you to implement Multijob tasks in Go.
//
//      args, err := multijob.ParseCommandLine(args, nil)
//      if err != nil {
//          ...
//      }
//
//      x, err := args.GetStr("x")
//      if err != nil {
//          ...
//      }
//
//      if err = args.NoFurtherArguments(); err != nil {
//          ...
//      }
package multijob

import "fmt"
import "strconv"

// JobArgvConfig lets you change the names of the special "--id" and "--rep"
// parameters.
type JobArgvConfig struct {
	JobIDKey        string // JobIDKey is the name of the "--id" argument.
	RepetitionIDKey string // RepetitionIDKey is the name of the "--rep" argument.
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

	jobIDStr, ok := specialArgs[config.JobIDKey]
	if !ok {
		err = fmt.Errorf("multijob: special JobID argument %q required",
			config.JobIDKey)
		return
	}

	repetitionIDStr, ok := specialArgs[config.RepetitionIDKey]
	if !ok {
		err = fmt.Errorf("multijob: special RepetitionID argument %q required",
			config.RepetitionIDKey)
		return
	}

	delete(specialArgs, config.JobIDKey)
	delete(specialArgs, config.RepetitionIDKey)

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

	args = &Args{
		JobID:        jobID,
		RepetitionID: repetitionID,
		args:         normalArgs,
		argWasUsed:   make(map[string]bool),
	}
	return
}

// Args represents the parsed arguments.
// You may retrieve arguments via the "Get*" methods, e.g. "GetStr()".
type Args struct {
	JobID        int
	RepetitionID int
	args         map[string]string
	argWasUsed   map[string]bool
}

func (args *Args) NoFurtherArguments() (err error) {
	unusedArgs := make([]string, 0, len(args.args))
	for k, _ := range args.args {
		if _, ok := args.argWasUsed[k]; !ok {
			unusedArgs = append(unusedArgs, k)
		}
	}

	if len(unusedArgs) > 0 {
		err = fmt.Errorf(
			"multijob: Unused arguments remain: %s",
			joinSortedQuotedItems(unusedArgs, ", "))
	}

	return
}

// GetStr retrieves a string value from the command line arguments.
func (args *Args) GetStr(key string) (value string, err error) {
	value, ok := args.args[key]
	if !ok {
		err = fmt.Errorf("multijob: no %q argument", key)
	}
	args.argWasUsed[key] = true
	return
}
