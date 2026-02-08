import React from 'react'

const metrics = [
  { id: 1, title: 'Calls Analyzed', value: '1,254' },
  { id: 2, title: 'Documents Processed', value: '3,412' },
  { id: 3, title: 'Risk Alerts', value: '27' }
]

const recent = [
  { id: 'C-1001', type: 'Call', summary: 'Detected potential compliance risk', time: '2h ago' },
  { id: 'D-203', type: 'Invoice', summary: 'Missing vendor tax ID', time: '5h ago' },
  { id: 'C-1005', type: 'Call', summary: 'Positive sentiment, action: follow-up', time: '1d ago' }
]

export default function Dashboard() {
  return (
    <div className="dashboard">
      <h2>Overview</h2>

      <div className="metrics">
        {metrics.map(m => (
          <div key={m.id} className="card metric">
            <div className="value">{m.value}</div>
            <div className="label">{m.title}</div>
          </div>
        ))}
      </div>

      <div className="panels">
        <section className="panel">
          <h3>Recent Activity</h3>
          <table className="recent-table">
            <thead>
              <tr><th>ID</th><th>Type</th><th>Summary</th><th>When</th></tr>
            </thead>
            <tbody>
              {recent.map(r => (
                <tr key={r.id}>
                  <td>{r.id}</td>
                  <td>{r.type}</td>
                  <td>{r.summary}</td>
                  <td>{r.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="panel chart">
          <h3>Processing Throughput</h3>
          <div className="placeholder-chart">📈 Placeholder chart</div>
        </section>
      </div>
    </div>
  )
}
