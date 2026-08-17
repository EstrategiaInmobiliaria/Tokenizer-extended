import { expect, it } from "vitest";
import {
  decodePair,
  decodeTriple,
  formatDuration,
  operations,
  subsetBits,
} from "./complexity";

it("counts polynomial and exponential operations", () => {
  expect(operations("constant", 100)).toBe(1);
  expect(operations("linear", 10)).toBe(10);
  expect(operations("quadratic", 10)).toBe(100);
  expect(operations("cubic", 10)).toBe(1000);
  expect(operations("exponential", 10)).toBe(1024);
});

it("shows exponential overtaking cubic after small n", () => {
  expect(operations("cubic", 8)).toBeGreaterThan(operations("exponential", 8));
  expect(operations("exponential", 16)).toBeGreaterThan(
    operations("cubic", 16)
  );
});

it("formats huge runtimes in human units", () => {
  expect(formatDuration(0.0000004)).toContain("ns");
  expect(formatDuration(0.002)).toContain("ms");
  expect(formatDuration(90)).toContain("min");
  expect(formatDuration(13.8e9 * 365.25 * 24 * 3600)).toContain("universo");
});

it("decodes nested-loop coordinates and subset bits", () => {
  expect(decodePair(7, 4)).toEqual({ i: 1, j: 3 });
  expect(decodeTriple(13, 3)).toEqual({ i: 1, j: 1, k: 1 });
  expect(subsetBits(0b10110, 5)).toEqual([1, 2, 4]);
});
