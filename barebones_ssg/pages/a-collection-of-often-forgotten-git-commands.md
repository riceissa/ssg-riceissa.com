---
layout: default
title: A collection of often-forgotten git commands
comments: "yes"
disqus-id: 9b9095c5f72440171ea4125a2f1bd22af5eab113
math: ""
last-major-revision-date: 
license: "CC-BY"
tags: git, linux
---


- View all unadded files, including ones in <code>.gitignore</code>.

    ```bash
    git add -Anf
    ```

    `-A`: all; `-n`: dry run; `-f`: force files in `.gitignore`.

    See [this question](http://stackoverflow.com/questions/3801321/git-list-only-untracked-files-also-custom-commands).

- Dealing with submodules

    ```bash
    git submodule update --init 
    git submodule foreach git pull origin master
    ```

    See [here](http://stackoverflow.com/questions/5828324/update-git-submodule) and [here](http://blog.jacius.info/git-submodule-cheat-sheet/).
