1. **Add navigation menu to Base.astro**
   - Edit `blog/src/layouts/Base.astro`.
   - Update the `<nav>` section to have links for "The Theater" (Home), "Scenes", "Press", "Backstage".
   - Links: `/the-theater`, `/the-theater/scenes`, `/the-theater/press`, `/the-theater/backstage`.

2. **Redesign the homepage (index.astro)**
   - Edit `blog/src/pages/index.astro`.
   - Filter `all` to only include `scene`, `post`, and `interview`.
   - Implement the "Hero" section showing the latest `scene` prominently, with a 200 character excerpt.
   - Implement the "The Story So Far" grid for the rest of the scenes, sorted newest first.
   - Implement the "Press Coverage" section for `post`s.
   - Implement the "Interviews" section for `interview`s.
   - Add a "Backstage" link at the bottom pointing to `/the-theater/backstage/`.
   - Update styles to reflect a theater newspaper/program, large typography, hero section, grid for scenes, social media style cards for posts, and Q&A style for interviews.

3. **Create `scenes` page**
   - Create a new file `blog/src/pages/scenes/index.astro`.
   - Fetch the `backstage` and `posts` collections.
   - Filter for `type === 'scene'`.
   - Display a list/grid of scenes.

4. **Create `press` page**
   - Create a new file `blog/src/pages/press/index.astro`.
   - Fetch the `backstage` and `posts` collections.
   - Filter for `type === 'post' || type === 'interview'`.
   - Display press items in a list/grid.

5. **Pre-commit checks**
   - Follow instructions from `pre_commit_instructions` to ensure code passes required checks.
