import { Routes } from '@angular/router';

export const appRoutes: Routes = [
  {
    path: '',
    loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'new-build',
    data: { openForge: true },
    loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'builds',
    loadComponent: () => import('./features/builds/builds.component').then((m) => m.BuildsComponent),
  },
  {
    path: 'agents',
    data: { workspacePage: 'agents' },
    loadComponent: () => import('./features/workspace/workspace.component').then((m) => m.WorkspaceComponent),
  },
  {
    path: 'skills',
    data: { workspacePage: 'skills' },
    loadComponent: () => import('./features/workspace/workspace.component').then((m) => m.WorkspaceComponent),
  },
  {
    path: 'knowledge',
    data: { workspacePage: 'knowledge' },
    loadComponent: () => import('./features/workspace/workspace.component').then((m) => m.WorkspaceComponent),
  },
  {
    path: 'run-history',
    data: { workspacePage: 'run-history' },
    loadComponent: () => import('./features/workspace/workspace.component').then((m) => m.WorkspaceComponent),
  },
  {
    path: 'settings',
    data: { workspacePage: 'settings' },
    loadComponent: () => import('./features/workspace/workspace.component').then((m) => m.WorkspaceComponent),
  },
  {
    path: 'build/:id',
    loadComponent: () => import('./features/build/build.component').then((m) => m.BuildComponent),
  },
  { path: '**', redirectTo: '' },
];
