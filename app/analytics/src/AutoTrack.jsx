import { useEffect } from 'react'
import { useEngagement } from './EngagementProvider'

function parseMeta(element) {
  const meta = {}
  const label = element.getAttribute('data-track-label')
  if (label) {
    meta.label = label
  }
  const raw = element.getAttribute('data-track-meta')
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      if (parsed && typeof parsed === 'object') {
        Object.assign(meta, parsed)
      }
    } catch (error) {
      meta.meta = raw
      console.warn('Failed to parse data-track-meta', raw, error)
    }
  }
  return meta
}

export default function AutoTrack({ selector = '[data-track-id]' }) {
  const { attachElement, detachElement } = useEngagement()

  useEffect(() => {
    if (typeof document === 'undefined') {
      return () => {}
    }

    const tracked = new Map()

    const connect = (element) => {
      if (!(element instanceof HTMLElement)) {
        return
      }
      const trackId = element.getAttribute('data-track-id')
      if (!trackId || tracked.has(element)) {
        return
      }
      const cleanup = attachElement(trackId, element, parseMeta(element))
      tracked.set(element, cleanup)
    }

    const disconnect = (element) => {
      if (!(element instanceof HTMLElement)) {
        return
      }
      const cleanup = tracked.get(element)
      if (cleanup) {
        cleanup()
        tracked.delete(element)
      } else {
        detachElement(element)
      }
    }

    document.querySelectorAll(selector).forEach(connect)

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            if (node.matches(selector)) {
              connect(node)
            }
            node.querySelectorAll?.(selector).forEach(connect)
          }
        })
        mutation.removedNodes.forEach((node) => {
          if (node instanceof HTMLElement) {
            if (node.matches(selector)) {
              disconnect(node)
            }
            node.querySelectorAll?.(selector).forEach(disconnect)
          }
        })
        if (
          mutation.type === 'attributes' &&
          mutation.target instanceof HTMLElement &&
          mutation.target.matches(selector)
        ) {
          disconnect(mutation.target)
          connect(mutation.target)
        }
      })
    })

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['data-track-id', 'data-track-label', 'data-track-meta'],
    })

    return () => {
      observer.disconnect()
      tracked.forEach((cleanup) => cleanup())
      tracked.clear()
    }
  }, [attachElement, detachElement, selector])

  return null
}
