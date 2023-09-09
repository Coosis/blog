---
title: "First-Time: WebPage Design"
date: 2023-09-09T21:41:07+08:00
draft: false;
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
\<title\> tag: defines the title of the page, including that shown in the browser, search results.
\<h1\> tag: defines a heading. From 1 to 6, the smaller the number, the bigger and important the heading.
\<hr\> tag: creates a horizontal line for splitting purposes. Note that a \</hr\>is not necessary.
\<p\> tag: defines a paragraph.
\<a\> tag: create a link. Use it like so: `<a href="https://www.google.com">Google site</a>`
\<img\> tag: display an image.
