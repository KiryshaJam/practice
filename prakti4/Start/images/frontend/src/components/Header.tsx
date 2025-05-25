import React from 'react';
import { Layout, Menu, Button, Space } from 'antd';
import { Link, useNavigate } from 'react-router-dom';
import { UserOutlined, CarOutlined, LogoutOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const { Header: AntHeader } = Layout;

const StyledHeader = styled(AntHeader)`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
`;

const Logo = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
`;

const Navigation = () => {
  const navigate = useNavigate();
  const isAuthenticated = false; // TODO: Получать из контекста авторизации

  const handleLogout = () => {
    // TODO: Реализовать выход
    navigate('/login');
  };

  return (
    <StyledHeader>
      <Logo>
        <Link to="/">АвтоПодбор</Link>
      </Logo>
      <Space>
        <Menu mode="horizontal" selectedKeys={[]}>
          <Menu.Item key="home" icon={<CarOutlined />}>
            <Link to="/">Главная</Link>
          </Menu.Item>
          <Menu.Item key="selection" icon={<CarOutlined />}>
            <Link to="/selection">Подбор автомобиля</Link>
          </Menu.Item>
          <Menu.Item key="comparison" icon={<CarOutlined />}>
            <Link to="/comparison">Сравнение</Link>
          </Menu.Item>
        </Menu>
        {isAuthenticated ? (
          <Space>
            <Button type="text" icon={<UserOutlined />}>
              <Link to="/profile">Профиль</Link>
            </Button>
            <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout}>
              Выйти
            </Button>
          </Space>
        ) : (
          <Space>
            <Button type="primary">
              <Link to="/login">Войти</Link>
            </Button>
            <Button>
              <Link to="/register">Регистрация</Link>
            </Button>
          </Space>
        )}
      </Space>
    </StyledHeader>
  );
};

export default Navigation; 