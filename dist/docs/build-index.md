# Metadata Index Builder

A command-line tool to scan directories for Markdown (`.md`) and YAML
(`.yml`/`.yaml`) files, extract their metadata, generate URLs for Markdown
sources, and build a consolidated JSON index mapping each document’s `id` to its
metadata. See [Metadata Fields](metadata-fields.md) for an overview of the
supported keys and defaults.

## Usage

```bash
# Scan 'content/' for .md, .yml, and .yaml files and print JSON result
./build_index.py content/

# Scan 'dist/docs/' and write the index to 'index.json'
./build_index.py dist/docs/ --output index.json

# Write logs to a file
./build_index.py dist/docs/ -o index.json --log build-index.log
```

### Arguments

- `<source_dir>`  
  Root directory to scan for Markdown and YAML files.

- `-o, --output <path>`
  (Optional) Path to write the resulting JSON index. Defaults to stdout if omitted.

- `-l, --log <path>`
  (Optional) Write logs to the specified file.

## Example Output

```json
{
  "intro": {
    "id": "intro",
    "title": "Introduction",
    "date": "2023-05-01",
    "url": "/guide/intro.html"
  },
  "settings": {
    "id": "settings",
    "title": "Configuration Settings",
    "citation": "configuration settings",
    "url": "/config/settings.html"
  }
}
```

## How It Works

1. **Scan Files**  
   Recursively finds Markdown and YAML files in the specified directory.

2. **Process Markdown**  
   - Reads YAML frontmatter delimited by `---` markers.  
   - Computes the corresponding HTML URL for files under `src/`.

3. **Process YAML**  
   - Parses the entire YAML document.  
   - Auto-fills missing `citation` (lowercased `title`) and `id` (filename without extension).  
   - Computes URL if the file lives under `src/`.

4. **Indexing**
   - Validates that each metadata entry has a unique `id`.
   - Aggregates all entries into a single JSON object.

Once the index is generated you can insert it into Redis with
[`update-index`](update-index.md).
