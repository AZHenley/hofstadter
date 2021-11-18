# The Hofstadter Esoteric Programming Language

> Hofstadter's Law: It always takes longer than you expect, even when you take into account Hofstadter's Law.

The Hofstadter esoteric programming language executes every line concurrently, in round-robin style. There are only 8 commands and each line can only store a single string value. There is [discussion](https://github.com/AZHenley/hofstadter/pull/8) that the language is not Turing complete.

The commands are as follows:

Action | Example code | Description
------ | ------- | -----------
HTTP request | http://www.austinhenley.com | If the line's data is empty, performs a HTTP GET at the specified URL and stores the result in data. If the line's data is not empty, performs a HTTP POST at the specified URL with the line's data as the request's body and stores the response in data.
Regex | "a(bc)*" | Runs the specified regex on the line's data and stores the first match back in the line's data.
File IO | foo.txt | If the line's data is empty, reads the specified file's contents to the line's data. If the line's data is not empty, writes the line's data to the specified file. Can be a relative or absolute path.
Console IO | # |  If the line's data is empty, reads from stdin into the line's data. If data is not empty, write tp stdout.
Conditional | ?5 | If the line's data is equal to the specified line's data, continue. Else, restart the execution of this line from the start but keep the data.
Conditional | !5 | If the line's data is not equal to the specified line's data, continue. Else, restart the execution of this line from the start but keep the data.
Swap data | @5 | Swaps the line's data with the specified line's data.
Concatenate | +5 | Concatenates the line's data with the specified line's data and stores it in the line's data.


Lines are 1-indexed. You can swap with lines that do not exist as extra storage (but they must be positive numbers). Line 0 always contains the empty string, no matter what you swap to it (`@0` is effectively a clear). Swapping with the current line is effectively a no-op. When lines restart, they retain their value. Commands are expected to be space separated.

### Example: Counting to 99.

Todo.

### Example: Two digit adder.

Todo.






