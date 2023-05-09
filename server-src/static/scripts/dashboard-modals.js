class phModalBox {
	constructor(selector) {
		this.maxPhUp = 10;
		this.maxPhDown = 10;
		this.phIncrement = 0.5;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-ph-button');
		this.bodyText = document.querySelector('.ph-modal-body p');
		this.upControls = new controlButtonGrp('#ph-up-plus', '#ph-up-minus', '#ph-up-text', 0, this.maxPhUp, this.phIncrement, this.updateDispenseButton.bind(this));
		this.downControls = new controlButtonGrp('#ph-down-plus', '#ph-down-minus', '#ph-down-text', 0, this.maxPhDown, this.phIncrement, this.updateDispenseButton.bind(this));
		this.setupEvents();
	}
	
	show() {
		this.upControls.setValue(0);
		this.downControls.setValue(0);
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}

	changeRequested() {
		return this.upControls.value + this.downControls.value > 0;
	}

	updateDispenseButton() {
		if (this.changeRequested()) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		};
	}
	
	setupEvents() {
	  	// Cancel button, background
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			})
		});

	  	// Dispense button
		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		if (this.changeRequested()) {
			if (this.upControls.value > 0) {
				let upRequest = {"ph": {"status": "request"}};
				upRequest["ph"]["action"] = "up";
				upRequest["ph"]["value"] = this.upControls.value;
				requestData.push(upRequest);
				confirmString += `Dispense ${this.upControls.value} mL of pH Up`;
			};
			if (this.downControls.value > 0) {
				let downRequest = {"ph": {"status": "request"}};
				downRequest["ph"]["action"] = "down";
				downRequest["ph"]["value"] = this.downControls.value;
				requestData.push(downRequest);
				if (confirmString.length > 0) {
					confirmString += '<br />'
				}
				confirmString += `Dispense ${this.downControls.value} mL of pH Down`
			}
		};
		return [requestData, confirmString];
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

class ecModalBox {
	constructor(selector) {
		this.maxAmounts = [150, 150, 150, 150];
		this.requestNames = ['nute1', 'nute2', 'nute3', 'nute4'];
		this.displayNames = ['FloraGro', 'FloraMicro', 'FloraBloom', 'CALiMAGic'];
		this.ecIncrement = 5;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-ec-button');
		this.bodyText = document.querySelector('.ec-modal-body p');
		this.oneControls = new controlButtonGrp('#ec-one-plus', '#ec-one-minus', '#ec-one-text', 0, this.maxAmounts[0], this.ecIncrement, this.updateDispenseButton.bind(this));
		this.twoControls = new controlButtonGrp('#ec-two-plus', '#ec-two-minus', '#ec-two-text', 0, this.maxAmounts[1], this.ecIncrement, this.updateDispenseButton.bind(this));
		this.threeControls = new controlButtonGrp('#ec-three-plus', '#ec-three-minus', '#ec-three-text', 0, this.maxAmounts[2], this.ecIncrement, this.updateDispenseButton.bind(this));
		this.fourControls = new controlButtonGrp('#ec-four-plus', '#ec-four-minus', '#ec-four-text', 0, this.maxAmounts[3], this.ecIncrement, this.updateDispenseButton.bind(this));
		this.controls = [this.oneControls, this.twoControls, this.threeControls, this.fourControls];
		this.setupEvents();
	}
	
	show() {
		this.controls.forEach((ctl) => {
			ctl.setValue(0);
		});
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}

	getRequestedAmounts() {
		const ecAmounts = [this.oneControls.value, this.twoControls.value, this.threeControls.value, this.fourControls.value];
		const amountSum = ecAmounts.reduce((partialSum, a) => partialSum + a, 0);
		return [ecAmounts, amountSum];
	}

	setupEvents() {
	  // Cancel button, background
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			})
		});

	  // Dispense button
		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});
	}

	updateDispenseButton() {
		const [ecAmounts, amountSum] = this.getRequestedAmounts();
		if (amountSum > 0) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		}
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		const [ecAmounts, amountSum] = this.getRequestedAmounts();
		if (amountSum > 0) {
		// Do this because the variable `this` is not in scope in the mapped function
			const requestNames = this.requestNames;
			const displayNames = this.displayNames;
			ecAmounts.map(function(amount, i) {
				if (amount > 0) {
					let ecRequest = {"ec": {"status": "request"}};
					ecRequest["ec"]["action"] = requestNames[i];
					ecRequest["ec"]["value"] = amount;
					requestData.push(ecRequest);
					if (confirmString.length > 0) {
						confirmString += '<br />'
					};
					confirmString += `Dispense ${amount} mL of ${displayNames[i]}`;
				}
			});
		};
		return [requestData, confirmString];
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

