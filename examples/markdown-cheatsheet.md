# Markdown Cheat Sheet

Everything from Lessons 01 and 02 on one page.

## Structure

```markdown
# Heading 1
## Heading 2
### Heading 3

A paragraph. Blank lines separate paragraphs.
Two spaces at the end of a line  
force a line break.

---
```

## Emphasis and code

```markdown
*italic*   **bold**   ***bold italic***   ~~strikethrough~~
`inline code`
\*escaped asterisk\*
```

````markdown
```bash
git status
```
````

## Lists

```markdown
- item
  - nested item
- item

1. first
2. second
   1. nested

- [ ] to do
- [x] done
```

## Links and images

```markdown
[text](https://example.com)
[text](relative/path.md)
[text](../up-one-level.md)
[text](#heading-anchor)
![alt text](image.png)
<https://bare-url.example.com>
```

## Blockquote

```markdown
> quoted text
> — attribution
```

## Table

```markdown
| Left | Centre | Right |
|:-----|:------:|------:|
| a    |   b    |     c |
```

## Things that trip people up

| Symptom | Cause |
|---------|-------|
| `#Heading` shows a literal `#` | no space after `#` |
| Two lines render as one paragraph | no blank line between them |
| `** bold **` shows stars | spaces inside the stars |
| Rest of document is one code block | unclosed fence |
| Table renders as text with pipes | missing `|---|` separator row |
| Link goes nowhere | path is relative to the *file*, not your terminal |
