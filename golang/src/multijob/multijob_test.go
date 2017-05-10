package multijob

import "testing"

func TestDecodesIDs(t *testing.T) {
	argv := []string{"--id=43", "--rep=7", "--", "a=b"}
	args, err := ParseCommandline(argv, nil)

	if err != nil {
		t.Errorf("Unexpected error: %s", err.Error())
		return
	}

	if args == nil {
		t.Errorf("Parsing was successful, but args == nil")
		return
	}

	expectedJobID := 43
	expectedRepetitionID := 7

	if args.JobID != expectedJobID {
		t.Errorf("JobID: expected %d, got: %d", expectedJobID, args.JobID)
	}

	if args.RepetitionID != expectedRepetitionID {
		t.Errorf("RepetitionID: expected %d, %d",
			expectedRepetitionID,
			args.RepetitionID)
	}

	b, err := args.GetStr("a")
	if err != nil {
		t.Errorf("GetStr(\"a\"): unexpected error: %s", err.Error())
	}
	if b != "b" {
		t.Errorf("GetStr(\"a\"): expected \"b\" but got %q", b)
	}

	_, err = args.GetStr("nonexistent")
	if err == nil {
		t.Errorf("GetStr(\"nonexistent\"): no error was returned")
	}
}

func TestDecodesIDsErrors(t *testing.T) {
	type failureCase struct {
		descr string
		argv  []string
	}

	cases := []failureCase{
		{"missing --rep",
			[]string{"--id=0", "--"}},
		{"missing --id",
			[]string{"--rep=0", "--"}},
		{"unknown special arg",
			[]string{"--id=0", "--rep=0", "--this doesn't exist=0", "--"}},
		{"Id is not numeric",
			[]string{"--id=x", "--rep=0", "--"}},
		{"Rep is not numeric",
			[]string{"--id=0", "--rep=x", "--"}},
		{"special arg has no value",
			[]string{"--id", "--rep=0", "--"}},
		{"arg has no value",
			[]string{"--id=0", "--rep=0", "--", "x"}},
	}

	for _, c := range cases {
		_, err := ParseCommandline(c.argv, nil)
		if err == nil {
			t.Errorf("Expected error for case %s", c.descr)
		}
	}
}

func TestPrivateSplitArg(t *testing.T) {
	cases := []struct {
		arg, key, value string
		fail            bool
	}{
		{"--", "", "", true},
		{"a=b", "a", "b", false},
		{"a=b=c", "a", "b=c", false},
	}

	for _, c := range cases {
		key, value, err := splitArg(c.arg)

		if c.fail && err == nil {
			t.Errorf("Expected failure but got key=%q value=%q", key, value)
			continue
		}

		if !c.fail && err != nil {
			t.Errorf("Unexpected failure: %s", err.Error())
			continue
		}

		if key != c.key {
			t.Errorf("Key: expected %q but got %q", c.key, key)
		}

		if value != c.value {
			t.Errorf("Value: expected %q but got %q", c.value, value)
		}
	}
}

func TestNoFurtherArguments(t *testing.T) {
	args, err := ParseCommandline(
		[]string{"--id=4", "--rep=7", "--", "x=a", "y=2"},
		nil)

	if err != nil {
		t.Errorf("command line was not parsed successfully")
		return
	}

	err = args.NoFurtherArguments()

	if err == nil {
		t.Errorf("expected error before args were consumed")
	}

	if err.Error() != "multijob: Unused arguments remain: \"x\", \"y\"" {
		t.Errorf("wrong error message: %q", err.Error())
	}

	_, err = args.GetStr("x")
	if err != nil {
		t.Errorf("GetStr(x) failed: %s", err.Error())
	}

	_, err = args.GetStr("y")
	if err != nil {
		t.Errorf("GetStr(y) failed: %s", err.Error())
	}

	err = args.NoFurtherArguments()

	if err != nil {
		t.Errorf("unexpected error after args were consumed: %q", err.Error())
	}
}
