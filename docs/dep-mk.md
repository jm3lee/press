# dep.mk Custom Dependencies

`dep.mk` is an optional Makefile that extends the build process with project specific rules.
It is included at the end of `app/shell/mk/build.mk` if present.

## How It Works

`build.mk` contains the line:

```make
-include /app/mk/dep.mk
```

During `docker compose` runs, the repository's `dep.mk` is mounted into the
shell container at `/app/mk/dep.mk`:

```yaml
shell:
  volumes:
    - ./dep.mk:/app/mk/dep.mk
```

If the file doesn't exist, the include is ignored. Any targets defined here run
inside the container and can create additional files under `build/`.

## Example: Quizzes

The provided `dep.mk` simply pulls in rules for building the React quiz
interface:

```make
include app/quiz/dep.mk
```

`app/quiz/dep.mk` compiles the quiz bundle with Vite and copies JSON quizzes into
`build/quiz/`. See `docs/quiz-workflow.md` for the full workflow.

## Customization

Add your own targets or includes to `dep.mk` to hook extra tools into the build.
This is a convenient place to generate assets that are not handled by the core
`build.mk` file.
