import { useState } from 'react'
import MarkdownEditor from './MarkdownEditor'
import ReactMarkdown from 'react-markdown'

export default function ResultsPanel({ result, selectedFile, onUpdate, onUploadToJira }) {
  const [isEditing, setIsEditing] = useState(false)
  const [showReview, setShowReview] = useState(false)

  const displayData = selectedFile || result
  if (!displayData) return null

  const markdown = displayData.markdown || displayData.content
  const filename = displayData.filename || displayData.name

  console.log('[ResultsPanel] displayData:', displayData)
  console.log('[ResultsPanel] filename extracted:', filename)

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 flex items-center">
          <svg className="h-5 w-5 mr-2 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          Generated Tickets
        </h2>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsEditing(!isEditing)}
            className={`px-3 py-1.5 text-sm font-medium rounded-md ${
              isEditing
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {isEditing ? '📖 Preview' : '✏️ Edit'}
          </button>

          <button
            onClick={() => {
              console.log('[ResultsPanel] Upload button clicked, filename:', filename)
              if (!filename) {
                alert('Error: No filename available. Please generate tickets first.')
                return
              }
              onUploadToJira(filename)
            }}
            className="px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={!filename}
          >
            ⬆️ Upload to Jira
          </button>
        </div>
      </div>

      {/* Stats */}
      {result?.stats && (
        <div className="mb-4 grid grid-cols-4 gap-3">
          {result.stats.epics > 0 && (
            <div className="bg-blue-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-blue-600">{result.stats.epics}</div>
              <div className="text-xs text-blue-700">Epics</div>
            </div>
          )}
          {result.stats.tasks > 0 && (
            <div className="bg-purple-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-purple-600">{result.stats.tasks}</div>
              <div className="text-xs text-purple-700">Tasks</div>
            </div>
          )}
          {result.stats.bugs > 0 && (
            <div className="bg-red-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-red-600">{result.stats.bugs}</div>
              <div className="text-xs text-red-700">Bugs</div>
            </div>
          )}
          {result.stats.stories > 0 && (
            <div className="bg-green-50 rounded-lg p-3 text-center">
              <div className="text-2xl font-bold text-green-600">{result.stats.stories}</div>
              <div className="text-xs text-green-700">Stories</div>
            </div>
          )}
        </div>
      )}

      {/* Review Results */}
      {result?.review && (
        <div className="mb-4">
          <button
            onClick={() => setShowReview(!showReview)}
            className="flex items-center text-sm font-medium text-amber-700 hover:text-amber-800"
          >
            <svg className={`h-4 w-4 mr-1 transform ${showReview ? 'rotate-90' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            Agent 2 Review Feedback
          </button>

          {showReview && (
            <div className="mt-3 space-y-3 pl-5">
              {result.review.gaps && result.review.gaps.length > 0 && (
                <div className="bg-amber-50 border-l-4 border-amber-400 p-3">
                  <h4 className="text-sm font-semibold text-amber-800 mb-1">🔍 Gaps Found</h4>
                  <ul className="text-sm text-amber-700 list-disc list-inside space-y-1">
                    {result.review.gaps.map((gap, i) => <li key={i}>{gap}</li>)}
                  </ul>
                </div>
              )}

              {result.review.questions && result.review.questions.length > 0 && (
                <div className="bg-blue-50 border-l-4 border-blue-400 p-3">
                  <h4 className="text-sm font-semibold text-blue-800 mb-1">❓ Questions</h4>
                  <ul className="text-sm text-blue-700 list-disc list-inside space-y-1">
                    {result.review.questions.map((q, i) => <li key={i}>{q}</li>)}
                  </ul>
                </div>
              )}

              {result.review.suggestions && result.review.suggestions.length > 0 && (
                <div className="bg-green-50 border-l-4 border-green-400 p-3">
                  <h4 className="text-sm font-semibold text-green-800 mb-1">✨ Suggestions</h4>
                  <ul className="text-sm text-green-700 list-disc list-inside space-y-1">
                    {result.review.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Markdown Content */}
      <div className="border-t pt-4">
        {isEditing ? (
          <MarkdownEditor
            value={markdown}
            onChange={(value) => onUpdate(filename, value)}
          />
        ) : (
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown>{markdown}</ReactMarkdown>
          </div>
        )}
      </div>

      {/* File Info */}
      <div className="mt-4 pt-4 border-t text-xs text-gray-500">
        <div className="flex items-center justify-between">
          <span>📄 {filename}</span>
          {displayData.size && (
            <span>{(displayData.size / 1024).toFixed(1)} KB</span>
          )}
        </div>
      </div>
    </div>
  )
}
