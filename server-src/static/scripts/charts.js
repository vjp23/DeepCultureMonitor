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

class phModalBox {
    constructor(selector) {
        this.elem = document.querySelector(selector);
        this.dispenseButton = document.querySelector('#dispense-ph-button');
        this.bodyText = document.querySelector('.ph-modal-body p')
        this.setupButtons();
        this.req_names = ["ph"];
        this.actions = ["up"];
        this.values = [0.5];
    }
    
    show() {
        this.elem.classList.toggle('is-active');
        this.onShow()
    }
    
    close() {
        this.elem.classList.toggle('is-active');
        this.onClose();
    }
    
    setupButtons() {
        const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
        const that = this;
        modalClose.forEach((e) => {
          e.addEventListener("click", () => {
              that.elem.classList.toggle('is-active');
              const event = new Event('modal:close');
              that.elem.dispatchEvent(event);
          })
        });
        this.dispenseButton.addEventListener("click", () => {
          this.elem.classList.toggle('is-active');
          const event = new Event('modal:close');
          this.elem.dispatchEvent(event);
          confirmModal.show(this.req_names, this.actions, this.values);
        });
    }
    
    onShow() {
        const event = new Event('modal:show');
        this.elem.dispatchEvent(event);
    }
    
    onClose() {
        const event = new Event('modal:close');
        this.elem.dispatchEvent(event);
    }
    
    addEventListener(event, callback) {
        this.elem.addEventListener(event, callback);
    }
};

class ecModalBox {
    constructor(selector) {
        this.elem = document.querySelector(selector);
        this.dispenseButton = document.querySelector('.modal-card-foot .dispense-ec-button');
        this.bodyText = document.querySelector('.ec-modal-body p')
        this.setupCloseButtons();
    }
    
    show() {
        // this.updateDispenseButton(callId, vmFile, page);
        // this.bodyText.textContent = `Permanently delete this voicemail from ${vmFrom}?`;
        this.elem.classList.toggle('is-active');
        this.onShow()
    }
    
    close() {
        this.elem.classList.toggle('is-active');
        this.onClose();
    }
    
    setupCloseButtons() {
        const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
        const that = this;
        modalClose.forEach((e) => {
            e.addEventListener("click", () => {
                that.elem.classList.toggle('is-active');
                const event = new Event('modal:close');
                that.elem.dispatchEvent(event);
            })
        })
    }

    // updateDispenseButton(callId, vmFile, page) {
    //     this.dispenseButton.href = `/deletevoicemail/${callId}/${vmFile}/${page}`;
    // }
    
    onShow() {
        const event = new Event('modal:show');
        this.elem.dispatchEvent(event);
    }
    
    onClose() {
        const event = new Event('modal:close');
        this.elem.dispatchEvent(event);
    }
    
    addEventListener(event, callback) {
        this.elem.addEventListener(event, callback);
    }
};

class levelModalBox {
    constructor(selector) {
        this.elem = document.querySelector(selector);
        this.dispenseButton = document.querySelector('.modal-card-foot .dispense-level-button');
        this.bodyText = document.querySelector('.level-modal-body p')
        this.setupCloseButtons();
    }
    
    show() {
        // this.updateDispenseButton(callId, vmFile, page);
        // this.bodyText.textContent = `Permanently delete this voicemail from ${vmFrom}?`;
        this.elem.classList.toggle('is-active');
        this.onShow()
    }
    
    close() {
        this.elem.classList.toggle('is-active');
        this.onClose();
    }
    
    setupCloseButtons() {
        const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
        const that = this;
        modalClose.forEach((e) => {
            e.addEventListener("click", () => {
                that.elem.classList.toggle('is-active');
                const event = new Event('modal:close');
                that.elem.dispatchEvent(event);
            })
        })
    }

    // updateDispenseButton(callId, vmFile, page) {
    //     this.dispenseButton.href = `/deletevoicemail/${callId}/${vmFile}/${page}`;
    // }
    
    onShow() {
        const event = new Event('modal:show');
        this.elem.dispatchEvent(event);
    }
    
    onClose() {
        const event = new Event('modal:close');
        this.elem.dispatchEvent(event);
    }
    
    addEventListener(event, callback) {
        this.elem.addEventListener(event, callback);
    }
};

class confirmModalBox {
    constructor(selector, postEndpoint) {
        this.elem = document.querySelector(selector);
        this.confirmButton = document.querySelector('.modal-card-foot .confirm-button');
        this.bodyText = document.querySelector('.modal-card-body p')
        this.postEndpoint = postEndpoint
        this.setupButtons();
    }
    
    show(deviceNames, actions, values) {
      var postData = {};
      deviceNames.forEach((name, i) => postData[name] = {"action": actions[i], "value": values[i]});
      this.postData = postData;
      this.bodyText.textContent = `Are you sure you want to take this action?`;
      this.elem.classList.toggle('is-active');
      this.onShow()
    }

    close() {
        this.elem.classList.toggle('is-active');
        this.onClose();
    }
    
    setupButtons() {
        const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
        this.confirmButton.addEventListener("click", () => {
          this.sendFlagPost();
        });
        const that = this;
        modalClose.forEach((e) => {
            e.addEventListener("click", () => {
                that.elem.classList.toggle('is-active');
                const event = new Event('modal:close');
                that.elem.dispatchEvent(event);
            })
        })
    }

    sendFlagPost() {
        let method = 'POST'
        return fetch(this.postEndpoint, {
            'method': method,
            'headers': {
                "Content-Type": "application/json"
            },
            'body': JSON.stringify(this.postData)
        })
        .then(response => {
            if (response.status === 200) {
              // Just close the modal :)
              this.elem.classList.toggle('is-active');
              const event = new Event('modal:close');
              this.elem.dispatchEvent(event);
            };
        });
    }
    
    onShow() {
        const event = new Event('modal:show');
        this.elem.dispatchEvent(event);
    }
    
    onClose() {
        const event = new Event('modal:close');
        this.elem.dispatchEvent(event);
    }
};

const el_ids = ["ph-chart", "ec-chart", "temp-chart", "level-chart"]
const data = [ph_data, ec_data, temp_data, level_data]
const colors = ["#DE3163", "#9FE2BF", "#FF7F50", "#CCCCFF"]
const titles = ["Nutrient Solution pH", "Nutrient Solution EC (PPM)", "Water Temperature (°F)", "Water Level (gallons)"]
const ymins = [5.5, 250, 65, 5.5]
const ymaxes = [6.5, 1000, 75, 8]

var _ = el_ids.map(function(e, i) {
  createChart(e, data[i], colors[i], titles[i], ymins[i], ymaxes[i], appTimezone);
});

// Setup modals and enable buttons to open them
const phModal = new phModalBox("#phModal");
const ecModal = new ecModalBox("#ecModal");
const levelModal = new ecModalBox("#levelModal");
const confirmModal = new confirmModalBox("#confirmModal", postEndpoint)

document.querySelector("#phBox").addEventListener("click", e => {
    phModal.show();}
);
document.querySelector("#ecBox").addEventListener("click", e => {
    ecModal.show();}
);
document.querySelector("#levelBox").addEventListener("click", e => {
    levelModal.show();}
);