import { useState, useEffect } from 'react'
import InputPanel from './components/InputPanel'
import ResultsPanel from './components/ResultsPanel'
import FilesPanel from './components/FilesPanel'
import Header from './components/Header'
import axios from 'axios'

function App() {
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [selectedFile, setSelectedFile] = useState(null)

  // Load configuration on mount
  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await axios.get('/api/config')
      setConfig(response.data)
    } catch (err) {
      console.error('Failed to fetch config:', err)
    }
  }

  const handleGenerate = async (inputData) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()

      if (inputData.file) {
        formData.append('file', inputData.file)
      }

      formData.append('text', inputData.text)
      formData.append('project_key', inputData.projectKey)
      formData.append('issue_type', inputData.issueType)
      formData.append('skip_review', inputData.skipReview)

      const response = await axios.post('/api/parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setResult(response.data)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate tickets')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = async (filename) => {
    try {
      const response = await axios.get(`/api/markdown/${filename}`)
      setSelectedFile(response.data)
    } catch (err) {
      setError('Failed to load file')
    }
  }

  const handleFileUpdate = async (filename, content) => {
    try {
      await axios.put(`/api/markdown/${filename}`, { content })
      setSelectedFile({ ...selectedFile, content })
    } catch (err) {
      setError('Failed to update file')
    }
  }

  const handleUploadToJira = async (filename) => {
    try {
      const response = await axios.post('/api/upload-to-jira', { filename })
      alert(response.data.message)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to upload to Jira')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Header config={config} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
              <div className="ml-auto pl-3">
                <button
                  onClick={() => setError(null)}
                  className="inline-flex text-red-400 hover:text-red-500"
                >
                  <span className="sr-only">Dismiss</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Panel */}
          <div className="lg:col-span-2">
            <InputPanel
              onGenerate={handleGenerate}
              loading={loading}
              defaultProject={config?.default_project || 'PROJ'}
            />

            {/* Results Panel */}
            {(result || selectedFile) && (
              <div className="mt-6">
                <ResultsPanel
                  result={result}
                  selectedFile={selectedFile}
                  onUpdate={handleFileUpdate}
                  onUploadToJira={handleUploadToJira}
                />
              </div>
            )}
          </div>

          {/* Files Panel */}
          <div className="lg:col-span-1">
            <FilesPanel
              onFileSelect={handleFileSelect}
              selectedFile={selectedFile?.filename}
            />
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-sm text-gray-500">
        JIRA Ticket Generator · Built with React + Flask
      </footer>
    </div>
  )
}

export default App
