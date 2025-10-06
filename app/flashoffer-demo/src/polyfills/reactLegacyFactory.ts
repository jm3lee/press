import * as React from "react";

type LegacyFactory = <T extends React.ElementType>(
  type: T
) => (
  props?: React.ComponentPropsWithoutRef<T>,
  ...children: React.ReactNode[]
) => React.ReactElement | null;

type ReactWithLegacyFactory = typeof React & {
  createFactory?: LegacyFactory;
};

const reactNamespace = React as ReactWithLegacyFactory & {
  default?: ReactWithLegacyFactory;
};

const legacyFactory: LegacyFactory = ((type: React.ElementType) => {
  const factory = (
    props?: Record<string, unknown> | null,
    ...children: React.ReactNode[]
  ) => React.createElement(type, props, ...children);

  (factory as { type?: React.ElementType }).type = type;

  return factory;
}) as LegacyFactory;

const targets = [reactNamespace, reactNamespace.default].filter(
  (candidate): candidate is ReactWithLegacyFactory =>
    Boolean(candidate) && typeof candidate === "object"
);

for (const target of targets) {
  if (typeof target.createFactory !== "function") {
    try {
      Object.defineProperty(target, "createFactory", {
        configurable: true,
        writable: true,
        value: legacyFactory
      });
    } catch {
      // Ignore attempts to define the property on non-extensible namespace objects.
    }
  }
}
