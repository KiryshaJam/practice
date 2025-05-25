import React, { useState } from 'react';
import { Steps, Form, Input, Select, Slider, Button, Card, Typography, Space } from 'antd';
import { UserOutlined, CarOutlined, SafetyOutlined, DollarOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const { Step } = Steps;
const { Title, Text } = Typography;
const { Option } = Select;

const StyledCard = styled(Card)`
  margin: 24px auto;
  max-width: 800px;
`;

const StyledForm = styled(Form)`
  margin-top: 24px;
`;

const criteria = [
  { name: 'price', label: 'Цена', icon: <DollarOutlined /> },
  { name: 'safety', label: 'Безопасность', icon: <SafetyOutlined /> },
  { name: 'reliability', label: 'Надежность', icon: <CarOutlined /> },
  { name: 'economy', label: 'Экономичность', icon: <DollarOutlined /> },
  { name: 'comfort', label: 'Комфорт', icon: <UserOutlined /> },
  { name: 'capacity', label: 'Вместимость', icon: <CarOutlined /> },
  { name: 'dynamics', label: 'Динамика', icon: <CarOutlined /> },
  { name: 'appearance', label: 'Внешний вид', icon: <CarOutlined /> },
  { name: 'maintenance_cost', label: 'Стоимость обслуживания', icon: <DollarOutlined /> },
  { name: 'additional_options', label: 'Дополнительные опции', icon: <CarOutlined /> },
];

const CarSelection = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();

  const onFinish = (values: any) => {
    console.log('Form values:', values);
    // TODO: Отправить данные на сервер для расчета рекомендаций
  };

  const renderProfileForm = () => (
    <StyledForm form={form} layout="vertical">
      <Form.Item
        name="usage_goals"
        label="Цели использования"
        rules={[{ required: true, message: 'Пожалуйста, выберите цели использования' }]}
      >
        <Select mode="multiple" placeholder="Выберите цели использования">
          <Option value="city">Городские поездки</Option>
          <Option value="family">Семейные путешествия</Option>
          <Option value="business">Деловые поездки</Option>
          <Option value="offroad">Внедорожные поездки</Option>
        </Select>
      </Form.Item>

      <Form.Item
        name="budget"
        label="Бюджет"
        rules={[{ required: true, message: 'Пожалуйста, укажите бюджет' }]}
      >
        <Input type="number" prefix="₽" placeholder="Максимальная стоимость" />
      </Form.Item>

      <Form.Item
        name="body_type"
        label="Тип кузова"
        rules={[{ required: true, message: 'Пожалуйста, выберите тип кузова' }]}
      >
        <Select placeholder="Выберите тип кузова">
          <Option value="sedan">Седан</Option>
          <Option value="hatchback">Хэтчбек</Option>
          <Option value="wagon">Универсал</Option>
          <Option value="suv">Кроссовер</Option>
          <Option value="offroad">Внедорожник</Option>
        </Select>
      </Form.Item>

      <Form.Item
        name="fuel_type"
        label="Тип топлива"
        rules={[{ required: true, message: 'Пожалуйста, выберите тип топлива' }]}
      >
        <Select placeholder="Выберите тип топлива">
          <Option value="petrol">Бензин</Option>
          <Option value="diesel">Дизель</Option>
          <Option value="electric">Электромобиль</Option>
          <Option value="hybrid">Гибрид</Option>
        </Select>
      </Form.Item>
    </StyledForm>
  );

  const renderCriteriaForm = () => (
    <StyledForm form={form} layout="vertical">
      {criteria.map((criterion) => (
        <Form.Item
          key={criterion.name}
          name={criterion.name}
          label={
            <Space>
              {criterion.icon}
              {criterion.label}
            </Space>
          }
        >
          <Slider
            min={1}
            max={9}
            marks={{
              1: 'Не важно',
              5: 'Средне',
              9: 'Очень важно',
            }}
          />
        </Form.Item>
      ))}
    </StyledForm>
  );

  const steps = [
    {
      title: 'Профиль',
      content: renderProfileForm(),
    },
    {
      title: 'Критерии выбора',
      content: renderCriteriaForm(),
    },
    {
      title: 'Результаты',
      content: <div>Здесь будут результаты подбора</div>,
    },
  ];

  const next = () => {
    setCurrentStep(currentStep + 1);
  };

  const prev = () => {
    setCurrentStep(currentStep - 1);
  };

  return (
    <StyledCard>
      <Title level={2}>Подбор автомобиля</Title>
      <Text type="secondary">
        Заполните информацию о ваших предпочтениях, и мы подберем автомобиль, который лучше всего подходит вам
      </Text>

      <Steps current={currentStep} style={{ margin: '24px 0' }}>
        {steps.map((item) => (
          <Step key={item.title} title={item.title} />
        ))}
      </Steps>

      <div className="steps-content">{steps[currentStep].content}</div>

      <div className="steps-action" style={{ marginTop: 24 }}>
        {currentStep > 0 && (
          <Button style={{ margin: '0 8px' }} onClick={prev}>
            Назад
          </Button>
        )}
        {currentStep < steps.length - 1 && (
          <Button type="primary" onClick={next}>
            Далее
          </Button>
        )}
        {currentStep === steps.length - 1 && (
          <Button type="primary" onClick={() => onFinish(form.getFieldsValue())}>
            Завершить
          </Button>
        )}
      </div>
    </StyledCard>
  );
};

export default CarSelection; 