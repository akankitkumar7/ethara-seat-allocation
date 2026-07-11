import { FormEvent, useEffect, useRef, useState } from "react";

const API = import.meta.env.VITE_API_URL;
const get = (path: string) =>
  fetch(API + path).then(async (response) => {
    if (!response.ok) throw new Error((await response.json()).detail);
    return response.json();
  });
const send = (path: string, body: unknown) =>
  fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).then(async (response) => {
    if (!response.ok) throw new Error((await response.json()).detail);
    return response.json();
  });

type Project = { id: number; name: string };
type Employee = { id: number; name: string };
type Seat = {
  id: number;
  floor: number;
  zone: string;
  bay: string;
  seat_number: string;
};

export function NewJoinerReset() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [seats, setSeats] = useState<Seat[]>([]);
  const [message, setMessage] = useState("");
  const formRef = useRef<HTMLFormElement>(null);

  useEffect(() => {
    get("/projects").then(setProjects);
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    try {
      const created = await send("/employees", {
        name: form.get("name"),
        email: form.get("email"),
        department: form.get("department"),
        role: form.get("role"),
        joining_date: form.get("joining_date"),
        project_id: Number(form.get("project_id")),
      });
      setEmployee(created);
      setSeats(await get(`/employees/${created.id}/seat-suggestions`));
      setMessage("");
    } catch (error: any) {
      setMessage(error.message);
    }
  }

  async function allocate(seat: Seat) {
    if (!employee) return;
    try {
      await send("/seats/allocate", {
        employee_id: employee.id,
        seat_id: seat.id,
      });
      setMessage(
        `Seat ${seat.seat_number} allocated successfully. The form is ready for the next joiner.`,
      );
      setSeats([]);
      setEmployee(null);
      formRef.current?.reset();
    } catch (error: any) {
      setMessage(error.message);
    }
  }

  return (
    <section>
      <div className="title">
        <h1>New joiner</h1>
        <p>Create an employee and allocate a suggested seat immediately.</p>
      </div>
      {message && <p className="notice">{message}</p>}
      <form ref={formRef} className="form panel" onSubmit={submit}>
        {[
          ["name", "Full name"],
          ["email", "Work email"],
          ["department", "Department"],
          ["role", "Role"],
        ].map(([key, label]) => (
          <label key={key}>
            {label}
            <input
              required
              name={key}
              type={key === "email" ? "email" : "text"}
            />
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
          <select required name="project_id" defaultValue="">
            <option value="" disabled>
              Select project
            </option>
            {projects.map((project) => (
              <option value={project.id} key={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </label>
        <button>Create and suggest seats</button>
      </form>
      {employee && (
        <div className="panel">
          <h3>Recommended seats for {employee.name}</h3>
          <div className="seat-grid">
            {seats.map((seat) => (
              <button
                className="seat"
                onClick={() => allocate(seat)}
                key={seat.id}
              >
                Floor {seat.floor}, {seat.zone}
                <small>
                  {seat.bay} · {seat.seat_number}
                </small>
              </button>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
