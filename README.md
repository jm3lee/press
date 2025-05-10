```
alias r='make -f redo.mk'
r setup
cp foo.png app/to-webp/input
r to-webp
ls app/to-webp/output
```
