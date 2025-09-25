import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import AutoTrack from './AutoTrack'
import { EngagementProvider } from './EngagementProvider'

function bootstrap(root) {
  const endpoint = root.dataset.endpoint
  const site = root.dataset.site
  const flushInterval = Number(root.dataset.flushInterval || 5000)
  const heartbeatInterval = Number(root.dataset.heartbeatInterval || 15000)
  const idleTimeout = Number(root.dataset.idleTimeout || 30000)
  const selector = root.dataset.selector || '[data-track-id]'

  createRoot(root).render(
    <StrictMode>
      <EngagementProvider
        endpoint={endpoint}
        site={site}
        flushInterval={flushInterval}
        heartbeatInterval={heartbeatInterval}
        idleTimeout={idleTimeout}
      >
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
