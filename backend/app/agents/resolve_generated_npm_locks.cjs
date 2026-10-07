// Resolve generated npm lockfiles during isolated packaging, with lifecycle
// scripts disabled. Kept in the backend image so direct Azure deployments
// can run the same resolver in an ACR task without publishing a Git branch.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

function resolveLocks(root, run = spawnSync) {
  root = fs.realpathSync(root);
  const projects = [];
  function visit(dir) {
    const manifest = path.join(dir, 'package.json');
    if (fs.existsSync(manifest)) {
      const pkg = JSON.parse(fs.readFileSync(manifest, 'utf8'));
      const otherManager = (pkg.packageManager && !pkg.packageManager.startsWith('npm@')) ||
        ['yarn.lock', 'pnpm-lock.yaml', 'bun.lock', 'bun.lockb'].some(name => fs.existsSync(path.join(dir, name)));
      if (otherManager) return;
      projects.push(dir);
      if (pkg.workspaces) return;
    }
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isDirectory() && !['node_modules', '.git'].includes(entry.name)) visit(path.join(dir, entry.name));
    }
  }
  visit(root);
  for (const dir of projects) {
    const locks = ['package-lock.json', 'npm-shrinkwrap.json'];
    const backups = new Map();
    for (const name of locks) {
      const file = path.join(dir, name);
      if (fs.existsSync(file)) {
        if (fs.lstatSync(file).isSymbolicLink()) throw new Error('Refusing symlink lockfile');
        backups.set(name, fs.readFileSync(file));
      }
    }
    try {
      for (const name of backups.keys()) fs.unlinkSync(path.join(dir, name));
      console.log(`Resolving generated npm dependencies: ${path.relative(root, dir) || '.'}`);
      const result = run('npm', ['install', '--package-lock-only', '--package-lock=true', '--ignore-scripts', '--include=dev', '--no-audit', '--no-fund'],
        { cwd: dir, stdio: 'inherit', timeout: 180000,
          env: { ...process.env, npm_config_ignore_scripts: 'true', npm_config_legacy_peer_deps: 'false', npm_config_force: 'false' } });
      if (result.error || result.status !== 0) throw new Error(`npm dependency resolution failed: ${result.error?.message || result.status}`);
      const generated = path.join(dir, 'package-lock.json');
      if (!fs.existsSync(generated)) throw new Error('npm did not produce a lockfile');
      if (backups.has('npm-shrinkwrap.json')) fs.renameSync(generated, path.join(dir, 'npm-shrinkwrap.json'));
    } catch (error) {
      for (const name of locks) {
        const file = path.join(dir, name);
        if (fs.existsSync(file)) fs.unlinkSync(file);
        if (backups.has(name)) fs.writeFileSync(file, backups.get(name));
      }
      throw error;
    }
  }
}

module.exports = { resolveLocks };
if (require.main === module) resolveLocks(process.argv[2]);
