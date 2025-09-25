import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import AutoTrack from './AutoTrack'
import AnalyticsPlayground from './AnalyticsPlayground'
import { EngagementProvider } from './EngagementProvider'
import './styles.css'

function bootstrap(root) {
  const endpoint = root.dataset.endpoint
  const site = root.dataset.site
  const flushInterval = Number(root.dataset.flushInterval || 5000)
  const heartbeatInterval = Number(root.dataset.heartbeatInterval || 15000)
  const idleTimeout = Number(root.dataset.idleTimeout || 30000)
  const selector = root.dataset.selector || '[data-track-id]'
  const consoleUrl = root.dataset.consoleUrl
  const consolePollMs = Number(root.dataset.consolePollMs || 3000)

  createRoot(root).render(
    <StrictMode>
      <EngagementProvider
        endpoint={endpoint}
        site={site}
        flushInterval={flushInterval}
        heartbeatInterval={heartbeatInterval}
        idleTimeout={idleTimeout}
      >
        <AnalyticsPlayground
          consoleUrl={consoleUrl}
          consolePollMs={consolePollMs}
        />
        <AutoTrack selector={selector} />
      </EngagementProvider>
    </StrictMode>
  )
}

function init() {
  const mounts = document.querySelectorAll('[data-engagement-root]')
  mounts.forEach((mount) => {
    bootstrap(mount)
  })
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init)
} else {
  init()
}
