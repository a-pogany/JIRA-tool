import { useState } from 'react'

export default function MarkdownEditor({ value, onChange }) {
  const [editValue, setEditValue] = useState(value)

  const handleChange = (e) => {
    setEditValue(e.target.value)
  }

  const handleSave = () => {
    onChange(editValue)
  }

  const handleReset = () => {
    setEditValue(value)
  }

  const hasChanges = editValue !== value

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">
          Edit Markdown
        </label>
        <div className="flex items-center space-x-2">
          {hasChanges && (
            <>
              <button
                onClick={handleReset}
                className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
              >
                Reset
              </button>
              <button
                onClick={handleSave}
                className="px-3 py-1 text-sm text-white bg-primary-600 rounded hover:bg-primary-700"
              >
                Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      <textarea
        value={editValue}
        onChange={handleChange}
        className="w-full h-96 px-3 py-2 font-mono text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-y"
        spellCheck="false"
      />

      <div className="text-xs text-gray-500">
        {editValue.split('\n').length} lines · {editValue.length} characters
        {hasChanges && <span className="ml-2 text-amber-600">• Unsaved changes</span>}
      </div>
    </div>
  )
}
