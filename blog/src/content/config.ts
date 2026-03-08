import { defineCollection, z } from 'astro:content';

const entrySchema = z.object({
  title: z.string(),
  author: z.string(),
  type: z.enum([
    'scene', 'reaction', 'think', 'plan', 'hobby',
    'rehearsal', 'log', 'interview', 'post', 'soul',
    'session', 'rule'
  ]),
  date: z.string(),
  session: z.number().optional(),
  tags: z.array(z.string()).default([]),
});

export const collections = {
  posts: defineCollection({ schema: entrySchema }),
  backstage: defineCollection({ schema: entrySchema }),
};
