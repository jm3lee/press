import React from 'react'
import ReactDOM from 'react-dom/client'
import ReactDemo from './ReactDemo.jsx'

const mountReactDemo = (element) => {
  const root = ReactDOM.createRoot(element)
  root.render(
    <React.StrictMode>
      <ReactDemo />
    </React.StrictMode>
  )
}

const roots = document.querySelectorAll('.react-demo-root')
if (roots.length > 0) {
  roots.forEach((element) => {
    if (!element.dataset.reactDemoMounted) {
      element.dataset.reactDemoMounted = 'true'
      mountReactDemo(element)
    }
  })
}

export default ReactDemo
