import {
  createContext,
  createElement,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
} from 'react'

const EngagementContext = createContext(null)

function nowIso() {
  return new Date().toISOString()
}

function fallbackUuid() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `${Date.now().toString(16)}-${Math.random().toString(16).slice(2)}`
}

function clampRatio(value) {
  return Number(Math.max(0, Math.min(1, value)).toFixed(3))
}

function calculateScrollRatio() {
  if (typeof window === 'undefined') {
    return { ratio: 0, pixels: 0 }
  }
  const scrollY = window.scrollY || window.pageYOffset || 0
  const viewport = window.innerHeight || 0
  const doc = document.documentElement
  const fullHeight = doc ? doc.scrollHeight || 0 : 0
  const ratio = fullHeight <= 0 ? 1 : (scrollY + viewport) / fullHeight
  return { ratio: Math.min(1, ratio), pixels: Math.round(scrollY) }
}

export function EngagementProvider({
  endpoint,
  site,
  children,
  flushInterval = 5000,
  heartbeatInterval = 15000,
  idleTimeout = 30000,
  scrollThresholds = [0.25, 0.5, 0.75, 1],
  viewThresholds = [0.25, 0.5, 0.75, 1],
  maxBatch = 25,
}) {
  const queueRef = useRef([])
  const sessionIdRef = useRef(fallbackUuid())
  const trackedElementsRef = useRef(new Map())
  const activeViewsRef = useRef(new Map())
  const activeTargetsRef = useRef(new Set())
  const observerRef = useRef(null)
  const thresholdsRef = useRef(viewThresholds)
  const flushRef = useRef(() => {})
  const maxBatchRef = useRef(maxBatch)
  const scrollStateRef = useRef(calculateScrollRatio())
  const intersectionHandlerRef = useRef(() => {})

  useEffect(() => {
    maxBatchRef.current = maxBatch
  }, [maxBatch])

  const enqueue = useCallback((event) => {
    queueRef.current.push(event)
    if (queueRef.current.length >= maxBatchRef.current) {
      flushRef.current?.('capacity')
    }
  }, [])

  const flush = useCallback(
    async (reason = 'interval', { sync = false } = {}) => {
      if (!endpoint || queueRef.current.length === 0) {
        return
      }
      const events = queueRef.current.splice(0, queueRef.current.length)
      const body = JSON.stringify({
        site,
        session_id: sessionIdRef.current,
        events,
        reason,
      })
      if (sync && typeof navigator !== 'undefined' && navigator.sendBeacon) {
        const ok = navigator.sendBeacon(endpoint, body)
        if (!ok) {
          queueRef.current.unshift(...events)
        }
        return
      }
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
          body,
          keepalive: sync,
        })
        if (!response.ok) {
          throw new Error(`Unexpected status ${response.status}`)
        }
      } catch (error) {
        console.warn('Failed to flush engagement events', error)
        queueRef.current.unshift(...events)
      }
    },
    [endpoint, site]
  )

  useEffect(() => {
    flushRef.current = flush
  }, [flush])

  useEffect(() => {
    thresholdsRef.current = viewThresholds
    if (!observerRef.current) {
      return
    }
    const elements = Array.from(trackedElementsRef.current.keys())
    observerRef.current.disconnect()
    observerRef.current = new IntersectionObserver((entries) => {
      intersectionHandlerRef.current(entries)
    }, { threshold: thresholdsRef.current })
    elements.forEach((element) => observerRef.current.observe(element))
  }, [viewThresholds])

  const detachElement = useCallback((element) => {
    if (!element || !trackedElementsRef.current.has(element)) {
      return
    }
    const info = trackedElementsRef.current.get(element)
    trackedElementsRef.current.delete(element)
    if (observerRef.current) {
      observerRef.current.unobserve(element)
    }
    activeTargetsRef.current.delete(info.trackId)
    activeViewsRef.current.delete(info.trackId)
  }, [])

  const ensureObserver = useCallback(() => {
    if (observerRef.current) {
      return observerRef.current
    }
    if (typeof window === 'undefined' || typeof IntersectionObserver === 'undefined') {
      return null
    }
    observerRef.current = new IntersectionObserver((entries) => {
      intersectionHandlerRef.current(entries)
    }, { threshold: thresholdsRef.current })
    return observerRef.current
  }, [])

  intersectionHandlerRef.current = (entries) => {
    const timestamp = performance.now()
    entries.forEach((entry) => {
      const info = trackedElementsRef.current.get(entry.target)
      if (!info) {
        return
      }
      const { trackId, meta } = info
      if (entry.isIntersecting) {
        activeTargetsRef.current.add(trackId)
        if (!activeViewsRef.current.has(trackId)) {
          activeViewsRef.current.set(trackId, {
            startedAt: timestamp,
            maxRatio: clampRatio(entry.intersectionRatio || 0),
            meta,
          })
          enqueue({
            type: 'view',
            target: trackId,
            meta: { ...meta, ratio: clampRatio(entry.intersectionRatio || 0) },
            at: nowIso(),
          })
        } else {
          const state = activeViewsRef.current.get(trackId)
          state.maxRatio = Math.max(state.maxRatio, clampRatio(entry.intersectionRatio || 0))
        }
      } else {
        activeTargetsRef.current.delete(trackId)
        const state = activeViewsRef.current.get(trackId)
        if (state) {
          activeViewsRef.current.delete(trackId)
          const duration = Math.round(timestamp - state.startedAt)
          enqueue({
            type: 'view-end',
            target: trackId,
            meta: {
              ...state.meta,
              duration_ms: duration,
              ratio: state.maxRatio,
            },
            at: nowIso(),
          })
        }
      }
    })
  }

  const attachElement = useCallback(
    (trackId, element, meta = {}) => {
      if (!trackId || !element) {
        return () => {}
      }
      const observer = ensureObserver()
      if (!observer) {
        return () => {}
      }
      if (trackedElementsRef.current.has(element)) {
        detachElement(element)
      }
      trackedElementsRef.current.set(element, { trackId, meta })
      element.setAttribute('data-track-id', trackId)
      observer.observe(element)
      return () => detachElement(element)
    },
    [detachElement, ensureObserver]
  )

  const register = useCallback(
    (trackId, element, meta = {}) => attachElement(trackId, element, meta),
    [attachElement]
  )

  const recordInteraction = useCallback((target, data = {}) => {
    if (!target) {
      return
    }
    const scroll = scrollStateRef.current
    const meta = {
      ...data,
      scroll: {
        ratio: clampRatio(scroll.ratio || 0),
        pixels: scroll.pixels || 0,
      },
    }
    if (activeTargetsRef.current.size > 0) {
      meta.active = Array.from(activeTargetsRef.current.values())
    }
    enqueue({ type: 'interaction', target, meta, at: nowIso() })
  }, [enqueue])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    let scheduled = false
    const thresholds = Array.from(new Set(scrollThresholds)).sort((a, b) => a - b)
    const crossed = new Set()

    const updateState = () => {
      scheduled = false
      const next = calculateScrollRatio()
      scrollStateRef.current = next
      thresholds.forEach((threshold) => {
        if (!crossed.has(threshold) && next.ratio >= threshold) {
          crossed.add(threshold)
          enqueue({
            type: 'scroll-depth',
            target: 'page',
            meta: { depth: threshold, pixels: next.pixels },
            at: nowIso(),
          })
        }
      })
    }

    const onScroll = () => {
      if (!scheduled) {
        scheduled = true
        requestAnimationFrame(updateState)
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    updateState()
    return () => {
      window.removeEventListener('scroll', onScroll)
    }
  }, [enqueue, scrollThresholds])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    let lastActive = Date.now()

    const markActive = () => {
      lastActive = Date.now()
    }

    const activityEvents = ['mousemove', 'keydown', 'scroll', 'touchstart', 'focus']
    activityEvents.forEach((event) => {
      window.addEventListener(event, markActive, { passive: true })
    })

    const visibilityListener = () => {
      if (document.visibilityState === 'visible') {
        markActive()
      }
    }
    document.addEventListener('visibilitychange', visibilityListener)

    const heartbeat = setInterval(() => {
      if (document.visibilityState !== 'visible') {
        return
      }
      if (Date.now() - lastActive > idleTimeout) {
        return
      }
      enqueue({
        type: 'dwell',
        target: 'page',
        meta: { interval_ms: heartbeatInterval },
        at: nowIso(),
      })
    }, heartbeatInterval)

    return () => {
      clearInterval(heartbeat)
      document.removeEventListener('visibilitychange', visibilityListener)
      activityEvents.forEach((event) => {
        window.removeEventListener(event, markActive)
      })
    }
  }, [enqueue, heartbeatInterval, idleTimeout])

  useEffect(() => {
    if (!flushInterval) {
      return
    }
    const id = setInterval(() => {
      flush('interval')
    }, flushInterval)
    return () => clearInterval(id)
  }, [flush, flushInterval])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') {
        flushRef.current?.('visibility', { sync: true })
      }
    }
    const handleUnload = () => {
      flushRef.current?.('unload', { sync: true })
    }
    document.addEventListener('visibilitychange', handleVisibility)
    window.addEventListener('pagehide', handleUnload)
    window.addEventListener('beforeunload', handleUnload)
    return () => {
      document.removeEventListener('visibilitychange', handleVisibility)
      window.removeEventListener('pagehide', handleUnload)
      window.removeEventListener('beforeunload', handleUnload)
    }
  }, [])

  const value = useMemo(
    () => ({
      register,
      attachElement,
      detachElement,
      recordInteraction,
      getActiveTargets: () => Array.from(activeTargetsRef.current.values()),
    }),
    [attachElement, detachElement, recordInteraction, register]
  )

  return <EngagementContext.Provider value={value}>{children}</EngagementContext.Provider>
}

export function useEngagement() {
  const context = useContext(EngagementContext)
  if (!context) {
    throw new Error('useEngagement must be used within an EngagementProvider')
  }
  return context
}

export function useViewTracker(trackId, meta = {}) {
  const { register } = useEngagement()
  const cleanupRef = useRef(null)
  const metaRef = useRef(meta)

  useEffect(() => {
    metaRef.current = meta
  }, [meta])

  return useCallback(
    (node) => {
      if (cleanupRef.current) {
        cleanupRef.current()
        cleanupRef.current = null
      }
      if (node) {
        cleanupRef.current = register(trackId, node, metaRef.current)
      }
    },
    [register, trackId]
  )
}

export function ViewTracker({ trackId, meta = {}, as: Component = 'div', children, ...props }) {
  const ref = useViewTracker(trackId, meta)
  return createElement(Component, { ref, ...props, 'data-track-id': trackId }, children)
}

export function useRecordInteraction(defaultTarget, defaultMeta = {}) {
  const { recordInteraction } = useEngagement()
  return useCallback(
    (target = defaultTarget, meta = defaultMeta) => {
      recordInteraction(target, meta)
    },
    [defaultMeta, defaultTarget, recordInteraction]
  )
}
