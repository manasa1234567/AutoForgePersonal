// Keep the pipeline and direct-Azure packaging paths on the same resolver.
const { resolveLocks } = require('../backend/app/agents/resolve_generated_npm_locks.cjs');
module.exports = { resolveLocks };
if (require.main === module) resolveLocks(process.argv[2]);
