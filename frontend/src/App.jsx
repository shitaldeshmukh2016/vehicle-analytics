
import { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [stats, setStats] = useState({
    total: 0,
    up: 0,
    down: 0,
    colors: []
  });

  const [events, setEvents] = useState([]);

  const fetchData = async () => {
    try {
      const statsResponse = await fetch("http://localhost:5000/api/stats");
      const eventsResponse = await fetch("http://localhost:5000/api/events");

      if (!statsResponse.ok || !eventsResponse.ok) {
        throw new Error("API request failed");
      }

      setStats(await statsResponse.json());
      setEvents(await eventsResponse.json());
    } catch (error) {
      console.error("Dashboard error:", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard">
      <header>
        <h1>Vehicle Analytics Dashboard</h1>
        <p>Real-Time Vehicle Monitoring System</p>
      </header>

      <section className="stats">
        <div className="card">
          <h3>Total Vehicles</h3>
          <h2>{stats.total}</h2>
        </div>

        <div className="card">
          <h3>Up Direction</h3>
          <h2>{stats.up}</h2>
        </div>

        <div className="card">
          <h3>Down Direction</h3>
          <h2>{stats.down}</h2>
        </div>
      </section>

      <section className="panel">
        <h2>Vehicle Color Analysis</h2>
        {stats.colors.map((item) => (
          <p key={item.color}>
            {item.color}: <strong>{item.count}</strong>
          </p>
        ))}
      </section>

      <section className="panel">
        <h2>Recent Vehicle Events</h2>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Vehicle ID</th>
                <th>Type</th>
                <th>Color</th>
                <th>Direction</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {events.map((event) => (
                <tr key={event.id}>
                  <td>{event.id}</td>
                  <td>{event.vehicle_id}</td>
                  <td>{event.vehicle_type}</td>
                  <td>{event.color}</td>
                  <td>{event.direction}</td>
                  <td>{new Date(event.timestamp).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

export default App;

