import type { Config } from "jest";

const config: Config = {
  preset: "ts-jest",
  testEnvironment: "jsdom",
  setupFilesAfterEnv: ["<rootDir>/setupTests.ts"],
  moduleFileExtensions: ["ts", "tsx", "js", "jsx"],
  moduleNameMapper: {
    "\\.(css|less|scss)$": "<rootDir>/test/__mocks__/styleMock.ts"
  },
  testMatch: ["<rootDir>/src/**/__tests__/**/*.test.(ts|tsx)"]
};

export default config;
