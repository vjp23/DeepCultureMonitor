Chart.defaults.global.legend.display = false;

new Chart(document.getElementById("ph-chart"), {
  type: 'scatter',
  data: {
    datasets: [{ 
        data: ph_data,
        borderColor: "#DE3163",
        fill: false
      }
    ]
  },
  options: {
    title: {
      display: true,
      text: 'Nutrient Solution pH'
    },
    scales: {
      y: {
        suggestedMin: 5.0,
        suggestedMax: 7.0
      },
      xAxes: [{
        type: 'time',
        time: {
          unit: 'hour',
          timezone: appTimezone,
          displayFormats: {
            hour: 'H:mm'
          },
          tooltipFormat: 'H:mm'
        }
      }]
    },
    elements: {
      line: {
        borderWidth: 1.5
      },
      point: {
        radius: 2,
        hoverRadius: 2.5,
        pointStyle: 'cross'
      }
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("ec-chart"), {
  type: 'scatter',
  data: {
    datasets: [{ 
        data: ec_data,
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
    scales: {
      y: {
        suggestedMin: 50.0,
        suggestedMax: 1500.0
      },
      xAxes: [{
        type: 'time',
        time: {
          unit: 'hour',
          timezone: appTimezone,
          displayFormats: {
            hour: 'H:mm'
          },
          tooltipFormat: 'H:mm'
        }
      }]
    },
    elements: {
      line: {
        borderWidth: 1.5
      },
      point: {
        radius: 2,
        hoverRadius: 2.5,
        pointStyle: 'cross'
      }
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("temp-chart"), {
  type: 'scatter',
  data: {
    // labels: temp_x,
    datasets: [{ 
        data: temp_data,
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
    scales: {
      y: {
        suggestedMin: 60.0,
        suggestedMax: 100.0
      },
      xAxes: [{
        type: 'time',
        time: {
          unit: 'hour',
          timezone: appTimezone,
          displayFormats: {
            hour: 'H:mm'
          },
          tooltipFormat: 'H:mm'
        }
      }]
    },
    elements: {
      line: {
        borderWidth: 1.5
      },
      point: {
        radius: 2,
        hoverRadius: 2.5,
        pointStyle: 'cross'
      }
    },
    maintainAspectRatio: false,
    responsive: true
  }
});

new Chart(document.getElementById("level-chart"), {
  type: 'scatter',
  data: {
    // labels: level_x,
    datasets: [{ 
        data: level_data,
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
    scales: {
      y: {
        suggestedMin: 0.0,
        suggestedMax: 8.0
      },
      xAxes: [{
        type: 'time',
        time: {
          unit: 'hour',
          timezone: appTimezone,
          displayFormats: {
            hour: 'H:mm'
          },
          tooltipFormat: 'H:mm'
        }
      }]
    },
    elements: {
      line: {
        borderWidth: 1.5
      },
      point: {
        radius: 2,
        hoverRadius: 2.5,
        pointStyle: 'cross'
      }
    },
    maintainAspectRatio: false,
    responsive: true
  }
});
