+++
date = '2026-02-13T19:43:01+08:00'
draft = false
title = 'Custom Validators in Go'
tags = ['go', 'validator']
+++

Have you ever wondered what `Echo`'s `c.Validate` does under the hood? Let's write our own.
<!--more-->

# Preface
So you know when using `Echo` framework, you can call `c.Validate` to validate 
the bound struct? Here's an example:

1. First we declare a custom validator:
```go
import (
	validator "github.com/go-playground/validator/v10"
)

type CustomValidator struct {
	validator *validator.Validate
}

func (cv *CustomValidator) Validate(i any) error {
	return cv.validator.Struct(i)
}
```

2. Then we wire it up for `Echo`:
```go
e := echo.New()
e.Validator = &CustomValidator{validator: validator.New()}
```

```go
func SomeEchoHandler(c echo.Context) error {
    type Params struct {
        Name string `json:"name" validate:"required"`
        Age  int    `json:"age" validate:"gte=0,lte=130"`
    }
    var p Params
	if err := c.Bind(&p); err != nil {
		log.Errorf("error binding filter params: %v", err)
		return c.JSON(400, map[string]string{"error": "malformed filter parameters"})
	}
	if err := c.Validate(p); err != nil {
		log.Errorf("validation error: %v", err)
		return c.JSON(400, map[string]string{"error": "invalid filter parameters"})
	}
```
This is a very common pattern in backend codebases that use `Echo`. But what does 
`c.Validate` do? How does it work? Can we write our own custom validator? Let's find out.

# Digging into go-playground/validator
The above example is actually a pretty stupid way of writing a custom validator, 
because all it does is relay the call to the validator from `go-playground/validator`. 
So let's look into that. Using `go to definition` from our wonderful lsp, and after a few hops we find:
```go
// traverseField validates any field, be it a struct or single field, ensures it's validity and passes it along to be validated via it's tag options
func (v *validate) traverseField(ctx context.Context, parent reflect.Value, current reflect.Value, ns []byte, structNs []byte, cf *cField, ct *cTag) {
	var typ reflect.Type
	var kind reflect.Kind

	current, kind, v.fldIsPointer = v.extractTypeInternal(current, false)

	var isNestedStruct bool

	switch kind {
	case reflect.Ptr, reflect.Interface, reflect.Invalid:

		if ct == nil {
			return
		}

		if ct.typeof == typeOmitEmpty || ct.typeof == typeIsDefault {
			return
		}

		if ct.typeof == typeOmitNil && (kind != reflect.Invalid && current.IsNil()) {
			return
		}

		if ct.typeof == typeOmitZero {
			return
		}
//...
}
```

Yep. It's a giant switch statement with reflection. You can read the full code if you want, 
but the gist of it is that it uses reflection to inspect the struct fields,
and then applies the validation rules specified in the `validate` tags. Sounds simple enough, let's 
try writing our own.

