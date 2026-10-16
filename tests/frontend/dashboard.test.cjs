const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const elements = { sourceChart: { innerHTML: "" }, statusChart: { innerHTML: "" } };
const context = {
  window: {},
  document: {
    // Return the chart container requested by the page script.
    getElementById(id) { return elements[id]; },
    // Ignore browser event bindings during this rendering check.
    addEventListener() {},
  },
  GreenCertApp: {
    // Preserve safe chart labels in the test context.
    escape(value) { return String(value); },
  },
};

const script = fs.readFileSync(path.resolve(__dirname, "../../static/js/pages.js"), "utf8");
vm.runInNewContext(script, context);

// Check labeled bars and the empty state without a browser or RPC.
function testDashboardCharts() {
  const pages = context.window.GreenCertPages;
  pages.dashboard({
    issued: 2, active: 1, retired: 1,
    sourceBreakdown: [
      { source: "Solar", quantityMWh: "25" },
      { source: "Wind", quantityMWh: "0" },
      { source: "Hydro", quantityMWh: "0" },
      { source: "Unknown", quantityMWh: "10" },
    ],
  });
  assert.match(elements.sourceChart.innerHTML, /Solar/);
  assert.match(elements.sourceChart.innerHTML, /25 MWh/);
  assert.match(elements.sourceChart.innerHTML, /Unknown/);
  assert.doesNotMatch(elements.sourceChart.innerHTML, /Wind/);
  assert.match(elements.statusChart.innerHTML, /Active/);
  assert.match(elements.statusChart.innerHTML, /Retired/);

  pages.dashboard({ issued: 0, active: 0, retired: 0, sourceBreakdown: [] });
  assert.match(elements.sourceChart.innerHTML, /No issued certificates yet/);
  assert.match(elements.statusChart.innerHTML, /No issued certificates yet/);
}

testDashboardCharts();
process.stdout.write("Dashboard chart rendering passed.\n");
