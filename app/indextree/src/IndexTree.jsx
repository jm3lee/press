import React, { useState, useEffect } from 'react';
import {
  TextField,
  List,
  ListItemButton,
  ListItemText,
  Collapse
} from '@mui/material';
import { ExpandLess, ExpandMore } from '@mui/icons-material';

/**
 * @typedef {Object} TreeNodeData
 * @property {string} id - Unique identifier.
 * @property {string} title - Display title.
 * @property {string} [url] - Optional link URL.
 * @property {TreeNodeData[]} [children] - Nested entries.
 */

/**
 * Recursively filter a tree of nodes by title.
 *
 * @param {TreeNodeData[]} nodes - Original tree.
 * @param {string} query - Lowercase substring to match.
 * @returns {TreeNodeData[]} Filtered tree containing matching nodes.
 */
function filterTree(nodes, query) {
  return nodes
    .map((node) => {
      const children = node.children ? filterTree(node.children, query) : [];
      if (node.title.toLowerCase().includes(query) || children.length) {
        return { ...node, children };
      }
      return null;
    })
    .filter(Boolean);
}

/**
 * Render a single tree node with optional children.
 *
 * @param {{ node: TreeNodeData, forceOpen: boolean }} props
 * @returns {JSX.Element}
 */
function TreeNode({ node, forceOpen }) {
  const [open, setOpen] = useState(false);
  const hasChildren = Boolean(node.children && node.children.length);

  useEffect(() => {
    if (forceOpen) {
      setOpen(true);
    }
  }, [forceOpen]);

  return (
    <>
      <ListItemButton onClick={() => hasChildren && setOpen((o) => !o)} sx={{ pl: 0 }}>
        {hasChildren && (open ? <ExpandLess /> : <ExpandMore />)}
        {node.url ? (
          <ListItemText
            primary={<a href={node.url} onClick={(e) => e.stopPropagation()}>{node.title}</a>}
          />
        ) : (
          <ListItemText primary={node.title} />
        )}
      </ListItemButton>
      {hasChildren && (
        <Collapse in={open} timeout="auto" unmountOnExit>
          <List component="div" disablePadding sx={{ pl: 4 }}>
            {node.children.map((child) => (
              <TreeNode key={child.id} node={child} forceOpen={forceOpen} />
            ))}
          </List>
        </Collapse>
      )}
    </>
  );
}

/**
 * Display a collapsible, searchable tree of navigation entries.
 *
 * @param {{ src: string }} props - Location of the JSON tree data.
 * @returns {JSX.Element}
 */
export default function IndexTree({ src }) {
  const [tree, setTree] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    fetch(src)
      .then((res) => res.json())
      .then((data) => setTree(data))
      .catch(console.error);
  }, [src]);

  const filtered = query
    ? filterTree(tree, query.toLowerCase())
    : tree;

  return (
    <div>
      <TextField
        fullWidth
        variant="outlined"
        label="Filter…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        sx={{ mb: 2 }}
      />
      <List sx={{ p: 0 }}>
        {filtered.map((node) => (
          <TreeNode key={node.id} node={node} forceOpen={Boolean(query)} />
        ))}
      </List>
    </div>
  );
}
