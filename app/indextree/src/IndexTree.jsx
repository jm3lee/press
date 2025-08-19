import React, { useState, useEffect, useMemo } from 'react';
import { TextField } from '@mui/material';
import { RichTreeView } from '@mui/x-tree-view/RichTreeView';
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

  const idMap = useMemo(() => {
    const map = new Map();
    function walk(nodes) {
      nodes.forEach((n) => {
        map.set(n.id, n);
        if (n.children) {
          walk(n.children);
        }
      });
    }
    walk(filtered);
    return map;
  }, [filtered]);

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
      <RichTreeView
        items={filtered}
        defaultCollapseIcon={<ExpandMoreIcon />}
        defaultExpandIcon={<ChevronRightIcon />}
        expandedItems={expanded}
        onExpandedItemsChange={(event, ids) => setExpanded(ids)}
        slotProps={{
          item: ({ itemId, label }) => {
            const node = idMap.get(itemId);
            return {
              label: node?.url ? (
                <a
                  href={node.url}
                  className="internal-link"
                  onClick={(e) => e.stopPropagation()}
                >
                  {label}
                </a>
              ) : (
                label
              ),
            };
          },
        }}
      />
    </div>
  );
}

