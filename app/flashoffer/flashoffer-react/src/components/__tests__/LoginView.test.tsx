/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { FlashofferThemeProvider } from "../../theme/FlashofferThemeProvider";
import { LoginView } from "../LoginView";
import type { LoginViewProps } from "../LoginView";

describe("LoginView", () => {
  function renderLoginView(props: Partial<LoginViewProps> = {}) {
    const onSubmit = props.onSubmit ?? jest.fn().mockResolvedValue(undefined);

    return {
      onSubmit,
      ...render(
        <FlashofferThemeProvider applyCssBaseline={false}>
          <LoginView onSubmit={onSubmit} {...props} />
        </FlashofferThemeProvider>,
      ),
    };
  }

  it("submits trimmed credentials and resets the loading state", async () => {
    const { onSubmit } = renderLoginView({
      defaultUsername: " admin ",
    });

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: " collaborator " } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "secret" } });

    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        username: "collaborator",
        password: "secret",
      });
    });

    expect(screen.getByRole("button", { name: /sign in/i })).not.toBeDisabled();
  });

  it("displays any submit errors returned by the handler", async () => {
    const submitError = new Error("Invalid username or password.");
    const onSubmit = jest.fn().mockRejectedValue(submitError);

    renderLoginView({ onSubmit });

    fireEvent.change(screen.getByLabelText(/username/i), { target: { value: "sfs" } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "wrong" } });

    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(submitError.message)).toBeInTheDocument();
  });

  it("renders custom copy and helper text", () => {
    renderLoginView({
      eyebrow: "Private dashboard",
      title: "Authenticate to view campaigns",
      subtitle: "Use the credentials shared in the ops vault.",
      helperText: <>Need access? Email ops@example.com.</>,
      usernameLabel: "Email",
      passwordLabel: "One-time passcode",
      submitLabel: "Authenticate",
      submittingLabel: "Authenticating",
    });

    expect(screen.getByText(/private dashboard/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /authenticate to view campaigns/i })).toBeInTheDocument();
    expect(screen.getByText(/use the credentials shared in the ops vault/i)).toBeInTheDocument();
    expect(screen.getByText(/need access\? email ops@example.com\./i)).toBeInTheDocument();

    const usernameField = screen.getByLabelText(/email/i);
    const passwordField = screen.getByLabelText(/one-time passcode/i);

    expect(usernameField).toBeInTheDocument();
    expect(passwordField).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /authenticate/i }));
  });
});
