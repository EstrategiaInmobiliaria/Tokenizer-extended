import { describe, expect, it } from "vitest";
import { CHAPTERS, ERAS, QUIZ, TIMELINE } from "../data/ieGuide";

describe("ieGuide", () => {
  it("covers the 13 chapters of the 2nd edition", () => {
    expect(CHAPTERS).toHaveLength(13);
    expect(CHAPTERS.map((chapter) => chapter.number)).toEqual(
      Array.from({ length: 13 }, (_, index) => index + 1)
    );
  });

  it("places every timeline event in a known era", () => {
    const eraIds = new Set(ERAS.map((era) => era.id));
    for (const event of TIMELINE) {
      expect(eraIds.has(event.era)).toBe(true);
    }
  });

  it("keeps quiz answers inside the option lists", () => {
    for (const item of QUIZ) {
      expect(item.answer).toBeGreaterThanOrEqual(0);
      expect(item.answer).toBeLessThan(item.options.length);
    }
  });
});
