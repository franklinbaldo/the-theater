import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

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
  posts: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/posts' }),
    schema: entrySchema,
  }),
  backstage: defineCollection({
    loader: glob({ pattern: '**/*.md', base: './src/content/backstage' }),
    schema: entrySchema,
  }),
};
