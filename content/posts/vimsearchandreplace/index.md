+++
date = '2024-12-06T16:47:07+08:00'
draft = false
title = 'Neovim Search/Replace'
+++

Blazingly fast!!!!
<!--more-->

# Search/Replace in Nvim
In neovim, use `:s` command to search/replace. The syntax of `:s` command is as follows:
```
:[range]s[ubstitute]/{pattern}/{string}/[flags] [count]
```
You can also do `:h :s` to read the documentation for `:s`.

`[range]` means the range of lines you want to search/replace.

`[flags]` can be `g` for global, `c` for confirm, `i` for ignore case, etc. There are many flags, but I won't cover them all here.

`[count]` means starting from some line(within `[range]`), how many lines you want to replace.

## `[range]`
`[range]` can be a line number:
```
12
```
a range:
```
12,15
```
the whole file:
```
%
```
Note that `'<` and `'>` represent the visual mode selected area, and `.` represents the current line.
When `[range]` is not specified, it defaults to the current line.

# Example
## Example 1: Replace `foo` with `bar` in the current line
```
:s/foo/bar/
```

## Example 2: Replace `foo` with `bar` in line 3
```
:3s/foo/bar/
```

## Example 3: Replace `foo` with `bar` in the whole line
```
:s/foo/bar/g
```

## Example 4: Replace `foo` with `bar` through out the whole file
```
:%s/foo/bar/g
```
Note that `%` means the whole file, and `g` means replace all `foo` on the line.

## Example 5: Replace `foo` with `bar` in a selected range
First go in `visual` mode, select some texts, then press `:`, at which point the command line will show `:'<,'>`. Then type the replace command normally, 
without the need to manually type out the selected range:
```
:'<,'>s/foo/bar/g
```

# Capture Group
`{pattern}` and `{string}` actually uses regex, so capture groups are also supported.

The syntax for capture group is `\(\)`. If you include `\v`(`very magic mode`), the syntax simplify to `()`.

To use the contents of captured groups, use `\i` where `i` is an integer starting from 1.

Consider the following example:
```go
func main() {
    let Field1 = "foo"
    let Field2 = "bar"
    let Field3 = 3
    let Field4 = 3.14
}
```
Oh no, I accidentally messed up golang's syntax. The correct syntax should be:
```go
Fieldx := someval
```
Select the text in visual mode and use following command:
(small tip: when cursor is above any of `()` `{}` `[]`, use `%` to jump to matching character)
When using `very magic mode`:
```
:'<,'>s/\vlet (\w+) \= (.+)/\1 := \2
```
When not using `very magic mode`:
```
:'<,'>s/let \(\w\+\) = \(.\+\)/\1 := \2
```
Please note that in `very magic mode`, `=` need escaping to match.
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/vimsearchandreplace/video1.mov" caption="Capture Group" >}}
{{< /gallery >}}

## Real-world example 1: filtering dictionary
Suppose i have a dictionary(not necessarily `json`) with similar structure, and I wish to skim through all key-value pairs where the value is a number.
```
    "key1": "val1",
    "key2": 2,
    "key3": 3.14,
    "key6": {
        "key7": 7
        "key8": "val8"
    },
    "key4": "val4",
    "key5": 5
}
```
Select the dictionary, and use following command:
```
:'<,'>s/\v\s+"\w+": "\w+",*\n/
```
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/vimsearchandreplace/video2.mov" caption="example 1" >}}
{{< /gallery >}}

## Real-world example 2: refactoring code
Consider the following code:
```swift
let increment1 = 1
let increment2 = 23
let increment3 = 4
let increment4 = 5
let increment5 = 289
```
You wish to turn these numeric constants into lambda expressions, i.e.:
```swift
let incrementx = { y in y + z }
```
Select the code, and use the following command:
```
:'<,'>s/\vlet (\w+) \= (.+)/let \1 = { x in x + \2 }
```
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/vimsearchandreplace/video3.mov" caption="example 2" >}}
{{< /gallery >}}
Of course, more simpler instructions exist, such as directly replacing the constant after the equal sign. But capturing the variable names in front provides other benefits:
Control their capitalization, or even add a prefix/suffix to them.
```
:'<,'>s/\vlet (\w+) \= (.+)/let \U\1\E = { x in x + \2 }
```
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/vimsearchandreplace/video4.mov" caption="example 3" >}}
{{< /gallery >}}

