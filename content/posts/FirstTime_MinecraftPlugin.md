---
title: "First-Time: Minecraft Plugin"
date: 2023-08-18T13:48:04+08:00
draft: false
tags: ["Minecraft", "Plugin"]
---

# Before Everything Else:
A week ago, a friend of mine was planning to set up a minecraft server. I got excited, since I have a spare RaspberryPi 4 with 8 gigs of ram ready to be put to use. But with a 32-bit os, it wasn't really fit for the job. So I started to use my old laptop. I installed pop!_os, downloaded java 17, and after some research, set up a papermc server. The reason why I chose papermc is that it seems newest, with a out-standing performance and detailed documentation. Now of course, with a server able to run plugins, I wasn't going to just download everyone else's plugins. I decided to write my own.

# Failing
I searched the tutorials for creating my own plugin. Every tutorial I found suggested using JetBrains' IntelliJ Idea as IDE. At this point I have no knowledge of java whatsoever and I wasn't aware of the difficulties ahead, which was why I decided to try and set up the project using just vscode, a text editor. I know.

Before I could set up my project, I need to decide which build tool to use: [Gradle](https://docs.gradle.org/current/userguide/userguide.html), or [Maven](https://maven.apache.org/what-is-maven.html)? To my understanding, Gradle is newer, Maven is rich on the resources side. But in the end I chose Gradle, because Gradle seemed to support most of Maven's repositories.

So I set up the directories like i was told on [papermc's documentation](https://docs.papermc.io/paper/dev/project-setup). And it didn't work, even after I set up build.gradle file and everything else correctly.