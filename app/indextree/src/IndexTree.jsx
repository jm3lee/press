import React, { useState, useEffect } from 'react';

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
 * @param {{ node: TreeNodeData }} props
 * @returns {JSX.Element}
 */
function TreeNode({ node }) {
  const [open, setOpen] = useState(false);
  const hasChildren = Boolean(node.children && node.children.length);

  return (
    <li style={{ listStyle: 'none' }}>
      <div
        style={{ cursor: hasChildren ? 'pointer' : 'default' }}
        onClick={() => hasChildren && setOpen((o) => !o)}
      >
        {hasChildren && (open ? '▼ ' : '▶ ')}
        {node.url ? (
          <a href={node.url}>{node.title}</a>
        ) : (
          node.title
        )}
      </div>
      {hasChildren && open && (
        <ul style={{ paddingLeft: '1rem', margin: 0 }}>
          {node.children.map((child) => (
            <TreeNode key={child.id} node={child} />
          ))}
        </ul>
      )}
    </li>
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
      <input
        type="text"
        placeholder="Filter…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        style={{
          width: '100%',
          padding: '0.5rem',
          marginBottom: '1rem',
          boxSizing: 'border-box'
        }}
      />
      <ul style={{ paddingLeft: 0 }}>
        {filtered.map((node) => (
          <TreeNode key={node.id} node={node} />
        ))}
      </ul>
    </div>
  );
}
