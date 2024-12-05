---
title: "Go Iterators"
date: 2024-06-21T23:00:51+08:00
draft: false
---

# Context:
So in Go 1.23, iterators are coming, apparently. So I went and tried to find out what they are and how they work.
I found this issue: [spec: add range over int, range over func #61405](https://github.com/golang/go/issues/61405)
I strongly encourage you to read it yourself. But, basically, what [rsc](https://github.com/rsc) is trying to propose is that, for loops should be able to iterate over numbers and functions, apart from the usual slices, arrays, maps, and channels.
The numbers part is pretty straightforward, it's the function part that I want to focus on.

# Go Iterators
So to make it possible to iterate over functions, [rsc](https://github.com/rsc) added three rows to the spec table:
```
Range expression                                   1st value          2nd value

array or slice      a  [n]E, *[n]E, or []E         index    i  int    a[i]       E
string              s  string type                 index    i  int    see below  rune
map                 m  map[K]V                     key      k  K      m[k]       V
channel             c  chan E, <-chan E            element  e  E
integer             n  integer type                index    i int

function, 0 values  f  func(func()bool) bool
function, 1 value   f  func(func(V)bool) bool      value    v  V
function, 2 values  f  func(func(K, V)bool) bool   key      k  K      v          V
```

And stated that:
> If f is a function type of the form func(yield func(T1, T2)bool) bool, then for x, y := range f { ... } is similar to f(func(x T1, y T2) bool { ... }), where the loop body has been moved into the function literal, which is passed to f as yield. The boolean result from yield indicates to f whether to keep iterating. The boolean result from f itself is ignored in this usage but present to allow easier composition of iterators.

So,
```go
for x, y := range f {
    // ...
}
```
is effectively the same as:
```go
f(func(x T1, y T2) bool {
    // ...
})
```

# How do they work?
Lets look at the example from the [GoWiki](https://go.dev/wiki/RangefuncExperiment):
Consider this function for iterating a slice backwards:
```go
package slices

func Backward[E any](s []E) func(func(int, E) bool) {
    return func(yield func(int, E) bool) {
        for i := len(s)-1; i >= 0; i-- {
            if !yield(i, s[i]) {
                return
            }
        }
    }
}
```
Immediately you'll notice something: Backward()'s return value does not have a return value. Now this confused me a bit as well, but it seems like in the official implementation, iterators do not need a return value, so it differs from rsc's original proposal.
This can be invoked as:
```go
s := []string{"hello", "world"}
for i, x := range slices.Backward(s) {
    fmt.Println(i, x)
}
```
This program would translate inside the compiler to a program more like:
```go
slices.Backward(s)(func(i int, x string) bool {
    fmt.Println(i, x)
    return true
})
```

In this example, `Backward` is a function that returns a Go iterator. We can use it to easily iterate over a slice backwards. Now, there are couple of things to notice:
1. The iterator is responsible for calling the body.
2. The body needs either: `k, v` or `v` or nothing.
3. The iterator calls yield with every: `k, v` or `v` or nothing.
4. `return true` keeps the loop going, while `return false` effectively breaks the loop.

Generalize and you get the definition:
Go iterators are functions that take a function as an argument. Specifically, the arguments are functions of the form `func(T1, T2) bool`, `func(T) bool`, or `func() bool`.

# Hard to understand?
I know, it's a bit much. I'm kind of confused as well. But we can see this more intuitively. What the `for k, v := range f { ... }` is doing, is basically as such:
> Iterate using `f` as an iterator, and for every iteration, call `{ ... }` with the values `k, v`.

Some may say that this is like .forEach in some other languages for passing a callback function. I suppose that's a nice way to look at it..?
You can also read this quote from the [spec: add range over int, range over func #61405](https://github.com/golang/go/issues/61405) issue page:
> For a function f, the iteration proceeds by calling f with a synthesized yield function that invokes the body of the loop. The values produced correspond to the arguments in successive calls to yield. As with range over other types, it is permitted to declare fewer iteration variables than there are iteration values. The return value from the yield function reports whether f should continue iterating. For example, if the loop body executes a break statement, the corresponding call to yield returns false. The return value from f is ignored by range but conventionally returns false when yield has returned false, to allow composing a sequence of such functions. The use of a synthesized yield function does not change the semantics of the loop body. In particular, break, continue, defer, goto, and return statements all behave in a loop body ranging over a function exactly as they do in a loop body ranging over other types.

To its core, iterators have the form like so:
```
func iterator(...) func(func(...) bool) {
    return func(yield func(...) bool) {
        // iterate somehow, calling yield on every iteration
    }
}
```
And when it pass back the function, the function will be immediately called with the body.

## Other reading sources:
- [Why People are Angry over Go 1.23 Iterators](https://www.gingerbill.org/article/2024/06/17/go-iterator-design/)
- [Iterators in Go](https://bitfieldconsulting.com/posts/iterators)
- [A look at iterators in Go](https://medium.com/eureka-engineering/a-look-at-iterators-in-go-f8e86062937c)

## Note:
This feature, as of the time of writing, is under heavy criticism, and I strongly encourage you do some research on this to learn the full story.
