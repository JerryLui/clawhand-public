import { definePluginEntry } from "openclaw";

export default definePluginEntry({
  id: "clawhand-agent-tools",
  name: "Clawhand Agent Tools",
  register(api) {
    // Skills are loaded from ./skills/ via openclaw.plugin.json
    // No runtime tools needed — all interaction is via REST API calls in SKILL.md
  },
});
