import { useState } from 'react'

export default function InputPanel({ onGenerate, loading, defaultProject }) {
  const [text, setText] = useState('')
  const [file, setFile] = useState(null)
  const [projectKey, setProjectKey] = useState(defaultProject)
  const [issueType, setIssueType] = useState('task')
  const [skipReview, setSkipReview] = useState(false)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      // Read file content and set text
      const reader = new FileReader()
      reader.onload = (event) => {
        setText(event.target.result)
      }
      reader.readAsText(selectedFile)
    }
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    onGenerate({
      text,
      file,
      projectKey,
      issueType,
      skipReview
    })
  }

  const handleClear = () => {
    setText('')
    setFile(null)
    document.getElementById('file-upload').value = ''
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg className="h-5 w-5 mr-2 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
        Input
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* File Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload File
          </label>
          <div className="flex items-center space-x-2">
            <label className="flex-1 flex items-center justify-center px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-primary-500 cursor-pointer transition-colors">
              <svg className="h-5 w-5 mr-2 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span className="text-sm text-gray-600">
                {file ? file.name : 'Choose file or drag here'}
              </span>
              <input
                id="file-upload"
                type="file"
                className="hidden"
                onChange={handleFileChange}
                accept=".txt,.md,.doc,.docx"
              />
            </label>
            {file && (
              <button
                type="button"
                onClick={handleClear}
                className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        <div className="flex items-center">
          <div className="flex-1 border-t border-gray-200"></div>
          <span className="px-3 text-sm text-gray-500">or</span>
          <div className="flex-1 border-t border-gray-200"></div>
        </div>

        {/* Text Input */}
        <div>
          <label htmlFor="text-input" className="block text-sm font-medium text-gray-700 mb-2">
            Type or Paste Text
          </label>
          <textarea
            id="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type or paste your meeting notes, bug description, or requirements here...&#10;&#10;Example:&#10;Build user authentication system. Users should login with email and password.&#10;Add password reset via email. Implement JWT tokens."
            className="w-full h-48 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y"
          />
          <p className="mt-1 text-sm text-gray-500">
            {text.length} characters
          </p>
        </div>

        {/* Issue Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Issue Type
          </label>
          <div className="grid grid-cols-2 gap-3">
            {[
              { value: 'task', label: 'Tasks/Epics', icon: '📋' },
              { value: 'bug', label: 'Bug Reports', icon: '🐛' },
              { value: 'story', label: 'User Stories', icon: '📖' },
              { value: 'epic-only', label: 'Epic-only', icon: '🎯' }
            ].map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => setIssueType(type.value)}
                className={`px-4 py-3 border-2 rounded-lg text-left transition-colors ${
                  issueType === type.value
                    ? 'border-primary-500 bg-primary-50 text-primary-700'
                    : 'border-gray-200 hover:border-gray-300 text-gray-700'
                }`}
              >
                <div className="flex items-center">
                  <span className="text-2xl mr-2">{type.icon}</span>
                  <span className="text-sm font-medium">{type.label}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Project Key */}
        <div>
          <label htmlFor="project-key" className="block text-sm font-medium text-gray-700 mb-2">
            Project Key
          </label>
          <input
            id="project-key"
            type="text"
            value={projectKey}
            onChange={(e) => setProjectKey(e.target.value.toUpperCase())}
            placeholder="PROJ"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>

        {/* Review Agent Option */}
        <div className="flex items-center">
          <input
            id="skip-review"
            type="checkbox"
            checked={skipReview}
            onChange={(e) => setSkipReview(e.target.checked)}
            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
          />
          <label htmlFor="skip-review" className="ml-2 block text-sm text-gray-700">
            Skip review agent (faster, but lower quality)
          </label>
        </div>

        {/* Generate Button */}
        <button
          type="submit"
          disabled={loading || !text.trim()}
          className="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Generating Tickets...
            </>
          ) : (
            <>
              <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Generate Tickets
            </>
          )}
        </button>
      </form>
    </div>
  )
}
