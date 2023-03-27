Chart.defaults.global.legend.display = false;

new Chart(document.getElementById("ph-chart"), {
  type: 'line',
  data: {
    labels: ph_x,
    datasets: [{ 
        data: ph_y,
        borderColor: "#DE3163",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: true,
      text: 'Nutrient Solution pH',
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("ec-chart"), {
  type: 'line',
  data: {
    labels: ec_x,
    datasets: [{ 
        data: ec_y,
        borderColor: "#9FE2BF",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: true,
      text: 'Nutrient Solution EC (PPM)'
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("temp-chart"), {
  type: 'line',
  data: {
    labels: temp_x,
    datasets: [{ 
        data: temp_y,
        borderColor: "#FF7F50",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: true,
      text: 'Water Temperature (°F)'
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("level-chart"), {
  type: 'line',
  data: {
    labels: level_x,
    datasets: [{ 
        data: level_y,
        borderColor: "#CCCCFF",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: true,
      text: 'Water Level (gallons)'
    },
    maintainAspectRatio: false,
    responsive: true
  }
});