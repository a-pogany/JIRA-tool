export default function Header({ config }) {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex-shrink-0">
              <svg className="h-8 w-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">JIRA Ticket Generator</h1>
              <p className="text-sm text-gray-500">AI-powered ticket extraction and generation</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {config && (
              <div className="flex items-center space-x-2 text-sm">
                <div className={`h-2 w-2 rounded-full ${config.has_llm ? 'bg-green-400' : 'bg-gray-300'}`} />
                <span className="text-gray-600">
                  {config.llm_provider ? `${config.llm_provider}` : 'No LLM'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
