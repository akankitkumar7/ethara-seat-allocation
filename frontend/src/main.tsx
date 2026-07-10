import React, { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import "./styles.css";
import { NewJoinerReset } from "./NewJoinerReset";
const API = "http://localhost:8000";
const get = (path: string) =>
  fetch(API + path).then(async (r) => {
    if (!r.ok) throw new Error((await r.json()).detail);
    return r.json();
  });
const send = (path: string, method: string, body: unknown) =>
  fetch(API + path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(async (r) => {
    if (!r.ok) throw new Error((await r.json()).detail);
    return r.json();
  });
type Project = { id: number; name: string };
type Employee = {
  id: number;
  employee_code: string;
  name: string;
  email: string;
  department: string;
  role: string;
  joining_date: string;
  project_id: number;
  project: Project;
};
type Seat = {
  id: number;
  floor: number;
  zone: string;
  bay: string;
  seat_number: string;
  status: string;
};
const colors = [
  "#4f46e5",
  "#0ea5e9",
  "#14b8a6",
  "#f59e0b",
  "#f43f5e",
  "#8b5cf6",
];
function Dashboard() {
  const [summary, setSummary] = useState<any>();
  const [projects, setProjects] = useState<any[]>([]);
  const [floors, setFloors] = useState<any[]>([]);
  const load = () =>
    Promise.all([
      get("/dashboard/summary"),
      get("/dashboard/project-utilization"),
      get("/dashboard/floor-utilization"),
    ]).then(([a, b, c]) => {
      setSummary(a);
      setProjects(b);
      setFloors(c);
    });
  useEffect(() => {
    load();
  }, []);
  if (!summary) return <p>Loading dashboard…</p>;
  return (
    <section>
      <Title
        title="Workspace overview"
        subtitle="Live allocation and capacity across Ethara."
      />
      <div className="cards">
        {[
          ["Employees", summary.total_employees],
          ["Total seats", summary.total_seats],
          ["Occupied", summary.occupied_seats],
          ["Available", summary.available_seats],
          ["Reserved", summary.reserved_seats],
          ["Pending joiners", summary.pending_allocation],
        ].map(([l, v]) => (
          <div className="card" key={String(l)}>
            <small>{l}</small>
            <strong>{v}</strong>
          </div>
        ))}
      </div>
      <div className="charts">
        <Chart title="Project-wise allocation">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={projects}>
              <XAxis dataKey="project" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="occupied" fill="#4f46e5" radius={4} />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
        <Chart title="Floor-wise occupancy">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={floors}>
              <XAxis dataKey="floor" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="occupied" fill="#14b8a6" radius={4} />
            </BarChart>
          </ResponsiveContainer>
        </Chart>
      </div>
    </section>
  );
}
function Title({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="title">
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  );
}
function Chart({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="panel">
      <h3>{title}</h3>
      {children}
    </div>
  );
}
function Employees() {
  const [items, setItems] = useState<Employee[]>([]),
    [search, setSearch] = useState(""),
    [projects, setProjects] = useState<Project[]>([]),
    [project, setProject] = useState(""),
    [selected, setSelected] = useState<Employee | null>(null),
    [suggestions, setSuggestions] = useState<Seat[]>([]),
    [message, setMessage] = useState(""),
    [hasSearched, setHasSearched] = useState(false);
  const load = () =>
    get(
      `/employees?search=${encodeURIComponent(search)}${project ? `&project_id=${project}` : ""}`,
    ).then(setItems);
  useEffect(() => {
    get("/projects").then(setProjects);
    load();
  }, []);
  const pick = async (e: Employee) => {
    setSelected(e);
    setSuggestions(await get(`/employees/${e.id}/seat-suggestions`));
  };
  const allocate = async (seat: Seat) => {
    try {
      await send("/seats/allocate", "POST", {
        employee_id: selected?.id,
        seat_id: seat.id,
      });
      setMessage(`Allocated ${seat.seat_number} to ${selected?.name}.`);
      setSuggestions([]);
      load();
    } catch (e: any) {
      setMessage(e.message);
    }
  };
  const noResults = hasSearched && items.length === 0;
  const noResultText = search.trim()
    ? `Employee “${search.trim()}” does not exist or does not match the selected project.`
    : "No employees were found for the selected filters.";
  return (
    <section>
      <Title
        title="Employees"
        subtitle="Search people, projects, and manage pending joiner seating."
      />
      <div className="toolbar">
        <input
          placeholder="Name, email or employee ID"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={project} onChange={(e) => setProject(e.target.value)}>
          <option value="">All projects</option>
          {projects.map((p) => (
            <option value={p.id} key={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <button
          onClick={() => {
            setHasSearched(true);
            load();
          }}
        >
          Search
        </button>
      </div>
      {message && <p className="notice">{message}</p>}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Employee</th>
              <th>Project</th>
              <th>Department</th>
              <th>Joined</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {noResults ? (
              <tr>
                <td className="empty-state" colSpan={5}>
                  {noResultText}
                </td>
              </tr>
            ) : (
              items.map((e) => (
                <tr key={e.id}>
                  <td>
                    <b>{e.name}</b>
                    <br />
                    <small>
                      {e.employee_code} · {e.email}
                    </small>
                  </td>
                  <td>{e.project?.name}</td>
                  <td>{e.department}</td>
                  <td>{e.joining_date}</td>
                  <td>
                    <button className="secondary" onClick={() => pick(e)}>
                      Seat options
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {selected && (
        <div className="panel suggestions">
          <h3>Suggested seats for {selected.name}</h3>
          <p>Ranked by where the {selected.project?.name} team already sits.</p>
          {suggestions.length ? (
            <div className="seat-grid">
              {suggestions.map((s) => (
                <button key={s.id} className="seat" onClick={() => allocate(s)}>
                  Floor {s.floor} · {s.zone}
                  <small>
                    {s.bay} / {s.seat_number}
                  </small>
                </button>
              ))}
            </div>
          ) : (
            <p>
              No available suggestion. This employee may already be allocated.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
function NewJoiner() {
  const [projects, setProjects] = useState<Project[]>([]),
    [employee, setEmployee] = useState<Employee | null>(null),
    [seats, setSeats] = useState<Seat[]>([]),
    [error, setError] = useState("");
  useEffect(() => {
    get("/projects").then(setProjects);
  }, []);
  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      const x = await send("/employees", "POST", {
        name: f.get("name"),
        email: f.get("email"),
        department: f.get("department"),
        role: f.get("role"),
        joining_date: f.get("joining_date"),
        project_id: Number(f.get("project_id")),
      });
      setEmployee(x);
      setSeats(await get(`/employees/${x.id}/seat-suggestions`));
      setError("");
    } catch (x: any) {
      setError(x.message);
    }
  };
  const allocate = async (s: Seat) => {
    try {
      await send("/seats/allocate", "POST", {
        employee_id: employee?.id,
        seat_id: s.id,
      });
      setError(`Seat ${s.seat_number} allocated successfully.`);
      setSeats([]);
    } catch (e: any) {
      setError(e.message);
    }
  };
  return (
    <section>
      <Title
        title="New joiner"
        subtitle="Create an employee and allocate a suggested seat immediately."
      />
      {error && <p className="notice">{error}</p>}
      <form className="form panel" onSubmit={submit}>
        {[
          ["name", "Full name"],
          ["email", "Work email"],
          ["department", "Department"],
          ["role", "Role"],
        ].map(([k, l]) => (
          <label key={k}>
            {l}
            <input required name={k} type={k === "email" ? "email" : "text"} />
          </label>
        ))}
        <label>
          Joining date
          <input
            required
            name="joining_date"
            type="date"
            defaultValue={new Date().toISOString().slice(0, 10)}
          />
        </label>
        <label>
          Active project
          <select name="project_id">
            {projects.map((p) => (
              <option value={p.id} key={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <button>Create and suggest seats</button>
      </form>
      {employee && (
        <Chart title={`Recommended seats for ${employee.name}`}>
          <div className="seat-grid">
            {seats.map((s) => (
              <button className="seat" onClick={() => allocate(s)} key={s.id}>
                Floor {s.floor}, {s.zone}
                <small>
                  {s.bay} · {s.seat_number}
                </small>
              </button>
            ))}
          </div>
        </Chart>
      )}
    </section>
  );
}
function Seats() {
  const [seats, setSeats] = useState<Seat[]>([]),
    [status, setStatus] = useState("Available");
  useEffect(() => {
    get("/seats?status=" + status).then(setSeats);
  }, [status]);
  return (
    <section>
      <Title
        title="Seat management"
        subtitle="View availability by physical location."
      />
      <div className="toolbar">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          {["Available", "Occupied", "Reserved", "Maintenance"].map((x) => (
            <option key={x}>{x}</option>
          ))}
        </select>
      </div>
      <div className="seat-grid large">
        {seats.slice(0, 300).map((s) => (
          <div className={"seat static " + s.status.toLowerCase()} key={s.id}>
            Floor {s.floor} · Zone {s.zone}
            <small>
              {s.bay} / {s.seat_number}
            </small>
          </div>
        ))}
      </div>
    </section>
  );
}
function Assistant() {
  const [q, setQ] = useState(""),
    [history, setHistory] = useState<{ q: string; a: string }[]>([]),
    [busy, setBusy] = useState(false);
  const ask = async (e: FormEvent) => {
    e.preventDefault();
    if (!q) return;
    setBusy(true);
    try {
      const a = await send("/ai/query", "POST", { query: q });
      setHistory((h) => [...h, { q, a: a.answer }]);
      setQ("");
    } finally {
      setBusy(false);
    }
  };
  return (
    <section>
      <Title
        title="Ethara Assistant"
        subtitle="Ask about seating, projects, availability, and utilization."
      />
      <div className="chat panel">
        {history.length === 0 && (
          <p>
            Try “Where is employee Amit seated?” or “Show all available seats on
            Floor 3.”
          </p>
        )}
        {history.map((x, i) => (
          <div key={i}>
            <p className="question">{x.q}</p>
            <p className="answer">{x.a}</p>
          </div>
        ))}
        <form onSubmit={ask}>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask a question…"
          />
          <button disabled={busy}>{busy ? "Checking…" : "Ask"}</button>
        </form>
      </div>
    </section>
  );
}
function App() {
  const [page, setPage] = useState("Dashboard");
  const pages: any = {
    Dashboard: <Dashboard />,
    Employees: <Employees />,
    "New Joiner": <NewJoinerReset />,
    Seats: <Seats />,
    Assistant: <Assistant />,
  };
  return (
    <main>
      <aside>
        <div className="brand">
          ethara<span>space</span>
        </div>
        {Object.keys(pages).map((x) => (
          <button
            key={x}
            className={page === x ? "active" : ""}
            onClick={() => setPage(x)}
          >
            {x}
          </button>
        ))}
        <small>Seat Allocation System</small>
      </aside>
      <article>{pages[page]}</article>
    </main>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
