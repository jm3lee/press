/*
 * Copyright (c) Flashoffer Developers
 * Released under the MIT license.
 */

import "@testing-library/jest-dom";
import * as React from "react";
import { act as domAct } from "react-dom/test-utils";

/**
 * Ensure React's `act` helper is always available during tests, even when
 * Jest resolves React from a build that does not attach the helper yet.
 */

type ReactWithAct = typeof React & { act?: typeof domAct };

const reactWithAct = React as ReactWithAct;

if (typeof reactWithAct.act !== "function") {
  reactWithAct.act = domAct;
}
