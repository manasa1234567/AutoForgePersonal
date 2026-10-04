import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders Hello World text", () => {
  render(<App />);
  const textElement = screen.getByText(/Hello World/i);
  expect(textElement).toBeInTheDocument();
});
