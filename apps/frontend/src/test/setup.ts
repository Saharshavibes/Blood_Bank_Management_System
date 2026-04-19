import "@testing-library/jest-dom/vitest";

class MockResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

if (typeof window !== "undefined" && !window.ResizeObserver) {
  window.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;
}
