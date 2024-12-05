---
title: "First-Time: WebPage Design"
date: 2023-09-09T21:41:07+08:00
draft: false;
tags: ["HTML", "Web", "CSS", "Design"]
---

# Before Everything Else:
College just started. During one of the tours of the school, I found that there's a Web-Design contest to be held by our school. Although I don't have the first clue of writing html and css and javascript, I still wanted to go and try. There would also be sophomore, junior and senior students participate, but apparently as a freshman I can get bonus score so I would still have a chance. So I started looking into html...

# HTML
## What is HTML?
I like to think that before you learn something, you have to know what it is. 
Here's a quote on the [HTML page](https://en.wikipedia.org/wiki/HTML) from wikipedia:
>The HyperText Markup Language or HTML is the standard [markup language](https://en.wikipedia.org/wiki/Markup_language) for documents designed to be displayed in a web browser. It defines the meaning and structure of web content.
A problem immediately occurs: what is a markup language? Looking into this further we can find:
>A markup language is a text-encoding system consisting of a set of symbols inserted in a text document to control its structure, formatting, or the relationship between its parts.

Of course, a definition is important throughly, but I now consider it "a tool to control a text document's structure, formatting, or the relationship between its parts". This is what HTML does.
## Why HTML?
Now I'm sure there are plenty answer to this question, but in my opinion the most important reason is that HTML tells the browser exactly how to handle a page's content. A page with just lines after lines of words is tedious to look at. With HTML, designers can easier create a more good-looking web page.
## How?
As I just mentioned, as programmers, we need to write HTML files for the browser in order to create a web page of our choice.
## Basics
To start, create a file ends with ".html" or ".htm". HTML uses "html element" as the basic web page building block. An html element need "html tag" to be declared. A html element is usually defined by a start tag, contents and an end tag, like so:  
`<a>some content maybe</a>`  
There are also times when an html element does not have an end tag, like so:  
`<br>`  
In this case, the 'br' tag itself is the html element.
The basic structure of a html file is usually like this:
```
<html>
    <head>
        ...
    </head>
    <body>
        ...
    </body>
</html>
```
All HTML documents must have a document type declaration at the start before everything else: `<!DOCTYPE html>`. The declaration represents the document type, helping browsers to display web pages correctly. In \<head\> tag, you can insert .css files and scripts and all kinds of meta information. The \<body\> tag is where all visible parts will go, like texts, graphs, and images. Here's a list of some html tags:  
\<div\> tag: creates a divition for the elements  
\<title\> tag: defines the title of the page, including that shown in the browser, search results.  
\<h1\> tag: defines a heading. From 1 to 6, the smaller the number, the bigger and important the heading.  
\<hr\> tag: creates a horizontal line for splitting purposes. Note that a \</hr\>is not necessary.  
\<p\> tag: defines a paragraph.  
\<a\> tag: create a link. Use it like so:  
`<a href="https://www.google.com">Google site</a>`  
\<img\> tag: display an image.  

# CSS
## What is CSS?
After creating my first test .html file, I quickly wanted to do something more, like moving the texts around, having image laid over another image, etc. So I started searching for exactly how I can do that. That's when I found [CSS](https://en.wikipedia.org/wiki/CSS):  
>Cascading Style Sheets (CSS) is a [style sheet language](https://en.wikipedia.org/wiki/Style_sheet_language) used for describing the presentation of a document written in a markup language such as HTML or XML (including XML dialects such as SVG, MathML or XHTML). CSS is a cornerstone technology of the World Wide Web, alongside HTML and JavaScript. 

Looking into [style sheet language](https://en.wikipedia.org/wiki/Style_sheet_language), we can find that a [style sheet language](https://en.wikipedia.org/wiki/Style_sheet_language) is a computer language that expresses the presentation of structured documents. In this case, I believe, CSS is a computer language I can use to achieve that mentioned above.
## How?
There are plenty different answer that I found, but in conclusion, whenever the browser reads a css file, the browser use the information to format the page and the elements.
## Basics
There are three ways to insert a style sheet.  
1. External Style Sheet  
2. Internal Style Sheet  
3. Inline Style  
### External Style Sheet
An External Style Sheet is a style sheet in an independent .css file. It's usually used to modify a lot of pages at once, given that changing one .css file can change the style in all page that referece it.  
To use an external style sheet, create an .css file. In the .html file, link to the .css file using  
`<link rel="stylesheet" type="text/css" href="my_css_style.css">` in the head section of the .html file.
### Internal Style Sheet
When an individual page needs a style, an Internal Style Sheet could be used. This is faster to write in my opinion, as we can do what we want within the .html file.
To use an Internal Style Sheet, use `<style>` tag in the head section, and put the styles inside, like so:  
```
<html>
    <head>
        <style>
            ...
        </style>
    </head>
    <body>
        ...
    </body>
</html>
```
### Inline Style
An Inline Style is usually used when only a single element needs a style. Due to it being mixed deep within html code, readability suffers. But I think it's quick for testing.
To use an Inline Style, use `<style>` within the tag of the elements, like so:  
```
<div style="..."></div>
```
### Selectors:
Selectors are used in css to select the element we wish to modify. There are two types of selectors: **id selector** and **class selector**. An id selector uses id to identify an element, whereas class selector uses elements' class to identify a set of  elements, modifying them all at once. To set id or class for element, use `<... id="">` or `<... class="">` like so:  
`<div id="..."></div>`  
`<div class=""></div>`  
Also note that two or more elements cannot have the same id at the same time. 
In css, an id is expressed as '#' while a class is expressed as '.'. To match and modify an element,  use #\[id\] or .\[classname\] and type \[property\]:\[value\]; closed with a brace block. 
In the example below, all element in class "center" will be aligned to center.
```
.center{
    text-align:center;
}
```
You can also make all paragraph be aligned to center:
```
p{
    text-align:center;
}
```
You can also make it so that it's just the paragraph with the class "center":
```
p.center{
    text-align:center;
}
```
See the pattern here?

# End..?
I also found there's javascript that can make even more complex effects, event animation. I'll have to look into that. Maybe I'll reflect on all of those after the contest.

# End
Nevermind I got obliterated