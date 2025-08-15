import { useEffect, useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';

export default function MagicBar({ pages = [] }) {
  const [query, setQuery] = useState('');
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    try {
      const regex = new RegExp(query, 'i');
      setMatches(
        pages.filter((p) =>
          regex.test(p.title) || (p.shortcut && regex.test(p.shortcut))
        )
      );
    } catch {
      setMatches([]);
    }
  }, [query, pages]);

  const handleSelect = (url) => {
    window.location.href = url;
  };

  return (
    <>
      <AppBar position="fixed" sx={{ top: 0 }}>
        <Toolbar sx={{ p: 1 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search pages"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            inputProps={{ 'aria-label': 'search pages' }}
          />
        </Toolbar>
      </AppBar>
      {matches.length > 0 && (
        <Paper
          sx={{
            position: 'fixed',
            top: 56,
            left: 0,
            right: 0,
            maxHeight: '50vh',
            overflowY: 'auto',
            zIndex: (theme) => theme.zIndex.appBar - 1,
          }}
        >
          <List dense>
            {matches.map((p, idx) => (
              <ListItemButton key={idx} onClick={() => handleSelect(p.url)}>
                <ListItemText primary={p.title} />
              </ListItemButton>
            ))}
          </List>
        </Paper>
      )}
    </>
  );
}
