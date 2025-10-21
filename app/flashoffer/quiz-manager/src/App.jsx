import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import GeneratorPage from './GeneratorPage'
import {Typography, AppBar, Box, Toolbar, CssBaseline} from '@mui/material'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <CssBaseline/>
      <AppBar>
      <Toolbar>
      <Typography>foobar</Typography>
      </Toolbar>
      </AppBar>
      <Box component="main">
      <GeneratorPage/>
      </Box>
    </>
  )
}

export default App
