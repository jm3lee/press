# Creating a New Site

This tutorial shows how to scaffold and run a new Press site.

## Generate project scaffolding

Run the helper script with the desired project name:

```bash
./bin/bash -c "create-site newsite"
cd newsite
git init
```

These commands generate the initial directory structure and initialize a Git repository for your site.

## Build and start the development stack

Define a handy alias to invoke the project's Makefile and then build and start services:

```bash
alias r='make -f redo.mk'
r
r up
```

The first `r` builds the site, while `r up` launches the development containers. Once complete, visit [http://localhost](http://localhost) to view the site.
