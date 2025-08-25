import React, { useState, useEffect } from 'react';
import {
  TextField,
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography
} from '@mui/material';

/**
 * @fileoverview Search component for browsing static index data.
 */

/**
 * Render a searchable list of content entries.
 *
 * @param {{name: string}} props
 * @returns {JSX.Element}
 */
export default function SearchIndex({ name }) {
  const [entries, setEntries] = useState([]);
  const [query, setQuery] = useState('');
  const [filtered, setFiltered] = useState([]);

  // Load the index file and transform it into a sorted array of entries.
  useEffect(() => {
    fetch(`/static/${name}`)
      .then((response) => response.json())
      .then((data) => {
        // transform the data object into an array of { code, title, url, … }
        const list = Object.entries(data).map(([code, info]) => ({
          code,
          ...info
        }));
        // sort entries by title
        list.sort((a, b) => a.title.localeCompare(b.title));
        setEntries(list);
        setFiltered(list);
      })
      .catch(console.error)
  }, [name]);

  // Update the displayed list based on the search query.
  useEffect(() => {
    const q = query.toLowerCase();
    setFiltered(
      query
        ? entries.filter((e) => e.title.toLowerCase().includes(q))
        : entries
    );
  }, [query, entries]);

  /**
   * Navigate to the given URL.
   *
   * @param {string} url - Destination location.
   */
  const go = (url) => {
    window.location.href = url;
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        marginX: 'auto',
        marginTop: 4
      }}
    >
      {/* add title "Content" */}
      <Typography
        variant="h6"
        component="h2"
        gutterBottom
      >
        Content
      </Typography>

      <TextField
        fullWidth
        variant="outlined"
        label="Search titles…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ marginBottom: 2 }}
      />

      {filtered.length > 0 ? (
        <List>
          {filtered.map((e) => (
            <ListItem
              button
              key={e.code}
              onClick={() => go(e.url)}
              sx={{
                borderRadius: 1,
                '&:hover': { backgroundColor: 'action.hover' }
              }}
            >
              <ListItemText primary={e.title} />
            </ListItem>
          ))}
        </List>
      ) : (
        <Typography
          variant="body2"
          color="textSecondary"
          align="center"
          sx={{ paddingY: 2 }}
        >
          No results found.
        </Typography>
      )}
    </Paper>
  );
}
