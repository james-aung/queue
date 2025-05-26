import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueueList } from './pages/QueueList';
import { QueueStatus } from './components/QueueStatus';
import { ShopkeeperLogin } from './pages/ShopkeeperLogin';
import { ShopkeeperDashboard } from './pages/ShopkeeperDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<QueueList />} />
        <Route path="/status/:entryId" element={<QueueStatus />} />
        <Route path="/shopkeeper/login" element={<ShopkeeperLogin />} />
        <Route path="/shopkeeper/dashboard" element={<ShopkeeperDashboard />} />
      </Routes>
    </Router>
  );
}

export default App
