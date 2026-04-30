import { render, screen } from '@testing-library/react';
import App from './App';

jest.mock('./pages/ProductList', () => () => <div>ProductList</div>);
jest.mock('./pages/ProductForm', () => () => <div>ProductForm</div>);
jest.mock('./pages/DomainList', () => () => <div>DomainList</div>);
jest.mock('./pages/DomainForm', () => () => <div>DomainForm</div>);
jest.mock('./pages/CriterionList', () => () => <div>CriterionList</div>);
jest.mock('./pages/CriterionForm', () => () => <div>CriterionForm</div>);
jest.mock('./pages/EvaluationSessionList', () => () => <div>EvaluationSessionList</div>);
jest.mock('./pages/EvaluationSessionForm', () => () => <div>EvaluationSessionForm</div>);
jest.mock('./pages/EvaluationInput', () => () => <div>EvaluationInput</div>);
jest.mock('./pages/EvaluationResults', () => () => <div>EvaluationResults</div>);
jest.mock('./pages/Login', () => () => <div>Login</div>);
jest.mock('./pages/Register', () => () => <div>Register</div>);
jest.mock('./pages/ProductDetail', () => () => <div>ProductDetail</div>);
jest.mock('./pages/Profile', () => () => <div>Profile</div>);

test('renders main navigation', () => {
  render(<App />);
  expect(screen.getByText(/продукты/i)).toBeInTheDocument();
});
