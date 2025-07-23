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
 * SearchIndex component renders a search input and a list of entries
 * fetched from `/static/index.json`. Uses Material-UI components for styling.
 *
 * @component
 * @returns {JSX.Element}
 */
export default function SearchIndex({name}) {
  const [entries, setEntries] = useState([]);
  const [query, setQuery] = useState('');
  const [filtered, setFiltered] = useState([]);

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
      .catch(console.error);
  }, [name]);

  useEffect(() => {
    const q = query.toLowerCase();
    setFiltered(
      query
        ? entries.filter((e) => e.title.toLowerCase().includes(q))
        : entries
    );
  }, [query, entries]);

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
