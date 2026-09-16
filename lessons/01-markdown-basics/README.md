# Lesson 01 — Markdown Fundamentals

## Objectives

By the end of this lesson you can write, from memory: headings, paragraphs,
bold, italic, inline code, code blocks, lists, nested lists, links, images,
blockquotes, horizontal rules, and escaped characters.

You will do this by writing a profile page about yourself (or a fictional
person) in `workspace/profile.md`.

## Concepts

### Seeing it rendered

Markdown is written as plain text and *rendered* into formatting. To see
the rendered version while you work:

- **VS Code**: open the `.md` file, press `Cmd+Shift+V` (macOS) or
  `Ctrl+Shift+V` (Windows/Linux). Or click the preview icon at the top
  right of the editor.
- **GitHub**: any `.md` file renders automatically when viewed.
- **No preview?** That is fine. Markdown is designed to be readable raw.

### Headings

A line beginning with `#` and a space is a heading. More `#` means a smaller
heading. Use one `#` for the document title and `##` for sections.

```markdown
# Title
## Section
### Subsection
```

Rule: space after the `#`. `#Title` is not a heading.

### Paragraphs and line breaks

A paragraph is one or more lines of text. A **blank line** separates
paragraphs. A single line break inside a paragraph is ignored when rendered,
so you can wrap long lines wherever you like.

```markdown
This is one paragraph, even
though it spans two lines.

This is a second paragraph.
```

To force a line break without a new paragraph, end the line with two spaces
or a backslash `\`.

### Emphasis

| Type this | Get this |
|-----------|----------|
| `*italic*` or `_italic_` | *italic* |
| `**bold**` or `__bold__` | **bold** |
| `***bold italic***` | ***bold italic*** |

No spaces just inside the stars: `** bold **` does not work.

### Inline code and code blocks

Wrap a word in backticks (`` ` ``, the key usually above Tab) to show it as
code: `` `git status` `` renders as `git status`. Use this for commands,
file names, and anything that must be typed exactly.

For several lines, use a *fenced* block: three backticks on their own line,
the content, three backticks again. Put a language name after the opening
fence for colour highlighting:

````markdown
```python
print("hello")
```
````

(Above, the outer fence uses four backticks so the inner three show up.
You rarely need this.)

### Lists

Unordered lists start each line with `-` (or `*` or `+`). Ordered lists
start with a number and a period. Indent by two or more spaces to nest.

```markdown
- fruit
  - apples
  - pears
- vegetables

1. wake up
2. coffee
   1. grind
   2. brew
3. work
```

You can write `1.` for every ordered item; Markdown numbers them for you.

### Links and images

```markdown
[text people click](https://example.com)
![description for people who cannot see it](https://picsum.photos/200)
```

An image is a link with `!` in front. The text in square brackets for an
image is *alt text*: it is read aloud by screen readers and shown if the
image fails to load. Always write it.

### Blockquotes

Start lines with `>`:

```markdown
> Simplicity is prerequisite for reliability.
> — Edsger Dijkstra
```

### Horizontal rules

Three or more dashes on a line by themselves, with blank lines around them:

```markdown
---
```

### Escaping

If you want a literal `*` or `#` or `` ` `` to appear, put a backslash in
front: `\*not italic\*` renders as \*not italic\*.

### Reference: the whole cheat sheet

[examples/markdown-cheatsheet.md](../../examples/markdown-cheatsheet.md)
has everything above on one page. Keep it open.

---

## Exercise 1.1 — Headings, paragraphs, emphasis

### Goal

Create `workspace/profile.md` with a title, two sections, two paragraphs,
bold, italic, and inline code.

### Why This Matters

Profiles, READMEs, and notes all start this way. Headings and emphasis are
most of the Markdown you will ever write.

### Before You Start

Your terminal is in the course folder (`git status` works).
`workspace/hello.md` exists from Lesson 00.

### Instructions

1. Create `workspace/profile.md` in your editor.

2. Give it this structure. Replace the bracketed parts with your own words;
   keep the heading levels.

   ```markdown
   # [Your name or a made-up name]

   ## About

   [One paragraph. Make one word **bold** and one word *italic*.]

   ## Tools I use

   [One paragraph mentioning at least one program by name in `inline code`,
   for example `git` or `vscode`.]
   ```

3. Save. Preview it if you can. Confirm from the terminal that the file
   exists:

   ```text
   ls workspace
   ```

   *Expected output:* `hello.md` and `profile.md`.

### Check Your Work

```text
python tools/check.py 01
```

Only the `01.profile.*` checks for this exercise need to pass yet; the list,
link, and image checks belong to the next exercises.

### What You Should Notice

- The raw file is readable without rendering. That is by design.
- `##` under `#` creates structure a reader can scan. Skipping levels
  (`#` straight to `###`) works but confuses readers and tools.

