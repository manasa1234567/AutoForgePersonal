const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { resolveLocks } = require('./resolve-generated-npm-locks.cjs');

function fixture(t, files) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'lock-resolver-test-'));
  t.after(() => fs.rmSync(dir, { recursive: true, force: true }));
  for (const [name, content] of Object.entries(files)) fs.writeFileSync(path.join(dir, name), content);
  return dir;
}

test('replaces generated hashes using npm; scripts and unsafe flags remain disabled', t => {
  const dir = fixture(t, {'package.json':'{}', 'package-lock.json':'bad hash'});
  resolveLocks(dir, (command, args, options) => {
    assert.equal(command, 'npm');
    assert(args.includes('--ignore-scripts'));
    assert(args.includes('--package-lock-only'));
    assert.equal(options.env.npm_config_legacy_peer_deps, 'false');
    assert.equal(fs.existsSync(path.join(dir,'package-lock.json')), false);
    fs.writeFileSync(path.join(dir,'package-lock.json'), 'resolved');
    return {status:0};
  });
  assert.equal(fs.readFileSync(path.join(dir,'package-lock.json'),'utf8'), 'resolved');
  assert.equal(fs.readFileSync(path.join(dir,'package.json'),'utf8'), '{}');
});
test('failed dependency resolution restores original lock and fails', t => {
  const dir = fixture(t, {'package.json':'{}', 'package-lock.json':'original'});
  assert.throws(() => resolveLocks(dir, () => ({status:1})), /resolution failed/);
  assert.equal(fs.readFileSync(path.join(dir,'package-lock.json'),'utf8'), 'original');
});
test('other package managers are untouched', t => {
  const dir = fixture(t, {'package.json':'{"packageManager":"pnpm@9.0.0"}'});
  resolveLocks(dir, () => {throw new Error('must not call npm');});
});
test('python-only project does not invoke npm', t => {
  const dir = fixture(t, {'requirements.txt':'fastapi'});
  resolveLocks(dir, () => {throw new Error('must not call npm');});
});
