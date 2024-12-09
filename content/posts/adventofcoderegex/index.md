+++
date = '2024-12-08T20:13:22+08:00'
draft = false
title = 'I did Advent of Code using neovim'
+++

It's only one day but...
<!--more-->

# Context:
Advent of Code 2024, day 3.

First part:
Given a string, find all substring that has the format of `mul(x,y)` where `x` and `y` are integers. 
What's the sum of all `x*y`?

Second part:
Given the same string, there are do's and don'ts scattered around. 
You need to find the sum of all `x*y` that are not in the "clause" of `do()`s and `don't()`s.

# Part 1:
Now immediately I thought of regex. I could just code regex in rust, 
but what's the fun? I can just use Neovim!

The first part is very simple. I just need to find all the matches of `mul(x,y)` and capture 
`x` and `y` and sum them up.

First, I have to extract all the `x` and `y` from the string. 
I selected all the lines, and typed:
```
:'<,'>s/\v.{-}mul\((\d*),(\d*)\).{-}/\1 \2\r/g
```
`\v` is for `very magic mode`, which makes regex a bit simpler(not a lot). 
`.{-}` is for non-greedy match. Basically, it matches as few characters as possible, this 
prevents it from "eating up" the next `mul`. 
`\d*` is for matching digits. 
`\1` and `\2` are for capturing groups. 
`\r` is for better visualization. You're probably fine withouth it.

Now this gives me something like this:
```
594 203
693 99
225 584
...
494 553
563 373
675 891
73 441
182 313
(]what()
```
Now you've probably noticed that there's a `what()` at the end. That's because since 
I used non-greedy match, characters after `mul` are not consumed. No problem, I can just delete 
that line easily with `dd`.

The problem is how to multiply them. I decided to multiply the two numbers at each line first.
We can do this easily with recoreded commands:
```
qt_viw"ayw"by:let @c = string(str2nr(@a) * str2nr(@b))<CR>V@cpjq"
```
This is probably a bit much. Let's break it down:
- `qt` starts recording a macro in register `t`
- `_` moves the cursor to the first character
- `viw"ay` selects the inner word and yanks it to register `a`
- `w"by` moves to the next word and yanks it to register `b`
- `:let @c = string(str2nr(@a) * str2nr(@b))<CR>` multiplies the two numbers and stores it in register `c`
- `V@cp` pastes the result in the line
- `jq` moves to the next line and stops recording
Still with me? Now I can just type `@t` to multiply the next line. As the file has a total of 728 
lines, I just needed to type `727@t` to multiply all the lines. 
This got me:
```
120582
68607
131400
...
273182
209999
601425
32193
56966
```

Now that I have all the results, I just need to sum them up. 
I can do this with:
```
ggqtviw"ayddviw"bydd:let @c = string(str2nr(@a) + str2nr(@b))<CR>"@cPa<Enter>jq"
```
This is similar to the previous command, so I won't elaborate.
After recording, I still had 727 lines, so I just typed `727@t` to sum them all up.
The result is `183669043`. I typed into the input box and got the first star!

# Part 2:
Now the second part is a bit more complicated. There's some sort of 'state' managed by 
`do()` and `don't()`, and at the beginning of the string, the state is `true`. We only consider 
`mul(x,y)` when the state is `true`. Here's an example: 
```
xmul(2,4)&mul[3,7]!^don't()_mul(5,5)+mul(32,64](mul(11,8)undo()?mul(8,5))
```

First, I concatenated all the lines, since the state can carry over to the next line:
```
:%s/\n//g
```
Now, now that I look back, the answer was correct because I was lucky. I shouldn't have done that, 
instead I should have used `:%s/\n/@/g` to replace the newline with `@`, so new `do()` and `don't()` 
won't form.


My immediate thought is to match the `do()`s and `don't()`s. But at the start the state is `true`. 
Easy fix, I just manually appended a `do()` at the start of the string. 
Now let's find all the `mul(x,y)` that are inside the `do()` and `don't()`. Let's start by 
replacing all the `don't()` with `\r`. The idea is that all occurrences of `mul(x,y)` that are 
after `don't()` and have not encountered a `do()` are not considered. It'll make sense later.
```
:%s/don't()/\r/g
```
Now the string still don't make sense. That's ok. Now the problem is: In each line, 
until you meet a `do()`, all `mul(x,y)` are not considered. So let's expose all the 
lines that have `do()`, and move the `do()` to the beginning of the line, also append newline 
for clearity.
```
:%s/\v.{-}(do\(\).*)/\1\r/g
```
Now the string is starting to make sense:
```
...
do()[from() ,what()~mul(97,535);~mul(526,845)...

do()'&-> why()mul(755,634)select()?[who()!whe...

>why()}(+)how()where()when()mul#where()mul(31...
when()who();; where()^what()how()~mul(668,57)...
from(), how()<]^who();mul(629,290)what()mul(2...
do()select()~~from()>}mul(372,283)>%why()/<mu...
...
```
Notice now some line has `do()` at the beginning. These are the lines we care about. 
Now let's get rid of the line that doesn't have `do()` at the beginning. 

To do this we'll need the `:g` command. This basically runs a command on all lines that match a 
pattern. `:g!` is the opposite, it runs a command on all lines that don't match a pattern. 
Actually, `:g!` is the one we need. 
```
:%g!/do()/s/.//g
```
Let's break it down:
- `%` is the range, it means all lines
- `g!` is the command that runs on all lines that don't match the pattern
- `do()` is the pattern we're looking for. If the line doesn't have `do()`, the command following will run
- `s/.//g` is the command that removes all characters in the line.
Now I have some lines that are blank, and some lines that have `do()` at the beginning.
You can probably change the command a bit to make it look nicer:
```
...

do()select()~~from()>}mul(372,283)>%why(...


do():~ ~;*:{*mul*select()from(984,969)mu...

do()from()+when()mul(753,641)~{ +mul(817...


do()>]&'* *,mul(531,698+)#where()who()(f...
...
```

Next I extracted all `mul(x, y)`, since they are all considered valid now:
```
:%s/\v.{-}mul\((\d*),(\d*)\).{-}/\1 \2\r/g
```
The result was:
```
...
478 963
;}<select(){$*[who()/

285 888
447 749
@[?~how()<#$where()how(895,368)

600 918
680 387
...
```

Similar to the first part, there are some garbage lines. This time there are multiple lines, 
so we have to use command: 
(Also, I got lucky because none of the garbage lines had digits at the start)
```
:%s/\v^\D.*$\n//
```
And now to get rid of the empty lines, I used:
```
:%s/\v^\n//
```

That left me with:
```
594 203
693 99
225 584
...
713 682
183 921
357 475
328 637
920 871
```
The rest is the same as the first part. I multiplied them all and summed them up. 
My result was: `59097164`.
