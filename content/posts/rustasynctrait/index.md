+++
date = '2025-03-04T12:59:14+08:00'
draft = false
title = 'Rust Async Trait Problem'
+++

I didn't know there was a problem
<!--more-->

# Context
1. `async`/`await` is a feature in Rust that allows you 
to write asynchronous code. 
2. `trait` is a feature in Rust that allows you to define 
shared behavior between types.
3. We start off with pre-1.65 Rust, where GATs were not possible.

# What we want
With that, naturally, we want to define an `async` function 
in a `trait`. No problem, let's do:
```rust
trait SomeTrait {
    async fn somefn(&self);
}
```
Rust desugars this to:
```rust
trait SomeTrait {
    fn somefn(&self) -> impl Future<Output = ()>;
}
```


Annnd... it doesn't compile. Rust says:
```bash
error[E0562]: `impl Trait` only allowed in function and inherent method return types, not in trait method return types
 --> src/main.rs:3:25
  |
3 |     fn somefn(&self) -> impl Future<Output = ()>;
  |                         ^^^^^^^^^^^^^^^^^^^^^^^^
  |
  = note: see issue #91611 <https://github.com/rust-lang/rust/issues/91611> for more information

For more information about this error, try `rustc --explain E0562`.
error: could not compile `test174` (bin "test174") due to previous error
```

The reason why it doesn't compile is because `impl Trait` is 
not supported in trait method return types. This is because 
Rust’s trait system historically required the trait’s 
signature to fully specify the return type for all implementors. 
This is a problem because `impl Trait` is a placeholder for 
a concrete type that is determined at compile time. We can see this 
using other traits as well:
```rust
trait SomeTrait {
    fn somefn(&self) -> impl Copy;
}
```
```bash
error[E0562]: `impl Trait` only allowed in function and inherent method return types, not in trait method return types
 --> src/main.rs:4:25
  |
4 |     fn somefn(&self) -> impl Copy;
  |                         ^^^^^^^^^
  |
  = note: see issue #91611 <https://github.com/rust-lang/rust/issues/91611> for more information
```


No problem, you think. We can just use associated types:
```rust
trait SomeTrait {
    type SomeType: Future<Output = ()>;
    fn somefn(&self) -> Self::SomeType;
}
```
And that does compile. But when you actually try to implement 
the trait:
```rust
struct Foo { }
impl SomeTrait for Foo {
    type SomeType = Future<Output = ()>;
    fn somefn(&self) -> Self::SomeType {
        ()
    }
}
```
And before you even compile it, your lsp(if present) will yell at you already. That's 
because you must provide a concrete type for associated types instead of a Future. 
That's ok, we can use the `dyn` keyword. But because futures are self-referential, 
you have to use `Pin<Box<dyn Future<Output = ()>>>` instead of `dyn Future<Output = ()>`. 

```rust
struct Foo { }
impl SomeTrait for Foo {
    type SomeType = Pin<Box<dyn Future<Output = ()>>>;
    fn somefn(&self) -> Self::SomeType {
        Box::pin(async { })
    }
}
```
Great! Now you basically desugared the `async` function in the trait to a 
`Pin<Box<dyn Future<Output = ()>>`. And that's exactly what `async_trait` crate does. 
yay! So what's the problem?

# The Problem
Consider the following case:
```rust
trait SomeTrait {
    type SomeType: Future<Output = u32>;
    fn somefn(&self) -> Self::SomeType;
}

struct Foo { 
    id: u32
}
impl SomeTrait for Foo {
    type SomeType = Pin<Box<dyn Future<Output = u32>>>;
    fn somefn(&self) -> Self::SomeType {
        Box::pin(async { self.id })
    }
}
```

This will not compile. Rust will say:
```bash
error: lifetime may not live long enough
  --> src/main.rs:14:9
   |
13 |     fn somefn(&self) -> Self::SomeType {
   |               - let's call the lifetime of this reference `'1`
14 |         Box::pin(async { self.id })
   |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^ returning this value requires that `'1` must outlive `'static`

