const createChart = (chart_element_id, dataset, border_color, title, y_min, y_max, tz) => {
  new Chart(document.getElementById(chart_element_id), {
    type: 'line',
    data: {
      datasets: [{ 
          data: dataset,
          borderColor: border_color,
          fill: false
        }
      ]
    },
    options: {
      plugins: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: title
        },
        zoom: {
          zoom: {
            wheel: {
              enabled: true,
              speed: 0.025
            },
            pinch: {
              enabled: true
            },
            mode: 'xy',
          },
          pan: {
            enabled: true
          },
          limits: {
            x: {
              min: 'original',
              max: 'original'
            },
            y: {
              min: 'original',
              max: 'original'
            }
          }
        }
      },
      scales: {
        y: {
          suggestedMin: y_min,
          suggestedMax: y_max
        },
        x: {
          adapters: {
            date: {
              zone: tz
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
};

const chartElements = ["ph-chart", "ec-chart", "temp-chart", "level-chart"]
const data = [ph_data, ec_data, temp_data, level_data]
const colors = ["#DE3163", "#9FE2BF", "#FF7F50", "#CCCCFF"]
const titles = ["Nutrient Solution pH", "Nutrient Solution EC (PPM)", "Water Temperature (°F)", "Water Level (gallons)"]
const ymins = [5.5, 250, 65, 5.5]
const ymaxes = [6.5, 1000, 75, 8]

var _ = chartElements.map(function(e, i) {
  createChart(e, data[i], colors[i], titles[i], ymins[i], ymaxes[i], appTimezone);
});
