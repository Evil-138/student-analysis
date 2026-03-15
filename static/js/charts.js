/**
 * charts.js — Chart.js 4.x helper functions
 * Outrix Student Analysis Platform
 */

/* ── Color palette ── */
const PALETTE = {
  primary:   'rgba(13,  110, 253, 0.85)',
  success:   'rgba(25,  135,  84, 0.85)',
  warning:   'rgba(255, 193,   7, 0.85)',
  danger:    'rgba(220,  53,  69, 0.85)',
  info:      'rgba( 13, 202, 240, 0.85)',
  orange:    'rgba(255, 126,   0, 0.85)',
  purple:    'rgba(111,  66, 193, 0.85)',
  teal:      'rgba( 32, 201, 151, 0.85)',
};

const GRADE_COLORS = {
  A: 'rgba(25, 135, 84, 0.85)',
  B: 'rgba(13, 110, 253, 0.85)',
  C: 'rgba(255, 193, 7, 0.85)',
  D: 'rgba(253, 126, 20, 0.85)',
  F: 'rgba(220, 53, 69, 0.85)',
};

const DEFAULT_COLORS = [
  PALETTE.primary, PALETTE.success, PALETTE.warning,
  PALETTE.danger,  PALETTE.info,    PALETTE.purple,
  PALETTE.orange,  PALETTE.teal,
];

/**
 * Background color resolution helper
 * If the labels match grade keys (A/B/C/D/F) use grade colours,
 * otherwise fall back to the default palette.
 */
function resolveColors(labels, override) {
  if (override) {
    return Array.isArray(override) ? override : Array(labels.length).fill(override);
  }
  const isGrades = labels.every(l => Object.keys(GRADE_COLORS).includes(l));
  if (isGrades) {
    return labels.map(l => GRADE_COLORS[l] || DEFAULT_COLORS[0]);
  }
  return labels.map((_, i) => DEFAULT_COLORS[i % DEFAULT_COLORS.length]);
}

/**
 * createPieChart — creates a Pie chart.
 * @param {string} canvasId   - ID of the <canvas> element
 * @param {string[]} labels   - Segment labels
 * @param {number[]} data     - Segment values
 * @param {string} title      - Chart title
 * @returns {Chart}
 */
function createPieChart(canvasId, labels, data, title) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'pie',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: resolveColors(labels),
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { position: 'right', labels: { font: { size: 12 } } },
        title: { display: !!title, text: title, font: { size: 14, weight: 'bold' } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.parsed} (${((ctx.parsed / ctx.dataset.data.reduce((a, b) => a + b, 0)) * 100).toFixed(1)}%)`,
          },
        },
      },
    },
  });
}

/**
 * createBarChart — creates a vertical Bar chart.
 * @param {string} canvasId      - ID of the <canvas> element
 * @param {string[]} labels      - X-axis labels
 * @param {number[]} data        - Bar values
 * @param {string} datasetLabel  - Dataset legend label
 * @param {string|string[]} color - Background colour(s)
 * @returns {Chart}
 */
function createBarChart(canvasId, labels, data, datasetLabel, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  const bgColors = resolveColors(labels, color);
  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: datasetLabel || '',
        data,
        backgroundColor: bgColors,
        borderColor: bgColors.map(c => c.replace(/[\d.]+\)$/, '1)')),
        borderWidth: 1,
        borderRadius: 4,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: 'rgba(0,0,0,0.05)' },
          ticks: { font: { size: 11 } },
        },
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
      },
      plugins: {
        legend: { display: !!datasetLabel, labels: { font: { size: 12 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}`,
          },
        },
      },
    },
  });
}

/**
 * createDoughnutChart — creates a Doughnut chart.
 * @param {string} canvasId   - ID of the <canvas> element
 * @param {string[]} labels   - Segment labels
 * @param {number[]} data     - Segment values
 * @param {string} title      - Chart title
 * @returns {Chart}
 */
function createDoughnutChart(canvasId, labels, data, title) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: [PALETTE.success, PALETTE.danger],
        borderWidth: 2,
        borderColor: '#fff',
        hoverOffset: 6,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: '60%',
      plugins: {
        legend: { position: 'bottom', labels: { font: { size: 12 } } },
        title: { display: !!title, text: title, font: { size: 14, weight: 'bold' } },
        tooltip: {
          callbacks: {
            label: (ctx) => {
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
              const pct = total ? ((ctx.parsed / total) * 100).toFixed(1) : 0;
              return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
            },
          },
        },
      },
    },
  });
}

/**
 * createRadarChart — creates a Radar chart.
 * @param {string} canvasId      - ID of the <canvas> element
 * @param {string[]} labels      - Axis labels
 * @param {object[]} datasets    - Chart.js dataset objects
 * @param {string} title         - Chart title
 * @returns {Chart}
 */
function createRadarChart(canvasId, labels, datasets, title) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;
  return new Chart(ctx, {
    type: 'radar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          beginAtZero: true,
          min: 0,
          max: 100,
          ticks: { stepSize: 20, font: { size: 10 } },
          grid: { color: 'rgba(0,0,0,0.08)' },
          pointLabels: { font: { size: 12, weight: 'bold' } },
        },
      },
      plugins: {
        legend: { position: 'top', labels: { font: { size: 12 } } },
        title: { display: !!title, text: title, font: { size: 14, weight: 'bold' } },
      },
    },
  });
}
