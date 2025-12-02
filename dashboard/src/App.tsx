import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Device {
  mac: string;
  ip: string;
  vendor: string;
  first_seen: string;
  last_seen: string;
  is_new: boolean;
}

const App: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const devRes = await axios.get("http://localhost:5000/devices");
      setDevices(devRes.data);
      const alertRes = await axios.get("http://localhost:5000/alerts");
      setAlerts(alertRes.data);
    };
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  // Mock chart data (expand to device count over time)
  const chartData = [
    { name: "Now", devices: devices.length },
    { name: "1min", devices: devices.length - 1 },
  ]; // Placeholder

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Network Guardian</h1>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="bg-red-100 p-4 mb-4 rounded">
          <h2 className="font-semibold">New Devices (Potential Intruders)</h2>
          <ul>
            {alerts.map((a, i) => (
              <li key={i}>
                {a.ip} ({a.vendor})
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Device Table */}
      <div className="mb-4">
        <h2 className="font-semibold">Connected Devices ({devices.length})</h2>
        <table className="w-full border-collapse border">
          <thead>
            <tr>
              <th className="border p-2">IP</th>
              <th>MAC</th>
              <th>Vendor</th>
              <th>Last Seen</th>
              <th>New?</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d, i) => (
              <tr key={i}>
                <td className="border p-2">{d.ip}</td>
                <td>{d.mac}</td>
                <td>{d.vendor}</td>
                <td>{d.last_seen}</td>
                <td>{d.is_new ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quick Chart */}
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="devices" stroke="#8884d8" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default App;