### Common Mistakes

- `#About` with no space: not a heading.
- Paragraphs run together because there is no blank line between them.
- `** bold **` with spaces inside: renders as literal stars.

### Recovery

If the file is a mess, delete its contents and start from the template. Git
is not tracking this file yet, so there is nothing to undo.

### Reflection

- Why might a tool prefer `# Title` over a big bold line?

---

## Exercise 1.2 — Lists and code blocks

### Goal

Add a nested list and a fenced code block to `workspace/profile.md`.

### Why This Matters

Steps, ingredients, options, and commands are lists and code blocks. These
two structures make technical writing readable.

### Before You Start

Exercise 1.1 done.

### Instructions

1. Add a section:

   ```markdown
   ## Things I want to learn

   1. [something]
      - [a detail about it]
      - [another detail]
   2. [something else]
   3. [a third thing]
   ```

   The nested items are indented by three spaces to line up under the text
   of item 1. Two spaces also works for `-` lists.

2. Add another section with a fenced code block. Put a language after the
   opening fence (`bash`, `text`, `python`, whatever fits):

   ````markdown
   ## A command I know

   ```bash
   git status
   ```
   ````

3. Save. Preview. The numbered list should show nested bullets under item 1,
   and the code block should appear in a box.

### Check Your Work

```text
python tools/check.py 01
```

### What You Should Notice

- Indentation carries meaning in lists. Elsewhere in Markdown it mostly
  does not.
- Inside a code block, Markdown symbols are shown literally. A `#` in a
  code block is not a heading.

### Common Mistakes

- Nested item not indented enough, so it appears as a top-level item.
- Forgetting the closing fence, so the rest of the document becomes code.
- Using the wrong character: a fence is three backticks, not three single
  quotes `'''`.

### Recovery

Same as 1.1: the file is untracked, edit freely. If the preview looks wrong
below a certain point, look for an unclosed fence above it.

### Reflection

- When would you choose a numbered list over a bulleted one?

---

## Exercise 1.3 — Links, images, quotes, rules, escaping

### Goal

Add a link, an image, a blockquote, a horizontal rule, and one escaped
character to `workspace/profile.md`.

### Why This Matters

Linking is what makes documentation a web instead of a pile. Alt text and
escaping are small habits that separate careful writers from careless ones.

### Before You Start

Exercises 1.1 and 1.2 done.

### Instructions

1. Add a horizontal rule and a final section:

   ```markdown
   ---

   ## Links

   I keep notes in [my notes](https://example.com).

   ![A placeholder image](https://picsum.photos/200)

   > A quote I like, and who said it.

   This sentence contains a literal asterisk: \* like that.
   ```

2. Replace the example URL with any real one. Keep the alt text meaningful.

3. Save. Preview. The rule should be a line across the page, the image
   should load (or show its alt text if you are offline), and the asterisk
   should appear as an asterisk, not turn anything italic.

### Check Your Work

```text
python tools/check.py 01
```

All `01.*` checks should now pass.

### What You Should Notice

- `[text](url)` and `![alt](url)` differ by one character. The text
  serves a different purpose in each.
- Escaping exists because Markdown symbols are ordinary characters too.

### Common Mistakes

- Reversing the brackets: `(text)[url]` is not a link.
- Blank alt text `![](...)`. Renders, but is inaccessible. The checker
  wants alt text.
- Horizontal rule without blank lines around it; some renderers then treat
  `---` as a heading underline for the line above.

### Recovery

Untracked file; edit freely. Compare against the cheat sheet.

### Reflection

- If an image fails to load, what does the reader see? Why does that matter?
- Your file is untracked. What do you think happens to it if you delete it?
  (Lesson 03 changes that answer.)
