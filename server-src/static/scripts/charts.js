new Chart(document.getElementById("ph-chart"), {
  type: 'line',
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
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        suggestedMin: 5.5,
        suggestedMax: 6.5
      },
      x: {
        adapters: {
          date: {
            zone: appTimezone
          }
        },
        type: 'time',
        time: {
          unit: 'hour',
        }
      }
    },
    elements: {
      line: {
        borderWidth: 1
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
  type: 'line',
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
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        suggestedMin: 250.0,
        suggestedMax: 1000.0
      },
      x: {
        type: 'time',
        time: {
          unit: 'hour',
        }
      }
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
  type: 'line',
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
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        suggestedMin: 65.0,
        suggestedMax: 80.0
      },
      x: {
        type: 'time',
        time: {
          unit: 'hour',
        }
      }
    },
    elements: {
      line: {
        borderWidth: 1
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
  type: 'line',
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
    plugins: {
      legend: {
        display: false
      }
    },
    scales: {
      y: {
        suggestedMin: 5.0,
        suggestedMax: 7.0
      },
      x: {
        type: 'time',
        time: {
          unit: 'hour',
        }
      }
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