class levelModalBox {
	constructor(selector) {
		this.maxGallons = 7;
		this.elem = document.querySelector(selector);
		this.dispenseButton = document.querySelector('#dispense-level-button');
		this.bodyText = document.querySelector('.level-modal-body p');
		this.fillButton = document.querySelector("#fill-button")
		this.drainButton = document.querySelector("#drain-button")
		this.controls = new controlButtonGrp('#level-plus', '#level-minus', '#level-text', 0, this.maxGallons, 0.1, this.updateDispenseButton.bind(this), false);
		this.setupEvents();
	}
	
	show() {
		this.controls.setValue(current_level);
		this.elem.classList.toggle('is-active');
		this.onShow()
	}
	
	close() {
		this.elem.classList.toggle('is-active');
		this.onClose();
	}
	
	setupEvents() {
		const modalClose = this.elem.querySelectorAll("[data-bulma-modal='close'], .modal-background");
		modalClose.forEach((e) => {
			e.addEventListener("click", () => {
				this.close();
			});
		});

		this.fillButton.addEventListener("click", () => {
			this.controls.setValue(7);
		});

		this.drainButton.addEventListener("click", () => {
			this.controls.setValue(0);
		});

		this.dispenseButton.addEventListener("click", () => {
			const [requestData, confirmString] = this.makeRequest();
			this.close();
			confirmModal.show(requestData, confirmString);
		});
	}

	updateDispenseButton() {
		if (this.controls.value != current_level) {
			this.dispenseButton.removeAttribute('disabled');
		} else {
			this.dispenseButton.setAttribute('disabled', 'disabled');
		};
	}

	makeRequest() {
		let requestData = [];
		let confirmString = '';

		if (this.controls.value != current_level) {
			if (this.controls.value === 0) {
				confirmString = "Empty the reservoir";
			} else if (this.controls.value === this.maxGallons) {
				confirmString = "Fill the reservoir";
			} else {
				confirmString = `Set the water level to ${this.controls.value} gallons`
			};
			requestData.push({"level": {"status": "request", "action": "set", "value": this.controls.value}})
		};
		return [requestData, confirmString];
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

class confirmModalBox {
	constructor(selector, postEndpoint) {
		this.elem = document.querySelector(selector);
		this.confirmButton = document.querySelector('.modal-card-foot .confirm-button');
		this.bodyText = document.querySelector('#confirm-string');
		this.postEndpoint = postEndpoint;
		this.setupButtons();
	}
	
	show(postData, confirmString) {
		this.postData = postData;
		this.bodyText.innerHTML = confirmString;
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

class controlButtonGrp {
	constructor(plusSelector, minusSelector, textSelector, minVal, maxVal, increment, updateCallback, resetOnMin=true) {
		this.plus = document.querySelector(plusSelector);
		this.minus = document.querySelector(minusSelector);
		this.text = document.querySelector(textSelector);
		this.value = 0;
		this.minVal = minVal;
		this.maxVal = maxVal;
		this.increment = increment;
		this.updateCallback = updateCallback;
		this.validNumberPattern = new RegExp(/^\d*\.?\d+/);
		this.resetOnMin = resetOnMin;
		this.setupEvents();
	}

	validateNumberEntry(newValue) {
		if (this.validNumberPattern.test(newValue)) {
			return parseFloat(newValue);
		} else {
			return 0;
		};
	}

	setupEvents() {
		this.plus.addEventListener("click", () => {
			this.onPlus();
		});

		this.minus.addEventListener("click", () => {
			this.onMinus();
		});

		this.text.addEventListener("blur", () => {
			this.value = this.validateNumberEntry(this.text.value);
			this.updateText();
		});
	}

	reset() {
		this.value = 0;
		this.updateText();
	}

	setValue(newValue) {
		this.value = newValue;
		this.updateText();
	}

	onPlus() {
		this.value = Math.min(this.maxVal, this.value + this.increment);
		this.updateText();
	}

	onMinus() {
		this.value = Math.max(this.minVal, this.value - this.increment);
		this.updateText();
	}

	updateText() {
		if (this.value > this.minVal) {
			this.value = Math.round(100 * Math.min(this.value, this.maxVal)) / 100;
			if (this.value == this.maxVal) {
				this.plus.setAttribute('disabled', 'disabled');
			} else {
				this.plus.removeAttribute('disabled');
			};
			this.minus.removeAttribute('disabled');
			this.text.value = this.value;
		} else {
			this.plus.removeAttribute('disabled');
			this.minus.setAttribute('disabled', 'disabled');
			if (this.resetOnMin) {
				this.text.value = '';
			} else {
				this.text.value = this.value;
			};
		};
		this.updateCallback();
	}
};

// Setup modals and enable buttons to open them
const phModal = new phModalBox("#phModal");
const ecModal = new ecModalBox("#ecModal");
const levelModal = new levelModalBox("#levelModal");
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
