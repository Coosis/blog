---
title: "Dynamic WebPage"
date: 2023-10-24T10:12:12+08:00
draft: false
tags: ["Web", "Dynamic"]
---

Dynamic or not dynamic, that is the question
<!--more-->

# Before Everything Else:
Remember how last time I promised to update once I learn more? It turned out that the web design contest has two groups: static, and dynamic. I wanted to try do a dynamic website, and oh boy was it a lot to unpack.

# Static and Dynamic?
According to [wikipedia]("https://en.wikipedia.org/wiki/Static_web_page"), static web page is a web page that is delivered to a web browser exactly as stored, displays the same information for all user, and often stored in a .html file.
A dynamic website, however, is often a web page generated by a web application. Its contents shift based on user inputs, informations. Dynamic websites are combinations of frontend and backend. 

{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/dynamicwebpage/frontend_backend.png" caption="how they connect" >}}
{{< /gallery >}}

# Frontend and Backend?
Frontend is the graphical user interface that we see on a page, the titles, the texts, the buttons and the images, etc. Frontend development is the process of creating those things, usually invoving html, css and javascript. Backend is what the user cannot see, the data-processing, the page-generating and more. It's the logic and mechanisms that happen on web pages. The frontend and backend are connected through http requests. When user say, clicks a button to log in, the a http request is made from frontend to backend, indicating a login is happening, so the server the backend is on can process the request.

# My Approach?
Since I only knew a bit of C#, I decided to write my backend using just that. C# is, well, not the most popular choice among its candidates like java and others. But it's definitely usable. So I began looking into it, and that was when I found: Razor Pages with asp.net. It's literally magic. Just let me tell you.

# RazorPage and asp.net
ASP.NET is a open-source web framework developed by microsoft. RazorPage is a new form of web page template ends in .cshtml. From that name you'd probably already have an idea what is does. It has the amazing ablity to embed C# code into html contents. When creating a razor page, a .cshtml.cs file is also created, and inside is where you can write your backend code. Wait, what just happened? Yes, when users are accessing a razor page, the GET and POST methods can directly be handled inside the corresponding .cshtml.cs file! With such power, I could become a "full-stack" web developer in just days!

# Result
After trying it out, I was able to create a site diplaying coffee. I implemented a log in mechanism, and yes, I had to rent a linux server. In my case, I used Apache as my web server, and created a mysql server for storing the user data.
Take a look!

{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/dynamicwebpage/websiteexample01.png" caption="a screenshot of my not-finished webpage." >}}
    {{< figure src="posts/dynamicwebpage/websiteexample02.png" caption="a screenshot of my not-finished webpage." >}}
    {{< figure src="posts/dynamicwebpage/websiteexample03.png" caption="a screenshot of my not-finished webpage." >}}
{{< /gallery >}}

# Actual Result
Nevermind I got obliterated in the contst
