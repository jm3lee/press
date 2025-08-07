import React, { useState, useEffect, useMemo } from 'react';
import { TextField } from '@mui/material';
import { TreeView } from '@mui/x-tree-view/TreeView';
import { TreeItem } from '@mui/x-tree-view/TreeItem';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

/**
 * @typedef {Object} TreeNodeData
 * @property {string} id - Unique identifier.
 * @property {string} label - Display label.
 * @property {string} [url] - Optional link URL.
 * @property {TreeNodeData[]} [children] - Nested entries.
 */

/**
 * Recursively filter a tree of nodes by label.
 *
 * @param {TreeNodeData[]} nodes - Original tree.
 * @param {string} query - Lowercase substring to match.
 * @returns {TreeNodeData[]} Filtered tree containing matching nodes.
 */
function filterTree(nodes, query) {
  return nodes
    .map((node) => {
      const children = node.children ? filterTree(node.children, query) : [];
      if (node.label.toLowerCase().includes(query) || children.length) {
        return { ...node, children };
      }
      return null;
    })
    .filter(Boolean);
}

/**
 * Collect all node IDs from the tree.
 *
 * @param {TreeNodeData[]} nodes
 * @param {string[]} ids
 * @returns {string[]}
 */
function collectIds(nodes, ids = []) {
  nodes.forEach((node) => {
    ids.push(node.id);
    if (node.children) {
      collectIds(node.children, ids);
    }
  });
  return ids;
}

/**
 * Render a TreeItem for a given node.
 *
 * @param {TreeNodeData} node
 * @returns {JSX.Element}
 */
function renderTree(node) {
  const label = node.url ? (
    <a href={node.url} onClick={(e) => e.stopPropagation()}>{node.label}</a>
  ) : (
    node.label
  );
  return (
    <TreeItem key={node.id} nodeId={node.id} label={label}>
      {Array.isArray(node.children)
        ? node.children.map((child) => renderTree(child))
        : null}
    </TreeItem>
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
  const [expanded, setExpanded] = useState([]);

  useEffect(() => {
    fetch(src)
      .then((res) => res.json())
      .then((data) => setTree(data))
      .catch(console.error);
  }, [src]);

  const filtered = useMemo(
    () => (query ? filterTree(tree, query.toLowerCase()) : tree),
    [tree, query],
  );

  useEffect(() => {
    if (query) {
      setExpanded(collectIds(filtered));
    } else {
      setExpanded([]);
    }
  }, [query, filtered]);

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
      <TreeView
        defaultCollapseIcon={<ExpandMoreIcon />}
        defaultExpandIcon={<ChevronRightIcon />}
        expanded={expanded}
        onNodeToggle={(event, ids) => setExpanded(ids)}
      >
        {filtered.map((node) => renderTree(node))}
      </TreeView>
    </div>
  );
}

