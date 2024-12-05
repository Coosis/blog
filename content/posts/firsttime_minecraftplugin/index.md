---
title: "First-Time: Minecraft Plugin"
date: 2023-08-18T13:48:04+08:00
draft: false
tags: ["Minecraft", "Plugin"]
---

# Before Everything Else:
A week ago, a friend of mine was planning to set up a minecraft server. I got excited, since I have a spare RaspberryPi 4 with 8 gigs of ram ready to be put to use. But with a 32-bit os, it wasn't really fit for the job. So I started to use my old laptop. I installed pop!_os, downloaded java 17, and after some research, set up a papermc server. The reason why I chose papermc is that it seems newest, with an out-standing performance and detailed documentation. Now of course, with a server able to run plugins, I wasn't going to just download everyone else's plugins. I decided to write my own.

# Maven or Gradle?
Before I could set up my project, I need to decide which build tool to use: [Gradle](https://docs.gradle.org/current/userguide/userguide.html), or [Maven](https://maven.apache.org/what-is-maven.html)? To my understanding, Gradle is newer, Maven is rich on the resources side. But in the end I chose Gradle, because Gradle seemed to support most of Maven's repositories.

# Failing
I searched the tutorials for creating my own plugin. Every tutorial I found suggested using JetBrains' IntelliJ Idea as IDE. At this point I have no knowledge of java whatsoever and I wasn't aware of the difficulties ahead, which was why I decided to try and set up the project using just vscode, a text editor. I know.

So I set up the directories like i was told on [papermc's documentation](https://docs.papermc.io/paper/dev/project-setup). And it didn't work, even after I set up build.gradle file and everything else correctly. In the end, I just gave up. I downloaded the IntelliJ IDEA, installed the Gradle Plugin and Minecraft Plugin.

# Finally Started Coding
At first, I wanted to create a teleport command. It's natural to have this thought: Player cannot teleport without op, but everyone has op makes it a security issue. It's also worth mentioning that I learnt about kotlin and immediately decided to use kotlin over java. Easier syntax is what I wanted. After, I learnt that to create a command, you need to:

1. Put down info about your command in the paper-plugin.yml file, like so:
```
commands:
    someCommand:
        usage: "/somecommand"
        description: "What the command does"
```
2. Register the command in onEnable(), like so:
```
override fun onEnable() {
        getCommand("someCommand")?.setExecutor(someClass())
        // Plugin startup logic
}
```
And in another file, do:
```
class someClass : CommandExecutor{
    override fun onCommand(sender: CommandSender, command: Command, label: String, args: Array<out String>?): Boolean {
        //do something here.
    }
}
```

So I did all that, and after some testing, I quickly found that did not work. I asked around in the papermc discord, apparently paper plugins don't do that anymore. There's another approach:

# Actually getting it done:
Create a class, inherit from the Command class, and do
`server.commandMap.register()`
from onEnable(). Here's the full code:
Main class:
```
class MangoPlugin : JavaPlugin() {
    override fun onEnable() {
        logger.info("loaded!")
        server.commandMap.register("mango", MangoExecutor(listOf("Mango"), logger))
        // Plugin startup logic
    }

    override fun onDisable() {
        // Plugin shutdown logic
        logger.info("unloaded!")
    }
}
```
MangoExecutor class:
```
class MangoExecutor(aliases: List<String?>, val logx: Logger) :
    Command("mango", "", "", aliases) {

    override fun execute(sender: CommandSender, commandLabel: String, args: Array<out String>?): Boolean {
        logx.info("command executed.")
        return true;
    }
}
```
Note that I put nothing in the second and third constructor of Command class, this is a bad practice, and I did it only for testing. It was time to get my sweet sweet .jar file. I ran the gradle:Build task and sure enough, I got my desired .jar file! It was in build/libs, I put it in the server, and... An error!
{{< gallery caption-effect="fade" >}}
    {{< figure src="/posts/firsttime_minecraftplugin/errorlog.jpg" link="errorlog.jpg" caption="error log" >}}
{{< /gallery >}}
Also, I learnt that the gradle:Build task does the same thing as IntelliJ IDEA's build artifact, if IntelliJ IDEA just calls gradle for the build task. Also, you need kotlin to use JVM the same version as java, in this case, 17. So go to build,gradle and add this(if the code already exists, just change the number accordingly):
```
kotlin {
    jvmToolchain(17)
}
```
A java.lang.NoClassDefFoundError! How could this be?
After searching aimlessly for hours, I was told gradle did not put kotlin libs into the .jar file, and that I need to use an extension called: [Gradle Shadow Plugin](https://imperceptiblethoughts.com/shadow/). Using this extension, I would be able to 'shadow' the libs into a 'fat-jar'. I added the line:
`id 'com.github.johnrengelman.shadow' version '8.1.1'`
in the plugins within the build.gradle file, like so:
```
plugins {
    id 'java'
    id 'org.jetbrains.kotlin.jvm' version '1.9.0'
    id 'com.github.johnrengelman.shadow' version '8.1.1'
}
```
and added this in the dependencies:
```
    shadow "org.jetbrains.kotlin:kotlin-stdlib:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-common:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.9.0"
```
like so:
```
dependencies {
    compileOnly "io.papermc.paper:paper-api:1.20.1-R0.1-SNAPSHOT"
    implementation "org.jetbrains.kotlin:kotlin-stdlib-jdk8"
    shadow "org.jetbrains.kotlin:kotlin-stdlib:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-common:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-jdk8:1.9.0"
    shadow "org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.9.0"
}
```
And to the right, do the shadowJar task provided by the extension, and another .jar, with a -all postfix appeared. Put it in the server, and... it worked!
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/firsttime_minecraftplugin/successoutput.jpg" caption="Success Log" >}}
{{< /gallery >}}

Side note: I never got the gallery thing figured out, so I'm stuck with just markdown images.
Side note: I got it I got it I got it!!! After learning the basics of html and css, I inspected the page and it turns out the path of the image was wrong. All better now!
