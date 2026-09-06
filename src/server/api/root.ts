import { createTRPCRouter } from "~/server/api/trpc";
import { leadScoringRouter } from "~/server/api/routers/lead-scoring";

/**
 * This is the primary router for your server.
 *
 * All routers added in /api/routers should be manually added here.
 */
export const appRouter = createTRPCRouter({
  leadScoring: leadScoringRouter,
});

// export type definition of API
export type AppRouter = typeof appRouter;
