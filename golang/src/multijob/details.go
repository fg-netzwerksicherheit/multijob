package multijob

import "fmt"
import "strings"
import "strconv"
import "sort"

func separateArgvIntoSpecialAndNormalKVs(argv []string, sep string) (
	special, normal map[string]string, err error) {

	special = make(map[string]string)
	normal = make(map[string]string)

	i := 0

	for ; i < len(argv); i++ {
		if argv[i] == sep {
			break
		}

		key, value, err := splitArg(argv[i])
		if err != nil {
			return nil, nil, err
		}

		special[key] = value
	}

	i++

	for ; i < len(argv); i++ {
		key, value, err := splitArg(argv[i])
		if err != nil {
			return nil, nil, err
		}

		normal[key] = value
	}

	return
}

// splitArgs splits a "key=value" argument into its respective parts.
func splitArg(arg string) (key string, value string, err error) {
	components := strings.SplitN(arg, "=", 2)
	if len(components) != 2 {
		return "", "", fmt.Errorf("multijob: can't split %q as argument", arg)
	}

	key = components[0]
	value = components[1]

	return
}

func joinSortedQuotedItems(items []string, sep string) string {
	strs := make([]string, len(items))
	copy(strs, items)

	sort.Strings(strs)

	// quote the keys
	for i, k := range strs {
		strs[i] = strconv.QuoteToASCII(k)
	}

	return strings.Join(strs, sep)
}

// joinKeys joins the sorted keys of a map.
func joinKeys(m map[string]string, sep string) string {
	keys := make([]string, len(m))

	// extract the keys
	i := 0
	for k, _ := range m {
		keys[i] = k
		i++
	}

	return joinSortedQuotedItems(keys, sep)
}
