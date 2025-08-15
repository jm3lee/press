import { useEffect, useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import TextField from '@mui/material/TextField';
import IconButton from '@mui/material/IconButton';
import Paper from '@mui/material/Paper';
import List from '@mui/material/List';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Fab from '@mui/material/Fab';
import CloseIcon from '@mui/icons-material/Close';
import SearchIcon from '@mui/icons-material/Search';

export default function MagicBar({ pages = [] }) {
  const [open, setOpen] = useState(false);
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

  useEffect(() => {
    const handleKey = (e) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      } else if (e.key === 'Escape') {
        setOpen(false);
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, []);

  useEffect(() => {
    if (open) {
      setMatches(pages);
    } else {
      setQuery('');
      setMatches([]);
    }
  }, [open, pages]);

  const handleSelect = (url) => {
    window.location.href = url;
  };

  return (
    <>
      {open && (
        <>
          <AppBar position="fixed" sx={{ top: 0 }}>
            <Toolbar sx={{ p: 1, gap: 1 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search pages"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                inputProps={{ 'aria-label': 'search pages' }}
              />
              <IconButton
                edge="end"
                color="inherit"
                aria-label="close"
                onClick={() => setOpen(false)}
              >
                <CloseIcon />
              </IconButton>
            </Toolbar>
          </AppBar>
          {matches.length > 0 && (
            <Paper
              sx={{
                position: 'fixed',
                top: 56,
                left: 0,
                right: 0,
                maxHeight:
                  query === ''
                    ? (theme) => theme.spacing(12)
                    : '50vh',
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
      )}
      {!open && (
        <Fab
          color="primary"
          aria-label="open search"
          onClick={() => setOpen(true)}
          sx={{ position: 'fixed', bottom: 16, right: 16 }}
        >
          <SearchIcon />
        </Fab>
      )}
    </>
  );
}
