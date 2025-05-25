import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import ruRU from 'antd/locale/ru_RU';
import { Layout } from 'antd';
import styled from 'styled-components';

import Header from './components/Header';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import CarSelection from './pages/CarSelection';
import CarComparison from './pages/CarComparison';

const { Content } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const StyledContent = styled(Content)`
  padding: 24px;
  background: #fff;
`;

function App() {
  return (
    <ConfigProvider locale={ruRU}>
      <Router>
        <StyledLayout>
          <Header />
          <StyledContent>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/selection" element={<CarSelection />} />
              <Route path="/comparison" element={<CarComparison />} />
            </Routes>
          </StyledContent>
          <Footer />
        </StyledLayout>
      </Router>
    </ConfigProvider>
  );
}

export default App; 