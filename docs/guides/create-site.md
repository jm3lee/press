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

## Explore built-in examples

Press ships with sample content in `src/examples` that demonstrates features like templating and metadata.
Build the repository and start the server to browse them:

```bash
# From the Press repository
r
r up
```

Then visit [http://localhost/examples](http://localhost/examples) to read the built-in examples.

## Next steps

- **Developing content** – Learn more about the build pipeline and adding assets in [build-process.md](build-process.md) and [store-files.md](store-files.md).
- **Customizing styles** – Edit `src/css/style.css` using SCSS syntax to style the site; the build compiles it to `build/css/style.css`.
- **Contributing** – Before submitting changes to Press, review [tests.md](tests.md) and [checklinks.md](checklinks.md) to run tests and link checks.

For additional topics, see the [guides index](README.md).
