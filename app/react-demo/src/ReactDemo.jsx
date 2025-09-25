import PropTypes from 'prop-types'
import { useMemo } from 'react'

const defaultSections = [
  {
    title: 'Placeholder Component',
    body: `This React component does not render any dynamic data yet.
It gives engineers a stable mounting point to experiment with application
wiring before UI work begins.`
  },
  {
    title: 'Next Steps',
    body: `Replace the placeholder markup with feature-specific content.
The component already ships with a ready-to-use bundling pipeline so teams can
immediately start iterating on behavior.`
  }
]

function ReactDemo({ sections = defaultSections }) {
  const renderedSections = useMemo(() => sections ?? defaultSections, [sections])

  return (
    <div className="react-demo">
      <h2 className="react-demo__heading">React Demo Component</h2>
      <p className="react-demo__lead">
        Use this shell to bootstrap a new Press integration backed by React.
      </p>
      <div className="react-demo__sections">
        {renderedSections.map((section) => (
          <section className="react-demo__section" key={section.title}>
            <h3 className="react-demo__section-title">{section.title}</h3>
            <p className="react-demo__section-body">{section.body}</p>
          </section>
        ))}
      </div>
    </div>
  )
}

ReactDemo.propTypes = {
  sections: PropTypes.arrayOf(
    PropTypes.shape({
      title: PropTypes.string.isRequired,
      body: PropTypes.string.isRequired
    })
  )
}

export default ReactDemo
