import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueueList } from './pages/QueueList';
import { QueueStatus } from './components/QueueStatus';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<QueueList />} />
        <Route path="/status/:entryId" element={<QueueStatus />} />
      </Routes>
    </Router>
  );
}

export default App
