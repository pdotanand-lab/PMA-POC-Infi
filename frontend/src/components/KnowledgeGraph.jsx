import React, { useEffect, useState } from "react";
import { getGraph } from "../api/api";

export default function KnowledgeGraph({ meetingId }) {
  const [graph, setGraph] = useState({ nodes: [], links: [] });

  useEffect(() => {
    if (!meetingId) return;
    getGraph(meetingId)
      .then((g) =>
        setGraph({
          nodes: Array.isArray(g?.nodes) ? g.nodes : [],
          links: Array.isArray(g?.links) ? g.links : [],
        })
      )
      .catch(console.error);
  }, [meetingId]);

  // simple circular layout (no external libs)
  const width = 800;
  const height = 320;
  const cx = width / 2;
  const cy = height / 2;
  const R = Math.min(width, height) / 2 - 30;

  const nodes = graph.nodes || [];
  const links = graph.links || [];

  const positioned = nodes.map((n, i) => {
    const ang = (2 * Math.PI * i) / Math.max(1, nodes.length);
    return {
      ...n,
      x: cx + R * Math.cos(ang),
      y: cy + R * Math.sin(ang),
    };
  });

  const posMap = Object.fromEntries(positioned.map((n) => [String(n.id), n]));

  const colorFor = (type) => {
    // tweak colors as you like
    if (type === "topic") return "#2563eb"; // blue-600
    return "#6b7280"; // gray-500
  };

  return (
    <div className="bg-white rounded-2xl shadow p-4">
      <h3 className="text-lg font-semibold mb-2">Knowledge Graph</h3>
      {nodes.length === 0 ? (
        <div className="text-sm text-gray-500">No topics yet.</div>
      ) : (
        <svg
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="xMidYMid meet"
          className="w-full h-[320px] border rounded-xl bg-white"
        >
          {/* links */}
          {links.map((l, idx) => {
            const s = posMap[String(l.source)];
            const t = posMap[String(l.target)];
            if (!s || !t) return null;
            return (
              <line
                key={idx}
                x1={s.x}
                y1={s.y}
                x2={t.x}
                y2={t.y}
                stroke="#cbd5e1"
                strokeWidth={Math.min(4, l.weight || 1)}
              />
            );
          })}

          {/* nodes */}
          {positioned.map((n, idx) => (
            <g key={idx}>
              <circle cx={n.x} cy={n.y} r={10} fill={colorFor(n.type)} />
              <title>{n.id}</title>
              <text x={n.x + 14} y={n.y + 4} fontSize="10" fill="#334155">
                {String(n.id)}
              </text>
            </g>
          ))}
        </svg>
      )}
    </div>
  );
}
