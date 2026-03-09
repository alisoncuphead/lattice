import { useEffect, useRef, useState, useCallback } from "react";
import cytoscape from "cytoscape";
import {
  Layers,
  Clock,
  Shield,
  Search,
  Info,
  Trash2,
  CheckCircle,
  Sun,
  Moon,
  RefreshCw,
  Route,
} from "lucide-react";
import { format } from "date-fns";
import client, { setWorkspaceHeader, setUserHeader } from "./api/client";
import type { DiamondNode, Relationship, Conflict } from "./types";
import "./App.css";

// Generate a random user ID for prototyping
const RANDOM_USER_ID = "analyst-" + Math.random().toString(36).substring(2, 7);

function App() {
  const cyRef = useRef<HTMLDivElement>(null);
  const cyInstance = useRef<cytoscape.Core | null>(null);

  const [nodes, setNodes] = useState<DiamondNode[]>([]);
  const [selectedNode, setSelectedNode] = useState<DiamondNode | null>(null);
  const [pathStartNode, setPathStartNode] = useState<DiamondNode | null>(null);
  const [isPathMode, setIsPathMode] = useState(false);
  const [lockedBy, setLockedBy] = useState<string | null>(null);
  const [activeWorkspace, setActiveWorkspace] = useState<string | null>(null);
  const [workspaces, setWorkspaces] = useState<string[]>([]);
  const [userId] = useState<string>(RANDOM_USER_ID);
  const [atTimestamp, setAtTimestamp] = useState<number>(
    Math.floor(Date.now() / 1000),
  );
  const [searchQuery, setSearchQuery] = useState("");
  const [conflicts, setConflicts] = useState<Conflict[]>([]);
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    setUserHeader(userId);
  }, [userId]);

  // Check for locks when a node is selected
  useEffect(() => {
    const checkNodeLock = async () => {
      if (selectedNode) {
        try {
          const res = await client.get(`/locks/${selectedNode.uid}`);
          setLockedBy(res.data.locked_by);
        } catch (err) {
          console.error("Failed to check lock", err);
        }
      } else {
        setLockedBy(null);
      }
    };
    checkNodeLock();
  }, [selectedNode]);

  const getThemeColor = useCallback((variable: string) => {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).strip ? 
           getComputedStyle(document.documentElement).getPropertyValue(variable).trim() : 
           getComputedStyle(document.body).getPropertyValue(variable).trim();
  }, [theme]);

  // Initialize Cytoscape
  useEffect(() => {
    if (!cyRef.current) return;

    cyInstance.current = cytoscape({
      container: cyRef.current,
      boxSelectionEnabled: false,
      autounselectify: false,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#38bdf8",
            label: "data(name)",
            color: "var(--node-label-color)",
            "font-size": "12px",
            "text-valign": "bottom",
            "text-margin-y": 5,
            width: 40,
            height: 40,
          },
        },
        {
          selector: 'node[label="Adversary"]',
          style: { "background-color": "#ef4444", shape: "diamond" },
        },
        {
          selector: 'node[label="Infrastructure"]',
          style: { "background-color": "#38bdf8", shape: "rectangle" },
        },
        {
          selector: 'node[label="Capability"]',
          style: { "background-color": "#f59e0b", shape: "triangle" },
        },
        {
          selector: 'node[label="Victim"]',
          style: { "background-color": "#22c55e", shape: "ellipse" },
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "var(--edge-color)",
            "target-arrow-color": "var(--edge-color)",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            label: "data(type)",
            "font-size": "10px",
            "text-rotation": "autorotate",
            color: "#94a3b8",
          },
        },
        {
          selector: "node:selected",
          style: {
            "border-width": 3,
            "border-color": "var(--accent-color)",
          },
        },
        {
          selector: ".path-highlight",
          style: {
            "border-width": 5,
            "border-color": "var(--warning-color)",
          },
        },
      ],
      layout: { name: "cose" },
    });

    cyInstance.current.on("select", "node", (evt) => {
      const nodeData = evt.target.data("raw");
      setSelectedNode(nodeData);
      
      if (isPathMode) {
        if (!pathStartNode) {
          setPathStartNode(nodeData);
          alert("Now select the TARGET node.");
        } else if (pathStartNode.uid !== nodeData.uid) {
          findPath(nodeData);
        }
      }
    });

    cyInstance.current.on("unselect", "node", () => {
      setSelectedNode(null);
    });

    return () => {
      cyInstance.current?.destroy();
    };
  }, []);

  // Sync Cytoscape with Theme
  useEffect(() => {
    if (!cyInstance.current) return;
    cyInstance.current.style()
      .selector("node")
      .style("color", theme === "dark" ? "#f1f5f9" : "#1e293b")
      .selector("edge")
      .style("line-color", theme === "dark" ? "#475569" : "#94a3b8")
      .style("target-arrow-color", theme === "dark" ? "#475569" : "#94a3b8")
      .update();
  }, [theme]);

  const fetchData = async () => {
    try {
      setWorkspaceHeader(activeWorkspace);

      const [infraRes, advRes, capRes, vicRes, relRes, wsRes] = await Promise.all([
        client.get("/infrastructure/"),
        client.get("/adversaries/"),
        client.get("/capabilities/"),
        client.get("/victims/"),
        client.get(`/relationships/?at=${atTimestamp}`),
        client.get("/workspaces/"),
      ]);

      setWorkspaces(wsRes.data);

      const allNodes = [
        ...infraRes.data.map((n: any) => ({ ...n, label: "Infrastructure", name: n.value })),
        ...advRes.data.map((n: any) => ({ ...n, label: "Adversary", name: n.name })),
        ...capRes.data.map((n: any) => ({ ...n, label: "Capability", name: n.name })),
        ...vicRes.data.map((n: any) => ({ ...n, label: "Victim", name: n.identity })),
      ];

      setNodes(allNodes);

      if (cyInstance.current) {
        cyInstance.current.elements().remove();

        // Add all nodes first
        cyInstance.current.add(allNodes.map((node) => ({
          data: {
            id: node.uid,
            name: (node as any).name || (node as any).value || (node as any).identity,
            label: node.label,
            raw: node,
          },
        })));

        // Add all relationships
        relRes.data.forEach((rel: any) => {
          const edgeId = `edge-${rel.source.uid}-${rel.target.uid}-${rel.type}`;
          // Only add edge if both nodes exist in the graph
          if (cyInstance.current?.getElementById(rel.source.uid).length && 
              cyInstance.current?.getElementById(rel.target.uid).length) {
            cyInstance.current.add({
              data: {
                id: edgeId,
                source: rel.source.uid,
                target: rel.target.uid,
                type: rel.type,
              },
            });
          }
        });

        cyInstance.current.layout({ name: "cose", animate: true, padding: 50 }).run();
      }

      if (activeWorkspace) {
        const conflictRes = await client.get(`/workspaces/${activeWorkspace}/conflicts`);
        setConflicts(conflictRes.data);
      } else {
        setConflicts([]);
      }
    } catch (err) {
      console.error("Failed to fetch data", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, [activeWorkspace, atTimestamp]);

  const toggleTheme = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  const findPath = async (targetNode: DiamondNode) => {
    if (!pathStartNode) return;
    try {
      const res = await client.get(`/analysis/path?source_uid=${pathStartNode.uid}&target_uid=${targetNode.uid}&at=${atTimestamp}`);
      const pathData = res.data;
      
      if (pathData.length === 0) {
        alert("No path found between these nodes.");
        return;
      }

      if (cyInstance.current) {
        // Reset styles first
        cyInstance.current.elements().removeClass("path-highlight");
        
        // Highlight path elements
        pathData.forEach((step: any) => {
          if (step.type === "node") {
            cyInstance.current?.getElementById(step.data.uid).addClass("path-highlight");
          } else {
            // Relationships are harder to target without unique IDs, 
            // but we can find edges between the surrounding nodes in the path
          }
        });
      }
      setPathStartNode(null);
      setIsPathMode(false);
    } catch (err) {
      alert("Path analysis failed.");
    }
  };

  const handlePromote = async () => {
    if (!activeWorkspace) return;
    try {
      await client.post(`/workspaces/${activeWorkspace}/promote`);
      setActiveWorkspace(null);
      fetchData();
      alert("Workspace promoted to Production successfully!");
    } catch (err) {
      alert("Promotion failed. Resolve conflicts first.");
    }
  };

  return (
    <div className={`app-container ${theme === "light" ? "light-theme" : ""}`}>
      <div className="sidebar">
        <div className="panel-header">
          <Layers size={20} color="var(--accent-color)" />
          Lattice Workspace
        </div>

        <div className="panel-content">
          <div style={{ marginBottom: "20px" }}>
            <label style={{ display: "block", fontSize: "0.75rem", marginBottom: "8px", color: "#64748b" }}>
              ACTIVE STRATUM
            </label>
            <div style={{ display: "flex", gap: "10px" }}>
              <select
                value={activeWorkspace || "production"}
                onChange={(e) => setActiveWorkspace(e.target.value === "production" ? null : e.target.value)}
                style={{ flex: 1 }}
              >
                <option value="production">Production (Main)</option>
                {workspaces.map(ws => (
                  <option key={ws} value={ws}>{ws}</option>
                ))}
              </select>
              <button className="secondary" onClick={fetchData} title="Refresh Data">
                <RefreshCw size={16} />
              </button>
            </div>
          </div>

          {activeWorkspace && (
            <div style={{ marginBottom: "20px" }}>
              <button onClick={handlePromote} style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}>
                <CheckCircle size={16} /> Promote to Production
              </button>
            </div>
          )}

          <div style={{ marginBottom: "20px" }}>
            <button 
              className={isPathMode ? "warning" : "secondary"} 
              onClick={() => {
                if (isPathMode) {
                  setIsPathMode(false);
                  setPathStartNode(null);
                  cyInstance.current?.elements().removeClass("path-highlight");
                } else {
                  setIsPathMode(true);
                  alert("Select the START node for path analysis.");
                }
              }} 
              style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: "8px" }}
            >
              <Route size={16} /> {isPathMode ? "Cancel Analysis" : "Path Analysis (Shortest Path)"}
            </button>
          </div>

          <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "20px", marginBottom: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" }}>
              <Shield size={18} color="var(--accent-color)" />
              <span style={{ fontWeight: 600 }}>Quick Add IP</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              <input
                id="newNodeValue"
                type="text"
                placeholder="IP Address"
              />
              <button onClick={async () => {
                const val = (document.getElementById("newNodeValue") as HTMLInputElement).value;
                if (!val) return;
                try {
                  await client.post("/infrastructure/", { value: val, infra_type: "ip" });
                  (document.getElementById("newNodeValue") as HTMLInputElement).value = "";
                  fetchData();
                } catch (err) { alert("Failed to add node"); }
              }}>Add Node</button>
            </div>
          </div>

          <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "20px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" }}>
              <Info size={18} color="var(--accent-color)" />
              <span style={{ fontWeight: 600 }}>Node Details</span>
            </div>

            {selectedNode ? (
              <div className="node-card active">
                <div style={{ fontWeight: 700, marginBottom: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>{(selectedNode as any).name || (selectedNode as any).value}</span>
                  <div style={{ display: "flex", gap: "5px" }}>
                    {lockedBy && (
                      <span className="workspace-badge" style={{ backgroundColor: "var(--error-color)", fontSize: "0.6rem" }}>
                        Locked by {lockedBy === userId ? "You" : lockedBy}
                      </span>
                    )}
                    <span className={`workspace-badge ${selectedNode.workspace_id ? "badge-workspace" : "badge-production"}`}>
                      {selectedNode.workspace_id ? "Workspace" : "Production"}
                    </span>
                  </div>
                </div>
                <div className="property-list">
                  <div className="property-item">
                    <span className="property-label">Type</span>
                    <span className="property-value">{selectedNode.label}</span>
                  </div>
                  <div className="property-item">
                    <span className="property-label">UID</span>
                    <span className="property-value" style={{ fontSize: "0.7rem" }}>{selectedNode.uid.substring(0, 12)}...</span>
                  </div>
                  {Object.entries(selectedNode).map(([key, val]) => {
                    if (["uid", "workspace_id", "label", "name", "value"].includes(key)) return null;
                    return (
                      <div className="property-item" key={key}>
                        <span className="property-label">{key}</span>
                        <span className="property-value">{String(val)}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <p style={{ color: "#64748b", fontSize: "0.9rem", textAlign: "center", marginTop: "40px" }}>
                Select a node in the graph to view properties.
              </p>
            )}
          </div>

          {conflicts.length > 0 && (
            <div style={{ borderTop: "1px solid var(--border-color)", paddingTop: "20px", marginTop: "20px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "15px" }}>
                <Trash2 size={18} color="var(--error-color)" />
                <span style={{ fontWeight: 600, color: "var(--error-color)" }}>Conflicts ({conflicts.length})</span>
              </div>
              {conflicts.map((c) => (
                <div key={c.uid} className="node-card" style={{ borderColor: "var(--error-color)" }}>
                  <div style={{ fontSize: "0.8rem", fontWeight: 600 }}>{c.uid.substring(0, 8)} ({c.label})</div>
                  {Object.entries(c.differences).map(([prop, diff]) => (
                    <div key={prop} style={{ fontSize: "0.75rem", marginTop: "5px" }}>
                      <span style={{ color: "var(--success-color)" }}>{diff.production}</span> → <span style={{ color: "var(--accent-color)" }}>{diff.workspace}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="main-content">
        <div className="top-bar">
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <Shield size={24} color="var(--accent-color)" />
            <h2 style={{ margin: 0, fontSize: "1.25rem" }}>Lattice Explorer</h2>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <button className="theme-toggle" onClick={toggleTheme} title="Toggle Theme">
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <div className={`workspace-badge ${activeWorkspace ? "badge-workspace" : "badge-production"}`}>
              {activeWorkspace ? `WS: ${activeWorkspace}` : "Stratum: Production"}
            </div>
            <div style={{ fontSize: "0.75rem", color: "#64748b", display: "flex", alignItems: "center", gap: "5px" }}>
              <Info size={14} />
              User: <span style={{ color: "var(--accent-color)", fontWeight: 700 }}>{userId}</span>
            </div>
          </div>
        </div>

        <div id="cy" ref={cyRef}></div>

        <div className="temporal-slider">
          <Clock size={20} color="var(--accent-color)" />
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "5px", fontSize: "0.75rem", color: "#64748b" }}>
              <span>HISTORICAL (90d)</span>
              <span style={{ color: "var(--accent-color)", fontWeight: 700 }}>
                {format(atTimestamp * 1000, "yyyy-MM-dd HH:mm:ss")}
              </span>
              <span>PRESENT</span>
            </div>
            <input
              type="range"
              min={Math.floor(Date.now() / 1000) - 7776000} // 90 days
              max={Math.floor(Date.now() / 1000)}
              value={atTimestamp}
              onChange={(e) => setAtTimestamp(parseInt(e.target.value))}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
