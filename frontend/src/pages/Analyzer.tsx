import { useState } from 'react'
import { analyzeURL } from '../services/api'
import { URLAnalysis } from '../types'

export default function Analyzer() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<URLAnalysis | null>(null)
  const [error, setError] = useState('')

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url) {
      setError('Please enter a URL')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const data = await analyzeURL({ url, include_content: true })
      setResult(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'safe': return 'text-green-600 bg-green-50'
      case 'suspicious': return 'text-yellow-600 bg-yellow-50'
      case 'dangerous': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getRiskIcon = (level: string) => {
    switch (level) {
      case 'safe': return '✅'
      case 'suspicious': return '⚠️'
      case 'dangerous': return '🚨'
      default: return '❓'
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8">URL Analyzer</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <form onSubmit={handleAnalyze}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter URL to analyze
            </label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze URL'}
          </button>
        </form>
      </div>

      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className={`${getRiskColor(result.risk_level)} rounded-lg p-6 mb-6`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2">
                  {getRiskIcon(result.risk_level)} {result.risk_level.toUpperCase()}
                </h2>
                <p className="text-lg">Risk Score: {(result.risk_score * 100).toFixed(0)}%</p>
                <p className="text-sm mt-1">Confidence: {(result.confidence * 100).toFixed(1)}%</p>
                <p className="text-sm">Scan Time: {result.scan_time.toFixed(2)}s</p>
              </div>
            </div>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">URL</h3>
            <p className="text-gray-600 break-all bg-gray-50 p-3 rounded">{result.url}</p>
          </div>

          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-2">Recommendations</h3>
            <ul className="space-y-2">
              {result.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Detected Features</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Object.entries(result.features).map(([key, value]) => (
                <div key={key} className="bg-gray-50 p-3 rounded">
                  <p className="text-sm text-gray-600">{key.replace(/_/g, ' ')}</p>
                  <p className="font-semibold">{String(value)}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
