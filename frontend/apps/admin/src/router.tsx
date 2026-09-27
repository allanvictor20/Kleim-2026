import { ComponentPreview } from '@kleim/ui';
import { createBrowserRouter, type RouteObject } from 'react-router';

import { Landing } from './routes/Landing';
import { Layout } from './routes/Layout';
import { NotFound } from './routes/NotFound';

/** Exported separately so tests can mount the same tree in a memory router. */
export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Landing /> },
      // Every component state in one place (UI/UX Style Guide section 5).
      { path: 'preview', element: <ComponentPreview /> },
      { path: '*', element: <NotFound /> },
    ],
  },
];

export const router = createBrowserRouter(routes);
