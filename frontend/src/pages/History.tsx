import { useEffect, useState } from 'react'
import { getHistory } from '../services/api'
import { URLAnalysis } from '../types'

export default function History() {
  const [history, setHistory] = useState<URLAnalysis[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadHistory()
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(() => {
      loadHistory()
    }, 3000)
    
    return () => clearInterval(interval)
  }, [])

  const loadHistory = async () => {
    try {
      const data = await getHistory(20)
      setHistory(data)
    } catch (error) {
      console.error('Failed to load history:', error)
    } finally {
      setLoading(false)
    }
  }

  const getRiskBadge = (level: string) => {
    const classes = {
      safe: 'bg-green-100 text-green-800',
      suspicious: 'bg-yellow-100 text-yellow-800',
      dangerous: 'bg-red-100 text-red-800',
    }[level] || 'bg-gray-100 text-gray-800'

    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${classes}`}>
        {level}
      </span>
    )
  }

  if (loading) {
    return <div className="text-center py-12">Loading history...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Scan History</h1>
        <div className="text-sm text-gray-500">
          Auto-refreshing • {history.length} scans
        </div>
      </div>

      {history.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <p className="text-gray-500">No scan history yet</p>
          <p className="text-sm text-gray-400 mt-2">Analyze a URL to see it here</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  URL
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Level
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {history.map((item, idx) => (
                <tr key={item.id || idx} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate" title={item.url}>
                    {item.url}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getRiskBadge(item.risk_level)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(item.risk_score * 100).toFixed(0)}%
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.confidence ? (item.confidence * 100).toFixed(1) : '-'}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
