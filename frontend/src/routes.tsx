import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Home from './pages/HomePage';
import Register from './pages/Register';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import PurchasePage from './pages/PurchasePage';
import EmailVerification from './components/EmailVerification';
import ProtectedRoute from './components/ProtectedRoute';
import AccountStatement from './components/AccountStatement';
import Profile from './pages/Profile';
import TransactionStatements from './pages/TransactionStatements';
import WalletsPayments from './pages/WalletsPayments';
import DepositFundsPage from './components/payments/DummyDeposit';
import DummyPaymentPage from './components/payments/DummyPayments';
import MailsPage from './pages/Mails';


const AppRoutes: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/verify-email/:token" element={<EmailVerification />} />
           

          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/purchase/:utilityType" 
            element={
              <ProtectedRoute>
                <PurchasePage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/dummy-payment" 
            element={
              <ProtectedRoute>
                <DummyPaymentPage />
              </ProtectedRoute>
            } 
          />
       
          <Route 
            path="/dashboard/profile" 
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard/account-statement" 
            element={
              <ProtectedRoute>
                <AccountStatement />
              </ProtectedRoute>
            } 
          />
          <Route
          path="/dashboard/transactions/wallets"
          element={
            <ProtectedRoute>
              <WalletsPayments/>
            </ProtectedRoute>
          }
          />
          <Route
          path="/dashboard/transactions/tokens"
          element={
            <ProtectedRoute>
              <TransactionStatements/>
            </ProtectedRoute>
          }
          />
          <Route
          path="/dashboard/deposit-funds"
          element={
            <ProtectedRoute>
              <DepositFundsPage/>
            </ProtectedRoute>
          }
          />
          <Route
          path="/dashboard/utility-dashboard"
          element={
            <ProtectedRoute>
              <DepositFundsPage/>
            </ProtectedRoute>
          }
          />
          <Route
          path="/dashboard/messages"
          element={
            <ProtectedRoute>
              <MailsPage/>
            </ProtectedRoute>
          }
          />
        </Routes>
      </Layout>
    </Router>
  );
};

export default AppRoutes;


