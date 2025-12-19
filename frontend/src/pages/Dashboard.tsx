import { useEffect, useState } from 'react'
import { getStats } from '../services/api'
import { Stats } from '../types'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = {
  safe: '#10b981',
  suspicious: '#f59e0b',
  dangerous: '#ef4444'
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(() => {
      loadStats()
    }, 3000)
    
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const data = await getStats()
      setStats(data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="text-center py-12">Loading...</div>
  }

  if (!stats) {
    return <div className="text-center py-12">Failed to load statistics</div>
  }

  const chartData = [
    { name: 'Safe', value: stats.safe_urls, color: COLORS.safe },
    { name: 'Suspicious', value: stats.suspicious_urls, color: COLORS.suspicious },
    { name: 'Dangerous', value: stats.phishing_detected, color: COLORS.dangerous },
  ]

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Scans"
          value={stats.total_scans}
          icon="📊"
          color="blue"
        />
        <StatCard
          title="Safe URLs"
          value={stats.safe_urls}
          icon="✅"
          color="green"
        />
        <StatCard
          title="Suspicious"
          value={stats.suspicious_urls}
          icon="⚠️"
          color="yellow"
        />
        <StatCard
          title="Phishing Detected"
          value={stats.phishing_detected}
          icon="🚨"
          color="red"
        />
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Threat Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

interface StatCardProps {
  title: string
  value: number
  icon: string
  color: 'blue' | 'green' | 'yellow' | 'red'
}

function StatCard({ title, value, icon, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
  }

  return (
    <div className={`${colorClasses[color]} rounded-lg p-6`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-75">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )
}
