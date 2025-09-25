import { useEffect, useMemo, useState } from 'react'
import { useEngagement, useRecordInteraction } from './EngagementProvider'
import EventConsole from './EventConsole'

const SECTIONS = [
  {
    id: 'features',
    label: 'Feature grid',
    title: 'Powerful instrumentation primitives',
    copy: [
      'View, interaction, scroll depth, and dwell events stream through a single provider. Mix declarative data attributes with hooks to instrument any component in a few lines of code.',
      'The provider batches events by session, flushes automatically, and merges duplicate views so that downstream analytics remain tidy.',
    ],
  },
  {
    id: 'case-studies',
    label: 'Case studies',
    title: 'Measure how readers explore long-form content',
    copy: [
      'Scroll milestones highlight which sections visitors reach. Combine them with intersection observers to track the exact dwell time on product callouts or testimonials.',
      'Use the event metadata to tie interactions back to the active view targets at the time of engagement.',
    ],
  },
  {
    id: 'pricing',
    label: 'Pricing table',
    title: 'Understand conversion intent',
    copy: [
      'Attach interaction handlers to call-to-action buttons, toggles, or accordions. The provider annotates each interaction with the user’s scroll depth and active view targets.',
      'Pair those signals with funnel analysis to understand how quickly visitors progress from awareness to conversion.',
    ],
  },
]

const STORIES = [
  {
    id: 'northstar',
    label: 'Northstar metrics',
    headline: 'Which sections drive the most trial sign-ups?',
    body: 'When visitors linger on feature walkthroughs before clicking the trial button we know the walkthrough is resonating. Engagement events provide the raw data to quantify that behavior.',
  },
  {
    id: 'activation',
    label: 'Activation',
    headline: 'Did the onboarding revamp reduce churn?',
    body: 'Track scroll depth across the onboarding article and pair it with dwell heartbeats. If readers drop off early you can iterate on the structure before rolling changes out to production.',
  },
  {
    id: 'experiments',
    label: 'Experiments',
    headline: 'Which layout keeps readers engaged the longest?',
    body: 'Run two variants of the same page, each with its own site slug. Engagement metrics reveal whether readers explore supporting content, hover over comparison tables, or trigger more interactions.',
  },
]

function ActiveTargets() {
  const { getActiveTargets } = useEngagement()
  const [targets, setTargets] = useState(() => getActiveTargets())

  useEffect(() => {
    const id = setInterval(() => {
      setTargets(getActiveTargets())
    }, 400)
    return () => clearInterval(id)
  }, [getActiveTargets])

  if (!targets.length) {
    return <p className="demo-subtle">No active view targets yet.</p>
  }

  return (
    <ul className="demo-active-targets">
      {targets.map((target) => (
        <li key={target}>{target}</li>
      ))}
    </ul>
  )
}

export default function DemoPage({ consoleUrl, consolePollMs = 3000 }) {
  const recordInteraction = useRecordInteraction()
  const [showBonus, setShowBonus] = useState(false)
  const bonusMeta = useMemo(() => JSON.stringify({ inserted: showBonus }), [showBonus])

  const handleCtaClick = (variant) => {
    recordInteraction('hero-cta', { variant })
  }

  const handleToggleBonus = () => {
    const next = !showBonus
    setShowBonus(next)
    recordInteraction('dynamic-track', { visible: next })
  }

  const handleScheduleDemo = () => {
    recordInteraction('pricing-contact', { action: 'schedule-demo' })
  }

  const handleCustomEvent = () => {
    recordInteraction('manual-event', { source: 'control-panel' })
  }

  return (
    <div className="demo-layout">
      <header
        className="demo-hero"
        data-track-id="hero"
        data-track-label="Hero section"
      >
        <p className="demo-kicker">Press analytics playground</p>
        <h1>Track engagement without third-party scripts</h1>
        <p className="demo-lede">
          Scroll through the sections, click the calls to action, and watch events
          roll into the live console below. Every data point comes from the
          engagement provider running on this page.
        </p>
        <div className="demo-actions">
          <button
            data-track-id="hero-cta"
            onClick={() => handleCtaClick('start-trial')}
          >
            Start free trial
          </button>
          <button onClick={() => handleCtaClick('watch-demo')}>
            Watch product tour
          </button>
        </div>
      </header>

      <div className="demo-main">
        <main className="demo-content">
          {SECTIONS.map((section) => (
            <section
              key={section.id}
              className="demo-section"
              data-track-id={section.id}
              data-track-label={section.label}
              data-track-meta={JSON.stringify({ section: section.id })}
            >
              <h2>{section.title}</h2>
              {section.copy.map((paragraph) => (
                <p key={paragraph}>{paragraph}</p>
              ))}
            </section>
          ))}

          <section
            className="demo-section"
            data-track-id="stories"
            data-track-label="Customer stories"
          >
            <h2>Questions this data can answer</h2>
            <div className="demo-stories">
              {STORIES.map((story) => (
                <article
                  key={story.id}
                  data-track-id={`story-${story.id}`}
                  data-track-label={story.label}
                  className="demo-story"
                >
                  <h3>{story.headline}</h3>
                  <p>{story.body}</p>
                  <button
                    onClick={() => recordInteraction(`story-${story.id}`, {
                      action: 'open-story',
                    })}
                  >
                    Open report
                  </button>
                </article>
              ))}
            </div>
          </section>

          {showBonus && (
            <section
              className="demo-section demo-section--accent"
              data-track-id="dynamic-insight"
              data-track-label="Dynamic content"
              data-track-meta={bonusMeta}
            >
              <h2>Dynamic content joined the DOM</h2>
              <p>
                The AutoTrack helper detects nodes added after load. Scroll this
                panel into view to emit another set of view events and confirm the
                mutation observer wiring.
              </p>
            </section>
          )}
        </main>

        <aside className="demo-sidebar">
          <section>
            <h2>Active view targets</h2>
            <ActiveTargets />
          </section>

          <section>
            <h2>Manual interactions</h2>
            <p className="demo-subtle">
              Use these controls to emit custom interaction events. They help
              validate that metadata flows alongside the automatic trackers.
            </p>
            <div className="demo-controls">
              <button onClick={handleToggleBonus}>
                {showBonus ? 'Remove dynamic section' : 'Add dynamic section'}
              </button>
              <button onClick={handleScheduleDemo}>Schedule a guided demo</button>
              <button onClick={handleCustomEvent}>Record custom event</button>
            </div>
          </section>
        </aside>
      </div>

      {consoleUrl ? (
        <EventConsole eventsUrl={consoleUrl} pollInterval={consolePollMs} />
      ) : null}
    </div>
  )
}