error: could not compile `test174` (bin "test174") due to previous error
```
The reason is obvious. The `async` block captures `self` by reference. Compiler 
cannot guarantee that the reference will live long enough. So we need to add 
a lifetime to the trait:
```rust
trait SomeTrait {
    type SomeType<'a>: Future<Output = u32> + 'a
        where Self: 'a;
    fn somefn(&self) -> Self::SomeType<'_>;
}

struct Foo { 
    id: u32
}
impl SomeTrait for Foo {
    type SomeType<'a> = Pin<Box<dyn Future<Output = u32> + 'a>>;
    fn somefn(&self) -> Self::SomeType<'_> {
        Box::pin(async move {
            self.id
        })
    }
}
```
"generic associated types" is often referred to as GATs.


Compiler yells at you again:
```bash
error[E0658]: generic associated types are unstable
 --> src/main.rs:4:5
  |
4 | /     type SomeType<'a>: Future<Output = u32> + 'a
5 | |         where Self: 'a;
  | |_______________________^
  |
  = note: see issue #44265 <https://github.com/rust-lang/rust/issues/44265> for more information

error[E0658]: where clauses on associated types are unstable
 --> src/main.rs:4:5
  |
4 | /     type SomeType<'a>: Future<Output = u32> + 'a
5 | |         where Self: 'a;
  | |_______________________^
  |
  = note: see issue #44265 <https://github.com/rust-lang/rust/issues/44265> for more information

error[E0658]: generic associated types are unstable
  --> src/main.rs:13:5
   |
13 |     type SomeType<'a> = Pin<Box<dyn Future<Output = u32> + 'a>>;
   |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   |
   = note: see issue #44265 <https://github.com/rust-lang/rust/issues/44265> for more information

For more information about this error, try `rustc --explain E0658`.
error: could not compile `test174` due to 3 previous errors
```
The problem is that pre-1.65 Rust does not support generic associated types. 
But with 1.74 rust, it works. Awesome!

# What about 1.75?
With 1.75 comes the ability to have `impl trait` in trait method return types. 
The earlier example:
```rust
trait SomeTrait {
    fn somefn(&self) -> impl Copy;
}
```
compiles just fine. Which means, `impl Future` is also valid. Since compiler can do 
this, it makes sense to do this automatically everytime, instead of needing to 
have `impl Future` in the trait definition everytime. The way it works is: 
1. It desugars `async fn` in a trait to `fn` that returns `impl Future`.
2. Depending on the context, it creates a GAT automatically.

Yay! No more problems! ...right?

# Well, no
The problem is that doing so does not make the trait `dyn compatible`(or `object safe`). 
If you don't care about `dyn compatible`, then yes, you're good to go. 
But why do we care about `dyn compatible`? Because we want to be able to 
do some runtime polymorphism. A lot of times we need to be able to take a 
trait object, without knowing its implementation details, and use it. Like:
```rust
trait SomeTrait {
    fn somefn(&self);
}

struct A;
impl SomeTrait for A {
    fn somefn(&self) {
        println!("A");
    }
}

struct B;
impl SomeTrait for B {
    fn somefn(&self) {
        println!("BBBBBB");
    }
}
```

So to achieve this, we still need to do `Pin<Box<T>>`. Doing this everytime is 
definitely tedious and error-prone. That's where the [`async_trait`](https://docs.rs/async-trait/latest/async_trait/) 
crate comes in. You do:
```rust
#[async_trait]
trait Advertisement {
    async fn run(&self);
}
```
and it transforms your async trait to a dyn compatible trait. How? 
It basically does that `Pin<Box<T>>` automatically for you. 
This means, in the modern rust world, [`async_trait`](https://docs.rs/async-trait/latest/async_trait/) 
is still valuable.


# Other Resources
1. [why async fn in traits are hard](https://smallcultfollowing.com/babysteps/blog/2019/10/26/async-fn-in-traits-are-hard/)
2. [Rust blog](https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits.html)
3. [Pin](https://doc.rust-lang.org/std/pin/)