# Writing Our Own Custom Validator
To have a basic understanding of how to do reflection in Go, I recommend starting with
[this article](https://go.dev/blog/laws-of-reflection).

## Playing With Reflection
Let's do some basic reflection to make sure we know what we're doing:
```go
package main

import (
	"fmt"
	"reflect"
)

func main() {
	var v float32 = 7.4
	fmt.Println(v)
	fmt.Println(reflect.TypeOf(v))
	reflect.ValueOf(&v).Elem().SetFloat(8.1)
	fmt.Println(v)

	reflect.ValueOf(v).SetFloat(9.6)
}
```
This prints:
```
7.4
float32
8.1
panic: reflect: reflect.Value.SetFloat using unaddressable value

goroutine 1 [running]:
reflect.flag.mustBeAssignableSlow(0x4?)
...
exit status 2
```
Perfect. At the beginning, `v` is `7.4`. Using reflection we can get its type `float32`,
and we can set its value to `8.1`. And as expected, `reflect.ValueOf(v).SetFloat(9.6)` panics because
when we call `reflect.ValueOf(v)`, we get a copy of `v`. When we try to set the value, logically 
it would set the copy's value, but that's not desired behavior, so go just panics. We pass a pointer, 
and use `Elem()` to dereference it, and now we can set the value.

## Printing Struct Field Tags
Now let's try inspecting a struct's field tags:
```go
package main

import (
	"fmt"
	"reflect"
)

type User struct {
	Age int32 `guard:"okok"`
	Paycheck int32 `guard:"min=1000"`
	notexported int32 `guard:"min=10009"`
	NoTag int32
}

func main() {
	var u User = User{Age: 20}
	typ := reflect.TypeOf(u)
	for i := range typ.NumField() {
		field := typ.Field(i)
		fmt.Printf(
			"Field %d: %s, with tag: %s, exported: %v\n", 
			i,
			field.Name,
			field.Tag.Get("guard"),
			field.IsExported(),
		)
	}
}
```

This program prints:
```
Field 0: Age, with tag: okok, exported: true
Field 1: Paycheck, with tag: min=1000, exported: true
Field 2: notexported, with tag: min=10009, exported: false
Field 3: NoTag, with tag: , exported: true
```
We can gain several insights from this:
1. We can use `reflect.TypeOf` to get the type of a struct, tag information is stored 
in the type(otherwise we would have to store this metadata alongside every value)
2. If there's no tag, `Tag.Get` returns an empty string.
3. We can check whether a field is exported using `IsExported()`.


Why is this important? What difference does it make whether a field is exported or not?
Well, let's try setting the value of an unexported field specifically:
```go
package main

import (
	"fmt"
	"reflect"
)

type User struct {
	Age int32 `guard:"okok"`
	Paycheck int32 `guard:"min=1000"`
	notexported int32 `guard:"min=10009"`
	NoTag int32
}

func main() {
	var u User = User{Age: 20}
	typ := reflect.TypeOf(u)

	vu := reflect.ValueOf(&u).Elem()
	for i := range typ.NumField() {
		field := typ.Field(i)
		fmt.Printf(
			"Field %d: %s, with tag: %s, exported: %v\n", 
			i,
			field.Name,
			field.Tag.Get("guard"),
			field.IsExported(),
		)

		if !field.IsExported() {
			vu.Field(i).SetInt(100)
		}
	}
}
```
Notice how we need both `reflect.Value` and `reflect.Type` to inspect and modify the struct.
This program prints:

```
Field 0: Age, with tag: okok, exported: true
Field 1: Paycheck, with tag: min=1000, exported: true
Field 2: notexported, with tag: min=10009, exported: false
panic: reflect: reflect.Value.SetInt using value obtained using unexported field

goroutine 1 [running]:
reflect.flag.mustBeAssignableSlow(0x14000104d88?)
...
exit status 2
```
Oh! We get a panic when trying to set the value of an unexported field. Reflection does not allow 
modifying unexported fields. This is important to note when writing our validator(you don't want it to panic, right?).

## Parsing Tags
The `Tag.Get` call returns the entire tag string identified by the key. In our case, I just chose a 
random key `guard`, and let's use comma for separation. We need to parse the tag string into 
various constraints. 
For simplicity, let's only support three constraints:
1. `required`: field must be a pointer, slice, map, or a channel, otherwise it's no-op. The value must not be nil.
2. `min=X`: field must be an integer/unsigned integer type, and its value must be >= X.
3. `max=X`: field must be an integer/unsigned integer type, and its value must be <= X.
Parser, for every tag string, must tell us:
1. Is this `required`?
2. Is there a `min` constraint? If so, what's the value?
3. Is there a `max` constraint? If so, what's the value?

Let's write a simple parser for this:
```go
type Guard struct {
	Required bool
	HaveMin bool
	Min int
	HaveMax bool
	Max int
}

func parseGuard(tag string) (Guard, error) {
	cons := strings.Split(tag, ",")
	if len(cons) > 3 {
		return Guard{}, fmt.Errorf("too many constraints: %d", len(cons))
	}

	var g Guard = Guard{
		Required: false,
		HaveMin: false,
		Min: 0,
		HaveMax: false,
		Max: 0,
	}
	for _, con := range cons {
		if con == "" {
			continue
		}
		if len(con) > 4 && con[:4] == "min=" {
			g.HaveMin = true
			num, err := fmt.Sscanf(con[4:], "%d", &g.Min)
			if err != nil || num != 1 {
				return Guard{}, fmt.Errorf("invalid min value: %s", con[4:])
			}
		} else if len(con) > 4 && con[:4] == "max=" {
			g.HaveMax = true
			num, err := fmt.Sscanf(con[4:], "%d", &g.Max)
			if err != nil || num != 1 {
				return Guard{}, fmt.Errorf("invalid max value: %s", con[4:])
			}
		} else if con == "required" {
			g.Required = true
		} else {
			return Guard{}, fmt.Errorf("unknown constraint: %s", con)
		}
	}
	return g, nil
}
```
Now let's test it out, I intentionally put some invalid tags to make sure the error handling works:
```go
package main

import (
	"fmt"
	"reflect"
	"strings"
)

type User struct {
	Age int32 `guard:""`
	Paycheck int32 `guard:"min=1000,ok=1000"`
	notexported int32 `guard:"what,min=10009"`
	NoTag int32
}

func main() {
	var u User = User{Age: 20}
	typ := reflect.TypeOf(u)

	for i := range typ.NumField() {
		field := typ.Field(i)
		fmt.Printf(
			"Field %d: %s, with tag: %s, exported: %v\n", 
			i,
			field.Name,
			field.Tag.Get("guard"),
			field.IsExported(),
		)
		g, err := parseGuard(field.Tag.Get("guard"))
		if err != nil {
			fmt.Printf("Error parsing guard: %v\n", err)
			continue
		}
		fmt.Printf("Parsed guard: %v\n", g)
	}
}
```
Output:
```
Field 0: Age, with tag: , exported: true
Parsed guard: {false false 0 false 0}
Field 1: Paycheck, with tag: min=1000,ok=1000, exported: true
Error parsing guard: unknown constraint: ok=1000
Field 2: notexported, with tag: what,min=10009, exported: false
Error parsing guard: unknown constraint: what
Field 3: NoTag, with tag: , exported: true
Parsed guard: {false false 0 false 0}
```
Yay! It's working. Now let's move on to validation logic.

## Validation Logic
```go
type MyValidator struct {}
func (v MyValidator) Validate(s any) error {
	val := reflect.ValueOf(s)
	typ := reflect.TypeOf(s)
	if typ.Kind() != reflect.Struct {
		return fmt.Errorf("expected struct, got %s", typ.Kind())
	}

	for i := range typ.NumField() {
		fv := val.Field(i)
		field := typ.Field(i)
		ft := field.Type
		tag := field.Tag.Get("guard")
        // skip unexported fields
        if !field.IsExported() {
            continue
        }
		g, err := parseGuard(tag)
		if err != nil {
			return fmt.Errorf("error parsing guard for field %s: %v", field.Name, err)
		}
		if g.Required {
			if ft.Kind() == reflect.Pointer || ft.Kind() == reflect.Slice ||
				ft.Kind() == reflect.Map || ft.Kind() == reflect.Chan {
				if fv.IsNil() {
					return fmt.Errorf("field %s is required but is nil", field.Name)
				}
			}
			// otherwise no-op
		}
		if g.HaveMin {
			switch ft.Kind() {
			case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
				if fv.Int() < int64(g.Min) {
					return fmt.Errorf("field %s is less than min %d", field.Name, g.Min)
				}
			case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
				if fv.Uint() < uint64(g.Min) {
					return fmt.Errorf("field %s is less than min %d", field.Name, g.Min)
				}
			default:
				return fmt.Errorf("min constraint not supported for field %s of type %s", field.Name, ft.Kind())
			}
		}
		if g.HaveMax {
			switch ft.Kind() {
			case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
				if fv.Int() > int64(g.Max) {
					return fmt.Errorf("field %s is greater than max %d", field.Name, g.Max)
				}
			case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
				if fv.Uint() > uint64(g.Max) {
					return fmt.Errorf("field %s is greater than max %d", field.Name, g.Max)
				}
			default:
				return fmt.Errorf("max constraint not supported for field %s of type %s", field.Name, ft.Kind())
			}
		}
	}
	return nil
}
```

## Testing Our Validator
Now let's wire it up with `Echo` and test it out:
```go
package main

import (
	"fmt"
	"reflect"
	"strings"

	"github.com/labstack/echo/v4"
)

type User struct {
	Age int32 `query:"age" guard:""`
	Paycheck *int32 `query:"paycheck" guard:"required"`
	SomeOtherField int32 `query:"some_other_field" guard:"max=100,min=10"`
}

func main() {
	e := echo.New()
	e.Validator = &MyValidator{}
	e.GET("/", func(c echo.Context) error {
		var p User
		if err := c.Bind(&p); err != nil {
			return c.JSON(400, map[string]string{"error": "invalid input"})
		}
		if err := c.Validate(p); err != nil {
			return c.JSON(400, map[string]string{"error": err.Error()})
		}
		return c.JSON(200, p)
	})
	e.Start(":11111")
}
```

I tweaked the fields a bit to make sure we test all the constraints. Now let's try some requests:
```bash
curl 'localhost:11111'
{"error":"field Paycheck is required but is nil"}

curl 'localhost:11111?paycheck=1'
{"error":"field SomeOtherField is less than min 10"}

curl 'localhost:11111?paycheck=1&some_other_field=-'
{"error":"invalid input"}

curl 'localhost:11111?paycheck=1&some_other_field=9'
{"error":"field SomeOtherField is less than min 10"}

curl 'localhost:11111?paycheck=1&some_other_field=10'
{"Age":0,"Paycheck":1,"SomeOtherField":10}

curl 'localhost:11111?paycheck=1&some_other_field=110'
{"error":"field SomeOtherField is greater than max 100"}
```
It works! 


# Conclusion
So that’s basically what `c.Validate` is: 
whatever you plug into `echo.Validator`, under the hood it's usually 
just "parse tags + walk values" with reflection.

This proof-of-concept validator works, but it has some drawbacks:

- This can't work with struct pointers, integer/unsigned integer pointer fields. You 
*can* add support, but code quickly becomes bloated so I omitted it for simplicity.

- Parser allows negative values for `min` and `max`, even for unsigned integer fields. 
But... You know, -1 *is* a big number in modular arithmetic, and anyone who uses it should know what they're doing.

- Many more!

However, that's it for this time. I hope this gives you a good idea of how validation works under the hood in Go,
and maybe you can try fixing the above issues as an exercise!
