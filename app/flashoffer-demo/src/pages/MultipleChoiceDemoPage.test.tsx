import { fireEvent, render, screen } from "@testing-library/react";
import { MultipleChoiceDemoPage } from "./MultipleChoiceDemoPage";

describe("MultipleChoiceDemoPage", () => {
  it("renders the quiz question and options", () => {
    render(<MultipleChoiceDemoPage />);

    expect(
      screen.getByRole("heading", {
        level: 2,
        name: /test your flashoffer instincts/i
      })
    ).toBeInTheDocument();
    expect(
      screen.getByRole("heading", {
        level: 3,
        name: /which flashoffer-react capability keeps campaign visuals aligned/i
      })
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText(/theme presets and typography utilities/i)
    ).toBeInTheDocument();
  });

  it("updates the feedback copy when the correct answer is selected", () => {
    render(<MultipleChoiceDemoPage />);

    fireEvent.click(
      screen.getByLabelText(/theme presets and typography utilities/i)
    );

    expect(
      screen.getByRole("heading", {
        level: 4,
        name: /correct — consistent theming drives alignment/i
      })
    ).toBeInTheDocument();
  });
});
