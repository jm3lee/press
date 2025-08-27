# Adding Reading Notes for a New Book

This guide shows how to add reading notes for a book under `src/books`.
It follows the structure used in
[`src/books/hull-2016`](../../src/books/hull-2016).

## 1. Create the book directory

1. Choose a short slug for the book, such as `hull-2016`.
2. Create `src/books/<slug>` and switch into it.
3. Add an `index.yml` file with metadata:
   - `title` – full book title.
   - `citation` – text used when citing the book.
   - `url` – base URL, e.g. `/books/hull-2016/`.
   - `id` – unique identifier using underscores, e.g. `hull_2016`.
   - `author`, `pubdate`, `description`.

See the [metadata reference](../reference/metadata-fields.md) for field
definitions.

## 2. List the book and its notes

1. Create `index.md` with two sections:
   - **Bibliography** – cite the book. The hull example embeds a link to the
     Amazon listing stored in `hull-2016-amzn.yml`.
   - **Reading Notes** – add a `<dl>` block containing an
     `include_deflist_entry` call that pulls in note pages:

   ```python
   include_deflist_entry("src/books/<slug>", glob="p*.md")
   ```

2. Add a sidecar file like `hull-2016-amzn.yml` if you want to link to an
   external resource.

## 3. Write individual note pages

1. Name files `pNNN.md` where `NNN` is the page number or range.
2. Start each file with YAML front matter:

   ```yaml
   title: Topic (Book, page)
   citation: (Book, page)
   description: 'Brief plain text summary.'
   id: book_page
   partof: '{{linktitle("<slug>")}}'
   author: Your Name
   pubdate: Jun 1, 2024
   ```

3. Follow the metadata with Markdown content. Wrap paragraphs at 80 columns.
4. Cross‑link related notes using `{{ link("note_id") }}` or
   `{{ linktitle("note_id") }}`.

## 4. Build and update the index

1. From the project root, rebuild the site:

   ```bash
   /usr/bin/make -f redo.mk
   ```

2. Update the global index so links resolve:

   ```bash
   /usr/bin/make -f redo.mk update-index
   ```

3. Run tests to verify the build:

   ```bash
   /usr/bin/make -f redo.mk test
   ```

Refer to [tests.md](tests.md) for details on the test environment.

